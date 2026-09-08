import unittest
from unittest.mock import patch

from deck_loader import DEFAULT_TEST_DECK
from engine import Session, state_hash
from zones import Zone

from card_definition import Card
from card_loader import load_card

from match_result import MatchResult

from copy import deepcopy

MIXED_DECK = "TEST/Test_42_T_001_8_T_002.json"

T001 = load_card("TEST/T-001.json")
T002 = load_card("TEST/T-002.json")

def arrange_top_by_kinds(player, kinds):
    remaining = list(player.deck)
    selected = []

    for kind in kinds:
        index = next(
            i
            for i, card in enumerate(remaining)
            if card.definition.kind == kind
        )
        selected.append(remaining.pop(index))

    player.deck[:] = selected + remaining
    return selected

def numbered_card(label, definition, number):
    return Card(
        instance_id=label,
        number=number,
        definition=definition,
    )


def install_damage_refresh_case(
    session,
    *,
    deck_cards,
    waiting_cards,
):
    player = session.state.players["P1"]

    player.deck[:] = list(deck_cards)
    player.waiting_room[:] = list(waiting_cards)

    player.clock.clear()
    player.resolution_zone.clear()
    player.level.clear()

    # 这里故意让 Refresh 洗牌结果保持原顺序，
    # 这样我们才能精确测试卡更与伤害之间的处理顺序，
    # 而不是测试 RNG。
    def deterministic_shuffle(player_id):
        session.events.append({
            "kind": "deck_shuffled",
            "player": player_id,
            "reason": "refresh",
        })

    session._shuffle_deck = deterministic_shuffle

    return player

