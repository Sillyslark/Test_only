"""Deterministic opening and turn engine. Zone index zero is always the top."""
from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
import random
from pathlib import Path
from actions import MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction
from phases import PHASES
from cards import Card, ClimaxDefinition
from deck_loader import build_deck, resolve_deck_path, DEFAULT_TEST_DECK
from rule_resolution import (
    STAGE_SLOTS,
    resolve_stage_overlaps,
    resolve_level_up,
    resolve_refresh,
    is_deck_waiting_defeat,
)
from zones import Zone
from resolution import ResolutionContext, collect_triggers, resolve_pending_effects, InterruptRule
from match_result import MatchResult

VERSION = 7
CLOCK_CAPACITY = 50
PLAYERS = ("P1", "P2")

@dataclass
class PlayerState:
    deck: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    waiting_room: list[Card] = field(default_factory=list)
    clock: list[Card] = field(default_factory=list)
    level: list[Card] = field(default_factory=list)
    stock: list[Card] = field(default_factory=list)
    memory: list[Card] = field(default_factory=list)
    climax: list[Card] = field(default_factory=list)
    resolution_zone: list[Card] = field(default_factory=list)
    stage: dict[str, list[Card]] = field(default_factory=lambda: {slot: [] for slot in STAGE_SLOTS})


@dataclass(frozen=True)
class DamageResult:
    requested: int
    revealed: tuple[str, ...]
    cancelled: bool


@dataclass
class GameState:
    seed: int
    first_player: str
    players: dict[str, PlayerState]
    rng_state: tuple
    mulligans_completed: int = 0
    current_player: str | None = None
    turn_number: int = 0
    phase: str | None = None
    clock_used: bool = False
    result: MatchResult = MatchResult.ONGOING

    @property
    def actor(self):
        if self.mulligans_completed == 2:
            return None
        return self.first_player if self.mulligans_completed == 0 else other(self.first_player)


def other(player):
    return "P2" if player == "P1" else "P1"


def state_hash(state, legacy=False, version=VERSION):
    values = asdict(state)

    # Resolution Zone entered persisted state in V7.
    if legacy or version < 7:
        for player in values["players"].values():
            player.pop("resolution_zone")

    if legacy or version < 5:
        values.pop("result")
    if legacy or version < 4:
        for player in values["players"].values():
            player.pop("stage")
            for zone in player.values():
                for card in zone:
                    card.pop("definition")
                    card.pop("face_up")
    if legacy or version < 3:
        values.pop("clock_used")
        for player in values["players"].values():
            player.pop("clock")
    if legacy:
        for key in ("current_player", "turn_number", "phase"):
            values.pop(key)
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


