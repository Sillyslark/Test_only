"""Deterministic opening and turn engine. Zone index zero is always the top."""
from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
import random
from actions import MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction
from phases import PHASES
from cards import Card
from rule_resolution import STAGE_SLOTS, resolve_stage_overlaps

from enum import Enum

VERSION = 4
CLOCK_CAPACITY = 50
PLAYERS = ("P1", "P2")

class Zone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    CONTROL_ROOM = "control_room"
    CLOCK = "clock"
    STAGE = "stage"

@dataclass
class PlayerState:
    deck: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    control_room: list[Card] = field(default_factory=list)
    clock: list[Card] = field(default_factory=list)
    stage: dict[str, list[Card]] = field(default_factory=lambda: {slot: [] for slot in STAGE_SLOTS})


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

    @property
    def actor(self):
        if self.mulligans_completed == 2:
            return None
        return self.first_player if self.mulligans_completed == 0 else other(self.first_player)


def other(player):
    return "P2" if player == "P1" else "P1"


def state_hash(state, legacy=False, version=VERSION):
    values = asdict(state)
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
    def __init__(self, seed: int):
        if type(seed) is not int:
            raise ValueError("种子必须是整数")
        rng = random.Random(seed)
        first = rng.choice(PLAYERS)
        players = {}
        for player in PLAYERS:
            cards = [Card(f"{player}-{n:02}", n) for n in range(1, 51)]
            rng.shuffle(cards)
            players[player] = PlayerState(deck=cards[5:], hand=cards[:5])
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
        if zone == Zone.CONTROL_ROOM:
            return player.control_room
        if zone == Zone.CLOCK:
            return player.clock

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

    def dispatch(self, action: MulliganAction | AdvancePhaseAction | ClockAction | PlayCardAction):
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
        chosen = set(ids)
        discarded = [c for c in player.hand if c.instance_id in chosen]
        kept = [c for c in player.hand if c.instance_id not in chosen]
        count = len(discarded)
        drawn = player.deck[:count]
        player.control_room[0:0] = discarded
        player.deck = player.deck[count:]
        player.hand = kept + drawn
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
        self.events.extend(resolve_stage_overlaps(player, action.player_id))
        # Future ON_PLAY abilities must consume this event only after resolution.
        event = {"kind": "card_played", "player": action.player_id,
                 "card_id": card.instance_id, "slot": action.target_slot}
        self.events.append(event)
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
        if len(player.deck) < 2:
            raise ValueError("卡组不足 2 张，无法执行计时操作；尚未实现卡组刷新")
        clocked = self._move_card(
            action.player_id,
            Zone.HAND,
            Zone.CLOCK,
            card_id=action.card_id,
            destination_index=0,
            reason="clock",
        )

        drawn = [
            self._move_card(
                action.player_id,
                Zone.DECK,
                Zone.HAND,
                reason="clock_draw",
            )
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
        if next_phase == "draw" and not player.deck:
            raise ValueError("卡组为空，无法进入抽卡阶段；当前版本尚未实现卡组刷新")
        if next_phase == "stand":
            state.current_player = other(state.current_player)
            state.turn_number += 1
            state.clock_used = False
        state.phase = next_phase
        event = {"kind": "turn_started" if next_phase == "stand" else "phase_changed",
                 "player": state.current_player, "turn": state.turn_number, "phase": next_phase}
        self.events.append(event)
        if next_phase == "draw":
            card = self._move_card(
                state.current_player,
                Zone.DECK,
                Zone.HAND,
                reason="draw",
            )
            self.events.append({"kind": "card_drawn", "player": state.current_player,
                                "card_id": card.instance_id, "turn": state.turn_number})
        self.actions.append(action)
        self.hashes.append(state_hash(state))
        return event

    def replay_data(self):
        return {"version": VERSION, "seed": self.state.seed,
                "config": {"players": 2, "cards_per_player": 50, "opening_hand": 5},
                "actions": [{"kind": {MulliganAction: "mulligan", AdvancePhaseAction: "advance_phase", ClockAction: "clock", PlayCardAction: "play_card"}[type(a)],
                             **asdict(a)} for a in self.actions], "state_hashes": list(self.hashes)}

    @classmethod
    def from_replay(cls, data):
        if data.get("version") not in (1, 2, 3, VERSION):
            raise ValueError("不支持的 Replay 版本")
        legacy = data["version"] == 1
        session = cls(data["seed"])
        hashes = [state_hash(session.state, legacy=legacy, version=data["version"])]
        if data.get("config") != session.replay_data()["config"]:
            raise ValueError("Replay 配置不匹配")
        for action in data["actions"]:
            if legacy or action["kind"] == "mulligan":
                command = MulliganAction(action["player_id"], tuple(action["card_ids"]))
            elif action["kind"] == "advance_phase":
                command = AdvancePhaseAction(action["player_id"])
            elif action["kind"] == "clock" and data["version"] >= 3:
                command = ClockAction(action["player_id"], action["card_id"])
            elif action["kind"] == "play_card" and data["version"] >= 4:
                command = PlayCardAction(action["player_id"], action["card_id"], action["target_slot"])
            else:
                raise ValueError("未知 Replay 动作")
            session.dispatch(command)
            hashes.append(state_hash(session.state, legacy=legacy, version=data["version"]))
        if hashes != data.get("state_hashes"):
            raise ValueError("Replay 状态校验失败，文件或运行环境不兼容")
        return session