class DamageTests(unittest.TestCase):
    def test_three_damage_hits_and_keeps_batch_order_on_clock(self):
        session = Session(42)
        player = session.state.players["P1"]

        old_clock = [
            player.deck.pop(),
            player.deck.pop(),
            player.deck.pop(),
        ]
        player.clock[:] = old_clock

        revealed_expected = list(player.deck[:3])
        result = session._deal_damage("P1", 3)

        self.assertFalse(result.cancelled)
        self.assertEqual(
            tuple(card.instance_id for card in revealed_expected),
            result.revealed,
        )

        # Internal top-first expected:
        # [3,2,1] + old Clock [6,5,4].
        self.assertEqual(
            list(reversed(revealed_expected)) + old_clock,
            player.clock,
        )
        self.assertEqual([], player.resolution_zone)

    def test_climax_at_first_second_or_third_reveal_cancels(self):
        for climax_position in (1, 2, 3):
            with self.subTest(climax_position=climax_position):
                session = Session(
                    42 + climax_position,
                    p1_deck=MIXED_DECK,
                    p2_deck=DEFAULT_TEST_DECK,
                )
                player = session.state.players["P1"]

                kinds = ["character"] * 3
                kinds[climax_position - 1] = "climax"
                arranged = arrange_top_by_kinds(player, kinds)

                waiting_before = list(player.waiting_room)
                result = session._deal_damage("P1", 3)

                self.assertTrue(result.cancelled)
                self.assertEqual(climax_position, len(result.revealed))

                revealed = arranged[:climax_position]
                self.assertEqual(
                    list(reversed(revealed)) + waiting_before,
                    player.waiting_room,
                )
                self.assertEqual([], player.resolution_zone)
                self.assertEqual([], player.clock)

    def test_climax_after_requested_damage_does_not_cancel(self):
        session = Session(
            51,
            p1_deck=MIXED_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )
        player = session.state.players["P1"]

        arranged = arrange_top_by_kinds(
            player,
            ["character", "character", "character", "climax"],
        )

        result = session._deal_damage("P1", 3)

        self.assertFalse(result.cancelled)
        self.assertEqual([arranged[3]], player.deck[:1])
        self.assertEqual(
            list(reversed(arranged[:3])),
            player.clock,
        )

    def test_preexisting_resolution_cards_are_not_moved_by_damage(self):
        session = Session(52)
        player = session.state.players["P1"]

        preexisting = [
            player.deck.pop(),
            player.deck.pop(),
        ]
        player.resolution_zone[:] = preexisting

        revealed = list(player.deck[:2])
        session._deal_damage("P1", 2)

        self.assertEqual(preexisting, player.resolution_zone)
        self.assertEqual(
            list(reversed(revealed)),
            player.clock,
        )

    def test_refresh_can_interrupt_between_damage_reveals(self):
        session = Session(53)
        player = session.state.players["P1"]

        while len(player.deck) > 1:
            session._move_card(
                "P1",
                Zone.DECK,
                Zone.WAITING_ROOM,
                card_id=player.deck[-1].instance_id,
                reason="test_setup",
            )

        first_damage_card = player.deck[0]
        result = session._deal_damage("P1", 2)

        self.assertFalse(result.cancelled)
        self.assertEqual(2, len(result.revealed))
        self.assertEqual(first_damage_card.instance_id, result.revealed[0])

        refresh_events = [
            event["kind"]
            for event in session.events
            if event["kind"].startswith("refresh_")
        ]
        self.assertEqual(
            ["refresh_started", "refresh_completed"],
            refresh_events,
        )

        # One Refresh Point + two damage cards.
        self.assertEqual(3, len(player.clock))
        self.assertEqual([], player.resolution_zone)

    def test_damage_batch_finishes_before_level_up_interrupt(self):
        session = Session(54)
        player = session.state.players["P1"]

        for _ in range(5):
            player.clock.append(player.deck.pop())

        with patch.object(
            session,
            "_resolve_level_up",
            wraps=session._resolve_level_up,
        ) as level_up:
            start = len(session.events)
            session._deal_damage("P1", 2)

        level_up.assert_called_once()

        new_events = session.events[start:]
        hit_move_indexes = [
            i
            for i, event in enumerate(new_events)
            if (
                event["kind"] == "card_moved"
                and event.get("reason") == "damage_hit"
            )
        ]
        level_start_index = next(
            i
            for i, event in enumerate(new_events)
            if event["kind"] == "level_up_started"
        )

        self.assertEqual(2, len(hit_move_indexes))
        self.assertLess(max(hit_move_indexes), level_start_index)

    def test_damage_ends_at_unified_resolution_point(self):
        session = Session(55)

        with patch.object(
            session,
            "_resolve_resolution_point",
            wraps=session._resolve_resolution_point,
        ) as resolver:
            session._deal_damage("P1", 1)

        resolver.assert_called_once()

    def test_zero_damage_is_noop(self):
        session = Session(56)
        player = session.state.players["P1"]

        before_deck = list(player.deck)
        before_clock = list(player.clock)
        before_resolution = list(player.resolution_zone)
        before_events = list(session.events)

        result = session._deal_damage("P1", 0)

        self.assertEqual(0, result.requested)
        self.assertEqual((), result.revealed)
        self.assertFalse(result.cancelled)
        self.assertEqual(before_deck, player.deck)
        self.assertEqual(before_clock, player.clock)
        self.assertEqual(before_resolution, player.resolution_zone)
        self.assertEqual(before_events, session.events)