class Session:
    def __init__(
        self,
        seed: int,
        *,
        p1_deck: str = DEFAULT_TEST_DECK,
        p2_deck: str = DEFAULT_TEST_DECK,
    ):
        if type(seed) is not int:
            raise ValueError("种子必须是整数")

        deck_sources = {
            "P1": str(Path(p1_deck).as_posix()),
            "P2": str(Path(p2_deck).as_posix()),
        }

        # Resolve and validate both deck paths before creating any match state.
        deck_paths = {
            player_id: resolve_deck_path(deck_sources[player_id])
            for player_id in PLAYERS
        }

        rng = random.Random(seed)
        first = rng.choice(PLAYERS)
        players = {}

        for player in PLAYERS:
            cards = build_deck(
                deck_paths[player],
                player,
            )
            rng.shuffle(cards)
            players[player] = PlayerState(deck=cards[5:], hand=cards[:5])

        self.deck_sources = dict(deck_sources)
        self.state = GameState(seed, first, players, rng.getstate())
        self.actions = []
        self.events = [{"kind": "game_started", "seed": seed, "first_player": first}]
        self.hashes = [state_hash(self.state)]

    def _get_zone(self, player_id, zone, slot=None):
        if player_id not in PLAYERS:
            raise ValueError("玩家无效")

        player = self.state.players[player_id]

        if zone == Zone.DECK:
            return player.deck
        if zone == Zone.HAND:
            return player.hand
        if zone == Zone.WAITING_ROOM:
            return player.waiting_room
        if zone == Zone.CLOCK:
            return player.clock
        if zone == Zone.LEVEL:
            return player.level
        if zone == Zone.STOCK:
            return player.stock
        if zone == Zone.MEMORY:
            return player.memory
        if zone == Zone.CLIMAX:
            return player.climax
        if zone == Zone.RESOLUTION:
            return player.resolution_zone

        if zone == Zone.STAGE:
            if slot not in STAGE_SLOTS:
                raise ValueError("舞台位置无效")
            return player.stage[slot]

        raise ValueError("未知区域")


    def _move_card(
        self,
        player_id,
        source,
        destination,
        *,
        card_id=None,
        source_slot=None,
        destination_slot=None,
        destination_index=None,
        face_up=None,
        reason=None,
    ):
        # Internal engine primitive only. Match operations must enter through dispatch().
        if not isinstance(source, Zone) or not isinstance(destination, Zone):
            raise ValueError("区域必须使用 Zone 枚举")

        if face_up is not None and type(face_up) is not bool:
            raise ValueError("face_up 必须是布尔值或 None")

        source_zone = self._get_zone(player_id, source, source_slot)
        destination_zone = self._get_zone(player_id, destination, destination_slot)

        # Validate the source card before mutating anything.
        if card_id is None:
            if not source_zone:
                raise ValueError("来源区域为空")
            source_index = 0
        else:
            source_index = next(
                (
                    i
                    for i, card in enumerate(source_zone)
                    if card.instance_id == card_id
                ),
                None,
            )
            if source_index is None:
                raise ValueError("指定卡牌不在来源区域")

        # Validate destination index before pop(). Python list.insert() silently
        # accepts negative / oversized values, which is undesirable for rules code.
        if destination_index is not None:
            if type(destination_index) is not int:
                raise ValueError("目标位置必须是整数或 None")
            if destination_index < 0 or destination_index > len(destination_zone):
                raise ValueError("目标位置超出区域范围")

        # Same-zone moves need index adjustment after removal when moving an
        # earlier card to a later position.
        adjusted_destination_index = destination_index
        if (
            source_zone is destination_zone
            and adjusted_destination_index is not None
            and source_index < adjusted_destination_index
        ):
            adjusted_destination_index -= 1

        source_name = source_slot if source == Zone.STAGE else source.value
        destination_name = destination_slot if destination == Zone.STAGE else destination.value

        # All validation has completed; mutation begins here.
        card = source_zone.pop(source_index)

        if face_up is not None:
            card = replace(card, face_up=face_up)

        if adjusted_destination_index is None:
            destination_zone.append(card)
        else:
            destination_zone.insert(adjusted_destination_index, card)

        self.events.append({
            "kind": "card_moved",
            "player": player_id,
            "card_id": card.instance_id,
            "source": source_name,
            "destination": destination_name,
            "reason": reason,
        })

        return card

    def _choose_level_card(self, player_id, candidates):
        """Choice hook for Level Up.

        ``candidates`` is the bottom seven Clock cards, kept in storage
        top-first order. The current deterministic default chooses the first
        card counted from the bottom, i.e. the last candidate.

        A future UI choice flow can replace/override this hook.
        """
        if not candidates:
            raise ValueError("没有可供升级选择的牌")
        return candidates[-1].instance_id

    def _resolve_level_up(self, player_id):
        """Resolve exactly one Level Up and emit its timing events."""
        player = self.state.players[player_id]
        if len(player.clock) < 7:
            return None

        # Snapshot the candidates for the start event before any movement.
        candidate_ids = tuple(card.instance_id for card in player.clock[-7:])
        self.events.append({
            "kind": "level_up_started",
            "player": player_id,
            "candidates": list(candidate_ids),
        })

        result = resolve_level_up(
            player,
            player_id,
            self._choose_level_card,
            lambda card_id: self._move_card(
                player_id,
                Zone.CLOCK,
                Zone.LEVEL,
                card_id=card_id,
                destination_index=0,
                reason="level_up",
            ),
            lambda card_id, destination_index: self._move_card(
                player_id,
                Zone.CLOCK,
                Zone.WAITING_ROOM,
                card_id=card_id,
                destination_index=destination_index,
                reason="level_up_discard",
            ),
        )

        self.events.append({
            "kind": "level_up_completed",
            "player": player_id,
            "chosen": result["chosen"],
            "discarded": list(result["discarded"]),
        })
        return result

    def _available_interrupt_rules(self, player_id):
        """Return all currently-valid same-priority interrupt rules."""
        player = self.state.players[player_id]
        rules = []

        if len(player.clock) >= 7:
            rules.append(InterruptRule.LEVEL_UP)

        if not player.deck and player.waiting_room:
            rules.append(InterruptRule.REFRESH)

        return tuple(rules)

    def _choose_interrupt_rule(self, player_id, rules):
        """Choice hook used when multiple same-priority interrupts are valid.

        The current deterministic default chooses Refresh first. A future UI
        should replace/override this hook with an actual player choice.
        """
        if not rules:
            raise ValueError("没有可选择的中断规则")

        if InterruptRule.REFRESH in rules:
            return InterruptRule.REFRESH

        return rules[0]

    def _resolve_interrupt_rule(self, player_id, rule):
        if rule == InterruptRule.LEVEL_UP:
            return self._resolve_level_up(player_id)

        if rule == InterruptRule.REFRESH:
            return self._resolve_refresh_once(player_id)

        raise ValueError("未知中断规则")

    def _resolve_interrupt_rules(self, player_id):
        """Resolve interrupts until the game returns to an interrupt-stable state.

        After every resolved rule, availability is recalculated from the new
        game state. Multiple same-priority rules require a player choice.
        """
        while True:
            rules = self._available_interrupt_rules(player_id)

            if not rules:
                return

            if len(rules) == 1:
                chosen = rules[0]
            else:
                chosen = self._choose_interrupt_rule(player_id, rules)

                if chosen not in rules:
                    raise ValueError("选择的中断规则当前不可处理")

                self.events.append({
                    "kind": "interrupt_rule_chosen",
                    "player": player_id,
                    "options": [rule.value for rule in rules],
                    "chosen": chosen.value,
                })

            self._resolve_interrupt_rule(player_id, chosen)

    def _shuffle_deck(self, player_id):
        """Shuffle Deck using the match RNG timeline and persist its new state."""
        player = self.state.players[player_id]
        rng = random.Random()
        rng.setstate(self.state.rng_state)
        rng.shuffle(player.deck)
        self.state.rng_state = rng.getstate()
        self.events.append({
            "kind": "deck_shuffled",
            "player": player_id,
            "reason": "refresh",
        })

    def _resolve_refresh_once(self, player_id):
        """Resolve exactly one Deck refresh, if required and possible."""
        player = self.state.players[player_id]
        if player.deck or not player.waiting_room:
            return None

        self.events.append({
            "kind": "refresh_started",
            "player": player_id,
            "count": len(player.waiting_room),
        })

        result = resolve_refresh(
            player,
            player_id,
            lambda card_id: self._move_card(
                player_id,
                Zone.WAITING_ROOM,
                Zone.DECK,
                card_id=card_id,
                reason="refresh_rebuild",
            ),
            lambda: self._shuffle_deck(player_id),
            lambda: self._move_card(
                player_id,
                Zone.DECK,
                Zone.CLOCK,
                destination_index=0,
                reason="refresh_point",
            ),
        )

        self.events.append({
            "kind": "refresh_completed",
            "player": player_id,
            "refresh_point": result["refresh_point"],
            "recycled": list(result["recycled"]),
        })

        return result

    def _resolve_refresh_if_needed(self, player_id):
        """Compatibility helper: enter the generalized interrupt loop."""
        self._resolve_interrupt_rules(player_id)

    def _draw_one(self, player_id, *, reason):
        """Move one card from Deck to Hand with interrupt checkpoints around it."""
        player = self.state.players[player_id]

        self._resolve_interrupt_rules(player_id)
        if not player.deck:
            raise ValueError("牌库为空且控制室无牌，无法抽牌")

        card = self._move_card(
            player_id,
            Zone.DECK,
            Zone.HAND,
            reason=reason,
        )

        # The next atomic step may not begin until all interrupts caused by this
        # movement are fully resolved.
        self._resolve_interrupt_rules(player_id)
        return card

    def _deal_damage(self, player_id, amount, *, reason="damage"):
        # Resolve one damage process. Storage convention is top-first.
        if player_id not in PLAYERS:
            raise ValueError("玩家无效")
        if type(amount) is not int or amount < 0:
            raise ValueError("伤害值必须是非负整数")

        if amount == 0:
            return DamageResult(0, (), False)

        state = self.state
        player = state.players[player_id]
        turn_player = state.current_player or state.first_player
        context = ResolutionContext(
            turn_player=turn_player,
            non_turn_player=other(turn_player),
            event_cursor=len(self.events),
        )

        self.events.append({
            "kind": "damage_started",
            "player": player_id,
            "amount": amount,
            "reason": reason,
        })

        damage_card_ids = []
        cancelled = False

        for _ in range(amount):
            self._resolve_interrupt_rules(player_id)

            if not player.deck:
                raise ValueError("伤害处理中牌库与等候室均无法提供下一张牌")

            card = self._move_card(
                player_id,
                Zone.DECK,
                Zone.RESOLUTION,
                destination_index=0,
                reason="damage_reveal",
            )
            damage_card_ids.append(card.instance_id)

            # Deck-empty Refresh may interrupt immediately after this reveal.
            self._resolve_interrupt_rules(player_id)

            # Special defeat during damage processing:
            #
            # After all applicable interrupt rules have been given a chance to resolve,
            # if Deck and Waiting Room are both empty and Resolution Zone contains no
            # Climax, the player loses immediately.
            #
            # The revealed damage cards remain in Resolution Zone. The normal
            # damage-hit step must not continue.
            if (
                not player.deck
                and not player.waiting_room
                and not any(
                    isinstance(
                        resolution_card.definition,
                        ClimaxDefinition,
                    )
                    for resolution_card in player.resolution_zone
                )
            ):
                self._apply_defeat_result((player_id,))

                return DamageResult(
                    requested=amount,
                    revealed=tuple(damage_card_ids),
                    cancelled=False,
                )

            if isinstance(card.definition, ClimaxDefinition):
                cancelled = True
                break

        destination = Zone.WAITING_ROOM if cancelled else Zone.CLOCK
        move_reason = "damage_cancel" if cancelled else "damage_hit"

        # Logical simultaneous batch:
        # reveal order [1,2,3] moved one-by-one to destination index 0 produces
        # top-first [3,2,1,...], so bottom->top is ...1,2,3.
        # No interrupt checkpoint is allowed inside this loop.
        for card_id in damage_card_ids:
            self._move_card(
                player_id,
                Zone.RESOLUTION,
                destination,
                card_id=card_id,
                destination_index=0,
                reason=move_reason,
            )

        # Interrupt only after the whole batch has reached its destination.
        self._resolve_interrupt_rules(player_id)

        result = DamageResult(
            requested=amount,
            revealed=tuple(damage_card_ids),
            cancelled=cancelled,
        )

        completed_event = {
            "kind": "damage_completed",
            "player": player_id,
            "requested": amount,
            "revealed": list(damage_card_ids),
            "cancelled": cancelled,
            "reason": reason,
        }

        self._resolve_resolution_point(
            context,
            timing_events=(completed_event,),
        )

        return result

    def _defeated_players_at_check_timing(self):
        """Snapshot all players satisfying the current defeat condition.

        This is a check-type rule: merely satisfying the condition between
        check timings does not immediately change the match result.
        """
        return tuple(
            player_id
            for player_id in PLAYERS
            if is_deck_waiting_defeat(
                self.state.players[player_id]
            )
        )

    def _apply_defeat_result(self, defeated_players):
        """Apply all defeat results from one check timing simultaneously."""
        defeated = set(defeated_players)

        if not defeated:
            return self.state.result

        if defeated == set(PLAYERS):
            result = MatchResult.BOTH_LOSE
        elif "P1" in defeated:
            result = MatchResult.P2_WIN
        elif "P2" in defeated:
            result = MatchResult.P1_WIN
        else:
            raise ValueError("败北玩家集合无效")

        self.state.result = result
        self.events.append({
            "kind": "match_result_changed",
            "result": result.value,
            "defeated_players": list(defeated_players),
        })
        return result

    def _resolve_check_rules(self, *, stage_player_ids=()):
        """Resolve check-type rules for one resolution point.

        All currently implemented check-rule conditions are snapshotted before
        any check-rule mutation occurs. This preserves same-timing semantics.

        Implemented check rules:
        - Deck and Waiting Room both empty -> defeat
        - Stage overlap
        """
        defeated_players = self._defeated_players_at_check_timing()

        for player_id in stage_player_ids:
            player = self.state.players[player_id]
            resolve_stage_overlaps(
                player,
                player_id,
                lambda source_slot, card_id, destination_index, pid=player_id: self._move_card(
                    pid,
                    Zone.STAGE,
                    Zone.WAITING_ROOM,
                    card_id=card_id,
                    source_slot=source_slot,
                    destination_index=destination_index,
                    reason="stage_overlap",
                ),
            )

        return self._apply_defeat_result(defeated_players)

    def _resolve_resolution_point(
        self,
        context=None,
        *,
        stage_player_ids=(),
        timing_events=(),
    ):
        """Unified entry for one resolution point.

        Order:
        1. Snapshot and resolve check-type rules.
        2. Append action-specific events belonging to this same timing.
        3. Collect triggers from all events created since the context began.
        4. Resolve pending effects.

        Damage and future effects should enter check-type processing through
        this method rather than calling individual check rules directly.
        """
        if context is None:
            turn_player = self.state.current_player or self.state.first_player
            context = ResolutionContext(
                turn_player=turn_player,
                non_turn_player=other(turn_player),
                event_cursor=len(self.events),
            )

        result = self._resolve_check_rules(
            stage_player_ids=stage_player_ids,
        )

        for event in timing_events:
            self.events.append(event)

        # Once the match ends, no triggered effect needs to continue resolving.
        if result != MatchResult.ONGOING:
            return context

        new_events = context.capture_new_events(self.events)
        collect_triggers(new_events, context)
        resolve_pending_effects(context)
        return context

    def dispatch(self, action: MulliganAction | AdvancePhaseAction | ClockAction | PlayCardAction):
        if self.state.result != MatchResult.ONGOING:
            raise ValueError("比赛已经结束")
        if isinstance(action, PlayCardAction):
            return self._play_card(action)
        if isinstance(action, ClockAction):
            return self._clock(action)
        if isinstance(action, AdvancePhaseAction):
            return self._advance_phase(action)
        state = self.state
        if not isinstance(action, MulliganAction):
            raise ValueError("未知操作")
        if state.actor is None or action.player_id != state.actor:
            raise ValueError("当前不轮到该玩家换牌")
        player = state.players[action.player_id]
        ids = action.card_ids
        if len(ids) != len(set(ids)):
            raise ValueError("不能重复选择同一张牌")
        if not set(ids).issubset({c.instance_id for c in player.hand}):
            raise ValueError("只能选择当前手牌")
        if len(ids) > len(player.deck):
            raise ValueError("卡组数量不足")
        # Selection click order never changes zone order. Top is index zero.
        # Capture the selected cards in current Hand order before moving them.
        chosen = set(ids)
        discarded = [c for c in player.hand if c.instance_id in chosen]
        count = len(discarded)

        # Move selected cards in Hand order to the top of Control Room.
        # Increasing destination indexes preserve the original Hand order.
        for destination_index, card in enumerate(discarded):
            self._move_card(
                action.player_id,
                Zone.HAND,
                Zone.WAITING_ROOM,
                card_id=card.instance_id,
                destination_index=destination_index,
                reason="mulligan_discard",
            )

        # Draw replacements from Deck top, appending each to Hand newest/right side.
        drawn = [
            self._move_card(
                action.player_id,
                Zone.DECK,
                Zone.HAND,
                reason="mulligan_draw",
            )
            for _ in range(count)
        ]

        state.mulligans_completed += 1
        canonical = MulliganAction(action.player_id, tuple(c.instance_id for c in discarded))
        self.actions.append(canonical)
        event = {"kind": "mulligan_completed", "player": action.player_id,
                 "discarded": list(canonical.card_ids), "drawn": [c.instance_id for c in drawn]}
        self.events.append(event)
        if state.mulligans_completed == 2:
            state.current_player = state.first_player
            state.turn_number = 1
            state.phase = PHASES[0]
            self.events.append({"kind": "turn_started", "player": state.current_player,
                                "turn": state.turn_number, "phase": state.phase})
        self.hashes.append(state_hash(state))
        return event

    def _play_card(self, action):
        state = self.state
        if state.phase != "main" or state.mulligans_completed != 2:
            raise ValueError("只能在主要阶段使用角色卡")
        if action.player_id != state.current_player:
            raise ValueError("只有当前玩家可以出牌")
        if action.target_slot not in STAGE_SLOTS:
            raise ValueError("舞台位置无效")
        player = state.players[action.player_id]
        card = next((c for c in player.hand if c.instance_id == action.card_id), None)
        if card is None:
            raise ValueError("请选择当前玩家的一张手牌")
        if card.definition.kind != "character":
            raise ValueError("该位置只能放置角色卡")
        if card.definition.level != 0 or card.definition.cost != 0:
            raise ValueError("当前测试版本仅支持 0 级 0 费角色，尚未实现等级检查和费用支付")
        # Begin one timing / resolution point before the card enters Stage.
        context = ResolutionContext(
            turn_player=state.current_player,
            non_turn_player=other(state.current_player),
            event_cursor=len(self.events),
        )

        card = self._move_card(
            action.player_id,
            Zone.HAND,
            Zone.STAGE,
            card_id=action.card_id,
            destination_slot=action.target_slot,
            destination_index=0,
            face_up=True,
            reason="play",
        )

        # "Played" belongs to the same timing as entry / overlap consequences.
        event = {"kind": "card_played", "player": action.player_id,
                 "card_id": card.instance_id, "slot": action.target_slot}

        # One unified resolution point:
        # check-type rules -> timing event -> trigger collection -> pending effects.
        self._resolve_resolution_point(
            context,
            stage_player_ids=(action.player_id,),
            timing_events=(event,),
        )

        self.actions.append(action)
        self.hashes.append(state_hash(state))
        return event

    def _clock(self, action):
        state = self.state
        if state.phase != "clock" or state.mulligans_completed != 2:
            raise ValueError("只能在计时阶段执行计时操作")
        if action.player_id != state.current_player:
            raise ValueError("只有当前玩家可以执行计时操作")
        if state.clock_used:
            raise ValueError("本回合已经执行过计时操作")
        player = state.players[action.player_id]
        card = next((c for c in player.hand if c.instance_id == action.card_id), None)
        if card is None:
            raise ValueError("请选择当前玩家的一张手牌")
        if len(player.clock) >= CLOCK_CAPACITY:
            raise ValueError("计时区已达到 50 张容量上限")
        if len(player.deck) < 2 and not player.waiting_room:
            raise ValueError("可用牌不足，无法完成计时阶段的抽 2")
        clocked = self._move_card(
            action.player_id,
            Zone.HAND,
            Zone.CLOCK,
            card_id=action.card_id,
            destination_index=0,
            reason="clock",
        )

        # Interrupt checkpoint: Level Up must fully resolve before ClockAction
        # continues to draw two replacement cards.
        self._resolve_interrupt_rules(action.player_id)

        drawn = [
            self._draw_one(action.player_id, reason="clock_draw")
            for _ in range(2)
        ]
        state.clock_used = True
        event = {"kind": "card_clocked", "player": action.player_id,
                 "card_id": clocked.instance_id, "drawn": [c.instance_id for c in drawn]}
        self.events.append(event)
        self.actions.append(action)
        self.hashes.append(state_hash(state))
        return event

    def _advance_phase(self, action):
        state = self.state
        if state.mulligans_completed != 2 or state.phase is None:
            raise ValueError("请先完成双方换牌")
        if action.player_id != state.current_player:
            raise ValueError("只有当前回合玩家可以推进阶段")
        index = PHASES.index(state.phase)
        next_phase = PHASES[(index + 1) % len(PHASES)]
        player = state.players[state.current_player]
        if next_phase == "draw" and not player.deck and not player.waiting_room:
            raise ValueError("牌库为空且控制室无牌，无法进入抽卡阶段")
        if next_phase == "stand":
            state.current_player = other(state.current_player)
            state.turn_number += 1
            state.clock_used = False
        state.phase = next_phase
        event = {"kind": "turn_started" if next_phase == "stand" else "phase_changed",
                 "player": state.current_player, "turn": state.turn_number, "phase": next_phase}
        self.events.append(event)
        if next_phase == "draw":
            card = self._draw_one(state.current_player, reason="draw")
            self.events.append({"kind": "card_drawn", "player": state.current_player,
                                "card_id": card.instance_id, "turn": state.turn_number})
        self.actions.append(action)
        self.hashes.append(state_hash(state))
        return event

    def replay_data(self):
        return {
            "version": VERSION,
            "seed": self.state.seed,
            "config": {
                "players": 2,
                "cards_per_player": 50,
                "opening_hand": 5,
                "decks": dict(self.deck_sources),
            },
            "actions": [
                {
                    "kind": {
                        MulliganAction: "mulligan",
                        AdvancePhaseAction: "advance_phase",
                        ClockAction: "clock",
                        PlayCardAction: "play_card",
                    }[type(action)],
                    **asdict(action),
                }
                for action in self.actions
            ],
            "state_hashes": list(self.hashes),
        }

    @classmethod
    def from_replay(cls, data):
        version = data.get("version")
        if version not in (1, 2, 3, 4, 5, 6, VERSION):
            raise ValueError("不支持的 Replay 版本")

        legacy = version == 1
        config = data.get("config")

        base_config = {
            "players": 2,
            "cards_per_player": 50,
            "opening_hand": 5,
        }

        if version >= 6:
            if not isinstance(config, dict):
                raise ValueError("Replay 配置无效")

            decks = config.get("decks")
            if not isinstance(decks, dict) or set(decks) != set(PLAYERS):
                raise ValueError("Replay 卡组配置无效")

            if {
                key: value
                for key, value in config.items()
                if key != "decks"
            } != base_config:
                raise ValueError("Replay 配置不匹配")

            session = cls(
                data["seed"],
                p1_deck=decks["P1"],
                p2_deck=decks["P2"],
            )
        else:
            # V1-V5 predate selectable decks and always used the original
            # default test deck.
            if config != base_config:
                raise ValueError("Replay 配置不匹配")
            session = cls(data["seed"])

        hashes = [
            state_hash(
                session.state,
                legacy=legacy,
                version=version,
            )
        ]
        for action in data["actions"]:
            if legacy or action["kind"] == "mulligan":
                command = MulliganAction(action["player_id"], tuple(action["card_ids"]))
            elif action["kind"] == "advance_phase":
                command = AdvancePhaseAction(action["player_id"])
            elif action["kind"] == "clock" and version >= 3:
                command = ClockAction(action["player_id"], action["card_id"])
            elif action["kind"] == "play_card" and version >= 4:
                command = PlayCardAction(action["player_id"], action["card_id"], action["target_slot"])
            else:
                raise ValueError("未知 Replay 动作")
            session.dispatch(command)
            hashes.append(state_hash(session.state, legacy=legacy, version=version))
        if hashes != data.get("state_hashes"):
            raise ValueError("Replay 状态校验失败，文件或运行环境不兼容")
        return session
