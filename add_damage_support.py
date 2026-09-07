# One-time patch: add Resolution Zone + internal damage resolution.
#
# Run from repository root:
#     python add_damage_support.py
#
# This patch intentionally does NOT add DamageAction or AttackAction yet.

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "engine.py"
ZONES = ROOT / "zones.py"
REPLAY_TEST = ROOT / "tests" / "test_replay_deck_choice.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Cannot find expected block for {label}; aborting.")
    return text.replace(old, new, 1)


def patch_zones():
    text = ZONES.read_text(encoding="utf-8")

    if 'RESOLUTION = "resolution_zone"' not in text:
        old = '''    CLIMAX = "climax"
    STAGE = "stage"
'''
        new = '''    CLIMAX = "climax"
    RESOLUTION = "resolution_zone"
    STAGE = "stage"
'''
        text = replace_once(
            text,
            old,
            new,
            "Zone.RESOLUTION",
        )

    ZONES.write_text(text, encoding="utf-8")


def patch_engine():
    text = ENGINE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "from cards import Card\n",
        "from cards import Card, ClimaxDefinition\n",
        "ClimaxDefinition import",
    )

    text = replace_once(
        text,
        "VERSION = 6\n",
        "VERSION = 7\n",
        "Replay version",
    )

    old = '''    climax: list[Card] = field(default_factory=list)
    stage: dict[str, list[Card]] = field(default_factory=lambda: {slot: [] for slot in STAGE_SLOTS})
'''
    new = '''    climax: list[Card] = field(default_factory=list)
    resolution_zone: list[Card] = field(default_factory=list)
    stage: dict[str, list[Card]] = field(default_factory=lambda: {slot: [] for slot in STAGE_SLOTS})
'''
    text = replace_once(text, old, new, "PlayerState.resolution_zone")

    old = '''@dataclass
class GameState:
'''
    new = '''@dataclass(frozen=True)
class DamageResult:
    requested: int
    revealed: tuple[str, ...]
    cancelled: bool


@dataclass
class GameState:
'''
    text = replace_once(text, old, new, "DamageResult")

    old = '''def state_hash(state, legacy=False, version=VERSION):
    values = asdict(state)
    if legacy or version < 5:
'''
    new = '''def state_hash(state, legacy=False, version=VERSION):
    values = asdict(state)

    # Resolution Zone entered persisted state in V7.
    if version < 7:
        for player in values["players"].values():
            player.pop("resolution_zone")

    if legacy or version < 5:
'''
    text = replace_once(text, old, new, "V7 state hash compatibility")

    old = '''        if zone == Zone.CLIMAX:
            return player.climax

        if zone == Zone.STAGE:
'''
    new = '''        if zone == Zone.CLIMAX:
            return player.climax
        if zone == Zone.RESOLUTION:
            return player.resolution_zone

        if zone == Zone.STAGE:
'''
    text = replace_once(text, old, new, "resolution zone lookup")

    marker = '''    def _defeated_players_at_check_timing(self):
'''
    damage_method = '''    def _deal_damage(self, player_id, amount, *, reason="damage"):
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

'''
    if marker not in text:
        raise RuntimeError("Cannot find defeat timing marker.")
    text = text.replace(marker, damage_method + marker, 1)

    old = '''        if version not in (1, 2, 3, 4, 5, VERSION):
'''
    new = '''        if version not in (1, 2, 3, 4, 5, 6, VERSION):
'''
    text = replace_once(text, old, new, "V6 replay compatibility")

    ENGINE.write_text(text, encoding="utf-8")


def patch_replay_test():
    if not REPLAY_TEST.exists():
        return

    text = REPLAY_TEST.read_text(encoding="utf-8")
    text = text.replace(
        "def test_current_replay_version_is_six(self):",
        "def test_current_replay_version_is_seven(self):",
    )
    text = text.replace(
        "self.assertEqual(6, VERSION)",
        "self.assertEqual(7, VERSION)",
    )
    text = text.replace(
        "def test_v6_replay_records_both_selected_decks",
        "def test_current_replay_records_both_selected_decks",
    )
    text = text.replace(
        "def test_v6_replay_restores_selected_decks",
        "def test_current_replay_restores_selected_decks",
    )
    text = text.replace(
        "def test_v6_missing_deck_file_fails_instead_of_falling_back",
        "def test_current_replay_missing_deck_file_fails_instead_of_falling_back",
    )
    text = text.replace(
        "def test_v6_missing_or_malformed_deck_config_is_rejected",
        "def test_current_replay_missing_or_malformed_deck_config_is_rejected",
    )
    text = text.replace(
        'self.assertEqual(6, data["version"])',
        'self.assertEqual(7, data["version"])',
    )
    REPLAY_TEST.write_text(text, encoding="utf-8")


def main():
    patch_zones()
    patch_engine()
    patch_replay_test()
    print("Damage support patch applied.")
    print("Run:")
    print("  python -B -m unittest tests.test_damage -v")
    print("  python -B -m unittest discover -s tests -v")


if __name__ == "__main__":
    main()