class DamageRefreshOrderingTests(unittest.TestCase):
    def test_case_1_refresh_then_climax_cancels_damage(self):
        """
        Deck top -> bottom:
            D1-T001
            D2-T001

        Waiting:
            W1-T002 ... W8-T002

        Damage 3:
            D1 -> Resolution
            D2 -> Resolution
            Refresh
            W1 -> Clock as Refresh Point
            W2 -> Resolution
            W2 is Climax
            Damage cancelled
        """
        session = Session(101)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)

        waiting = [
            numbered_card(
                f"W{i}-T002",
                T002,
                10 + i,
            )
            for i in range(1, 9)
        ]

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=waiting,
        )

        result = session._deal_damage("P1", 3)

        self.assertTrue(result.cancelled)

        self.assertEqual(
            (
                "D1-T001",
                "D2-T001",
                "W2-T002",
            ),
            result.revealed,
        )

        # Refresh Point W1 已经进入 Clock。
        # 后来的伤害取消不能把它移走。
        self.assertEqual(
            ["W1-T002"],
            [
                card.instance_id
                for card in player.clock
            ],
        )

        self.assertEqual(
            [],
            player.resolution_zone,
        )

        relevant = [
            (event["reason"], event["card_id"])
            for event in session.events
            if (
                event["kind"] == "card_moved"
                and event.get("reason")
                in {
                    "damage_reveal",
                    "refresh_point",
                    "damage_cancel",
                }
            )
        ]

        self.assertEqual(
            [
                ("damage_reveal", "D1-T001"),
                ("damage_reveal", "D2-T001"),

                # 必须先完成 Refresh Point。
                ("refresh_point", "W1-T002"),

                # 然后才继续原来的 Damage。
                ("damage_reveal", "W2-T002"),

                # 最后伤害取消。
                ("damage_cancel", "D1-T001"),
                ("damage_cancel", "D2-T001"),
                ("damage_cancel", "W2-T002"),
            ],
            relevant,
        )

    def test_case_2_refresh_then_remaining_damage_hits(self):
        """
        Deck:
            D1-T001
            D2-T001

        Waiting:
            W1-T001 ... W8-T001

        Damage 3:
            D1
            D2
            Refresh
            W1 -> Clock
            W2 -> Resolution
            Damage hits

        Clock bottom -> top:
            W1, D1, D2, W2
        """
        session = Session(102)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)

        waiting = [
            numbered_card(
                f"W{i}-T001",
                T001,
                10 + i,
            )
            for i in range(1, 9)
        ]

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=waiting,
        )

        result = session._deal_damage("P1", 3)

        self.assertFalse(result.cancelled)

        self.assertEqual(
            (
                "D1-T001",
                "D2-T001",
                "W2-T001",
            ),
            result.revealed,
        )

        # Engine 内部是 index 0 = top。
        #
        # 因此玩家看到的：
        #
        # bottom -> top
        # W1 D1 D2 W2
        #
        # 内部应该是：
        #
        # W2 D2 D1 W1
        self.assertEqual(
            [
                "W2-T001",
                "D2-T001",
                "D1-T001",
                "W1-T001",
            ],
            [
                card.instance_id
                for card in player.clock
            ],
        )

        self.assertEqual(
            [],
            player.resolution_zone,
        )

        relevant = [
            (event["reason"], event["card_id"])
            for event in session.events
            if (
                event["kind"] == "card_moved"
                and event.get("reason")
                in {
                    "damage_reveal",
                    "refresh_point",
                    "damage_hit",
                }
            )
        ]

        self.assertEqual(
            [
                ("damage_reveal", "D1-T001"),
                ("damage_reveal", "D2-T001"),

                # 卡更伤害必须先结算。
                ("refresh_point", "W1-T001"),

                # 然后才继续第三点伤害。
                ("damage_reveal", "W2-T001"),

                # 最后本次3张伤害牌整体进入Clock。
                ("damage_hit", "D1-T001"),
                ("damage_hit", "D2-T001"),
                ("damage_hit", "W2-T001"),
            ],
            relevant,
        )

    def test_case_3_climax_empties_deck_refresh_before_cancel(self):
        """
        Deck top -> bottom:
            D1-T001
            D2-T002

        Waiting:
            W1-T001 ... W8-T001

        Damage 3:
            D1 -> Resolution
            D2 -> Resolution
            D2 is Climax AND Deck becomes empty

        Correct order:
            Refresh first
            W1 -> Clock
            then finish damage cancellation
            D1 + D2 -> Waiting Room
        """
        session = Session(103)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T002", T002, 2)

        waiting = [
            numbered_card(
                f"W{i}-T001",
                T001,
                10 + i,
            )
            for i in range(1, 9)
        ]

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=waiting,
        )

        result = session._deal_damage("P1", 3)

        self.assertTrue(result.cancelled)

        # Climax 是第二张，所以不会再翻第三张。
        self.assertEqual(
            (
                "D1-T001",
                "D2-T002",
            ),
            result.revealed,
        )

        # Refresh Point 已经先进入 Clock。
        self.assertEqual(
            ["W1-T001"],
            [
                card.instance_id
                for card in player.clock
            ],
        )

        self.assertEqual(
            [],
            player.resolution_zone,
        )

        relevant = [
            (event["reason"], event["card_id"])
            for event in session.events
            if (
                event["kind"] == "card_moved"
                and event.get("reason")
                in {
                    "damage_reveal",
                    "refresh_point",
                    "damage_cancel",
                }
            )
        ]

        self.assertEqual(
            [
                ("damage_reveal", "D1-T001"),
                ("damage_reveal", "D2-T002"),

                # 即使刚翻出的 D2 是 Climax，
                # Deck 空导致的 Refresh 仍必须先完整执行。
                ("refresh_point", "W1-T001"),

                # Refresh 完成后才结束伤害取消处理。
                ("damage_cancel", "D1-T001"),
                ("damage_cancel", "D2-T002"),
            ],
            relevant,
        )

class DamageEmptyWaitingSpecialTests(unittest.TestCase):
    def test_case_1_two_t001_empty_waiting_loses_with_cards_still_in_resolution(self):
        """Deck top->bottom: D1(T001), D2(T001); Waiting empty; Damage 2.

        Both cards are revealed into Resolution Zone. When the second reveal
        leaves both Deck and Waiting Room empty, there is no Climax among this
        damage's Resolution cards, so the player loses immediately.

        The damage-hit step must NOT move D1/D2 to Clock first.
        """
        session = Session(201)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=[],
        )

        session._deal_damage("P1", 2)

        self.assertEqual(
            MatchResult.P2_WIN,
            session.state.result,
        )

        # Resolution Zone is top-first.
        self.assertEqual(
            ["D2-T001", "D1-T001"],
            [card.instance_id for card in player.resolution_zone],
        )
        self.assertEqual([], player.clock)
        self.assertEqual([], player.waiting_room)

        relevant = [
            (event["kind"], event.get("reason"), event.get("card_id"))
            for event in session.events
            if (
                event["kind"] in {"card_moved", "match_result_changed"}
                and (
                    event["kind"] == "match_result_changed"
                    or event.get("reason") in {
                        "damage_reveal",
                        "damage_hit",
                    }
                )
            )
        ]

        self.assertEqual(
            [
                ("card_moved", "damage_reveal", "D1-T001"),
                ("card_moved", "damage_reveal", "D2-T001"),
                ("match_result_changed", None, None),
            ],
            relevant,
        )

    def test_case_2_t001_then_t002_empty_waiting_cancels_then_refreshes_and_continues(self):
        """Deck top->bottom: D1(T001), D2(T002); Waiting empty; Damage 2.

        Both cards enter Resolution Zone. Because D2 is a Climax, the special
        empty-Deck/empty-Waiting defeat does not occur during damage.

        Damage cancellation moves D1/D2 to Waiting Room, which then enables
        Refresh. Refresh completes and leaves one card in Deck after its
        Refresh Point, so the game continues.
        """
        session = Session(202)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T002", T002, 2)

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=[],
        )

        result = session._deal_damage("P1", 2)

        self.assertTrue(result.cancelled)
        self.assertEqual(
            ("D1-T001", "D2-T002"),
            result.revealed,
        )
        self.assertEqual(
            MatchResult.ONGOING,
            session.state.result,
        )

        self.assertEqual([], player.resolution_zone)
        self.assertEqual(0, len(player.waiting_room))
        self.assertEqual(1, len(player.clock))
        self.assertEqual(1, len(player.deck))

        relevant_reasons = [
            event.get("reason")
            for event in session.events
            if event["kind"] == "card_moved"
            and event.get("reason") in {
                "damage_reveal",
                "damage_cancel",
                "refresh_rebuild",
                "refresh_point",
            }
        ]

        self.assertEqual(
            [
                "damage_reveal",
                "damage_reveal",
                "damage_cancel",
                "damage_cancel",
                "refresh_rebuild",
                "refresh_rebuild",
                "refresh_point",
            ],
            relevant_reasons,
        )

        self.assertFalse(
            any(
                event["kind"] == "match_result_changed"
                for event in session.events
            )
        )

    def test_case_3_single_t002_cancels_refreshes_then_loses_after_refresh(self):
        """Deck: D1(T002); Waiting empty; Damage 2.

        D1 enters Resolution Zone and cancels the damage. Because a Climax is in
        this damage process, the player does not lose at the empty Deck/Waiting
        state during damage.

        D1 then goes to Waiting Room, Refresh occurs, and D1 becomes the Refresh
        Point. Deck and Waiting Room are empty again. Damage has already ended,
        so the normal defeat check then makes P1 lose.
        """
        session = Session(203)

        d1 = numbered_card("D1-T002", T002, 1)

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1],
            waiting_cards=[],
        )

        result = session._deal_damage("P1", 2)

        self.assertTrue(result.cancelled)
        self.assertEqual(
            ("D1-T002",),
            result.revealed,
        )

        self.assertEqual(
            MatchResult.P2_WIN,
            session.state.result,
        )

        self.assertEqual([], player.resolution_zone)
        self.assertEqual([], player.deck)
        self.assertEqual([], player.waiting_room)
        self.assertEqual(
            ["D1-T002"],
            [card.instance_id for card in player.clock],
        )

        relevant = [
            (
                event["kind"],
                event.get("reason"),
                event.get("card_id"),
            )
            for event in session.events
            if (
                event["kind"]
                in {
                    "card_moved",
                    "refresh_started",
                    "refresh_completed",
                    "match_result_changed",
                }
                and (
                    event["kind"] != "card_moved"
                    or event.get("reason") in {
                        "damage_reveal",
                        "damage_cancel",
                        "refresh_rebuild",
                        "refresh_point",
                    }
                )
            )
        ]

        self.assertEqual(
            [
                ("card_moved", "damage_reveal", "D1-T002"),
                ("card_moved", "damage_cancel", "D1-T002"),
                ("refresh_started", None, None),
                ("card_moved", "refresh_rebuild", "D1-T002"),
                ("card_moved", "refresh_point", "D1-T002"),
                ("refresh_completed", None, None),
                ("match_result_changed", None, None),
            ],
            relevant,
        )

    def test_special_defeat_stops_damage_immediately(self):
        """After the damage-process special defeat, nothing else may resolve."""
        session = Session(204)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=[],
        )

        start = len(session.events)
        result = session._deal_damage("P1", 2)
        events = session.events[start:]

        self.assertEqual(
            MatchResult.P2_WIN,
            session.state.result,
        )
        self.assertFalse(result.cancelled)
        self.assertEqual(
            ("D1-T001", "D2-T001"),
            result.revealed,
        )

        # The two revealed cards must remain in Resolution Zone.
        self.assertEqual(
            ["D2-T001", "D1-T001"],
            [card.instance_id for card in player.resolution_zone],
        )
        self.assertEqual([], player.clock)
        self.assertEqual([], player.waiting_room)

        # Once the special defeat occurs, the current Damage process terminates.
        forbidden_event_kinds = {
            "damage_completed",
            "refresh_started",
            "refresh_completed",
            "level_up_started",
            "level_up_completed",
        }
        self.assertFalse(
            any(
                event["kind"] in forbidden_event_kinds
                for event in events
            )
        )

        # No revealed damage card may continue to the normal hit/cancel movement.
        self.assertFalse(
            any(
                event["kind"] == "card_moved"
                and event.get("reason") in {
                    "damage_hit",
                    "damage_cancel",
                    "refresh_rebuild",
                    "refresh_point",
                    "level_up",
                    "level_up_discard",
                }
                for event in events
            )
        )

        # The match result change is the final event produced by this damage.
        self.assertEqual(
            "match_result_changed",
            events[-1]["kind"],
        )

class DamageResolutionZoneHashTests(unittest.TestCase):
    def test_v7_hash_includes_resolution_zone_but_v6_hash_ignores_it(self):
        """Resolution Zone is persisted from V7 onward.

        Current hashes must distinguish a state whose only difference is
        Resolution Zone content. Historical V6 hashes must ignore that field,
        preserving compatibility with replay files created before the zone
        existed in PlayerState.
        """
        session = Session(205)
        base_state = deepcopy(session.state)
        changed_state = deepcopy(session.state)

        # Change only the new V7 field. Do not move the card out of Deck:
        # this is deliberately a state-shape/hash compatibility test, not a
        # card-conservation scenario.
        marker = changed_state.players["P1"].deck[0]
        changed_state.players["P1"].resolution_zone.append(marker)

        self.assertNotEqual(
            state_hash(base_state),
            state_hash(changed_state),
        )

        self.assertEqual(
            state_hash(base_state, version=6),
            state_hash(changed_state, version=6),
        )

    def test_special_defeat_hash_preserves_cards_left_in_resolution_zone(self):
        """The V7 state hash must retain the special-defeat Resolution contents."""
        session = Session(206)

        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=[],
        )

        session._deal_damage("P1", 2)

        self.assertEqual(
            MatchResult.P2_WIN,
            session.state.result,
        )
        self.assertEqual(
            ["D2-T001", "D1-T001"],
            [card.instance_id for card in player.resolution_zone],
        )

        hash_with_resolution = state_hash(session.state)

        cleared = deepcopy(session.state)
        cleared.players["P1"].resolution_zone.clear()

        # If Resolution Zone were accidentally omitted from the V7 persisted
        # state, these hashes would incorrectly be equal.
        self.assertNotEqual(
            hash_with_resolution,
            state_hash(cleared),
        )

        # Historical V6 hashing deliberately ignores Resolution Zone.
        self.assertEqual(
            state_hash(session.state, version=6),
            state_hash(cleared, version=6),
        )

class DamageNestedInterruptTests(unittest.TestCase):
    def test_refresh_point_level_up_finishes_before_damage_continues(self):
        session = Session(301)

        clock_cards = [
            numbered_card(f"C{i}-T001", T001, 100 + i)
            for i in range(1, 7)
        ]
        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)
        waiting = [
            numbered_card(f"W{i}-T001", T001, 10 + i)
            for i in range(1, 9)
        ]

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=waiting,
        )
        player.clock[:] = list(reversed(clock_cards))

        result = session._deal_damage("P1", 3)

        self.assertFalse(result.cancelled)
        self.assertEqual(3, len(result.revealed))
        self.assertEqual(1, len(player.level))

        relevant = [
            (
                event["kind"],
                event.get("reason"),
                event.get("card_id"),
            )
            for event in session.events
            if (
                event["kind"] in {
                    "card_moved",
                    "refresh_started",
                    "refresh_completed",
                    "level_up_started",
                    "level_up_completed",
                }
                and (
                    event["kind"] != "card_moved"
                    or event.get("reason") in {
                        "damage_reveal",
                        "refresh_point",
                        "level_up",
                        "level_up_discard",
                        "damage_hit",
                    }
                )
            )
        ]

        first_reveal = next(
            i
            for i, event in enumerate(relevant)
            if event == ("card_moved", "damage_reveal", "D1-T001")
        )
        second_reveal = next(
            i
            for i, event in enumerate(relevant)
            if event == ("card_moved", "damage_reveal", "D2-T001")
        )
        refresh_point = next(
            i
            for i, event in enumerate(relevant)
            if event == ("card_moved", "refresh_point", "W1-T001")
        )
        level_started = next(
            i
            for i, event in enumerate(relevant)
            if event[0] == "level_up_started"
        )
        level_completed = next(
            i
            for i, event in enumerate(relevant)
            if event[0] == "level_up_completed"
        )
        third_reveal = next(
            i
            for i, event in enumerate(relevant)
            if (
                event[0] == "card_moved"
                and event[1] == "damage_reveal"
                and event[2] not in {"D1-T001", "D2-T001"}
            )
        )
        damage_hits = [
            i
            for i, event in enumerate(relevant)
            if (
                event[0] == "card_moved"
                and event[1] == "damage_hit"
            )
        ]

        self.assertLess(first_reveal, second_reveal)
        self.assertLess(second_reveal, refresh_point)
        self.assertLess(refresh_point, level_started)
        self.assertLess(level_started, level_completed)
        self.assertLess(level_completed, third_reveal)
        self.assertEqual(3, len(damage_hits))
        self.assertLess(third_reveal, min(damage_hits))

    def test_refresh_induced_level_up_uses_choice_hook_before_damage_resumes(self):
        session = Session(302)

        clock_cards = [
            numbered_card(f"C{i}-T001", T001, 100 + i)
            for i in range(1, 7)
        ]
        d1 = numbered_card("D1-T001", T001, 1)
        d2 = numbered_card("D2-T001", T001, 2)
        waiting = [
            numbered_card(f"W{i}-T001", T001, 10 + i)
            for i in range(1, 9)
        ]

        player = install_damage_refresh_case(
            session,
            deck_cards=[d1, d2],
            waiting_cards=waiting,
        )
        player.clock[:] = list(reversed(clock_cards))

        choices = []

        def choose_first_from_bottom(player_id, candidates):
            choices.append(
                (
                    player_id,
                    tuple(card.instance_id for card in candidates),
                )
            )
            return candidates[-1].instance_id

        session._choose_level_card = choose_first_from_bottom

        result = session._deal_damage("P1", 3)

        self.assertFalse(result.cancelled)
        self.assertEqual(1, len(choices))
        self.assertEqual("P1", choices[0][0])
        self.assertEqual(7, len(choices[0][1]))
        self.assertEqual(3, len(result.revealed))
        self.assertEqual([], player.resolution_zone)

    def test_damage_batch_reaching_fourteen_resolves_two_level_ups_after_batch(self):
        session = Session(303)
        player = session.state.players["P1"]

        initial_clock = [
            player.deck.pop()
            for _ in range(6)
        ]
        player.clock[:] = initial_clock

        start = len(session.events)
        result = session._deal_damage("P1", 8)
        events = session.events[start:]

        self.assertFalse(result.cancelled)
        self.assertEqual(8, len(result.revealed))

        hit_indexes = [
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "card_moved"
                and event.get("reason") == "damage_hit"
            )
        ]
        level_start_indexes = [
            i
            for i, event in enumerate(events)
            if event["kind"] == "level_up_started"
        ]
        level_complete_indexes = [
            i
            for i, event in enumerate(events)
            if event["kind"] == "level_up_completed"
        ]

        self.assertEqual(8, len(hit_indexes))
        self.assertEqual(2, len(level_start_indexes))
        self.assertEqual(2, len(level_complete_indexes))
        self.assertLess(max(hit_indexes), min(level_start_indexes))
        self.assertLess(level_start_indexes[0], level_complete_indexes[0])
        self.assertLess(level_complete_indexes[0], level_start_indexes[1])
        self.assertLess(level_start_indexes[1], level_complete_indexes[1])

        self.assertEqual(2, len(player.level))
        self.assertEqual(0, len(player.clock))
        self.assertEqual([], player.resolution_zone)


if __name__ == "__main__":
    unittest.main()
