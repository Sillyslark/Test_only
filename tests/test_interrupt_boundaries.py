from copy import deepcopy
import unittest

from engine import Session
from resolution import InterruptRule
from tests.helpers import at_clock
from zones import Zone


def move_n(session, player_id, source, destination, count, reason):
    moved = []
    for _ in range(count):
        moved.append(
            session._move_card(
                player_id,
                source,
                destination,
                reason=reason,
            )
        )
    return moved


class InterruptBoundaryTests(unittest.TestCase):
    def test_single_interrupt_does_not_call_choice_hook(self):
        """只有一个中断规则成立时，应自动处理，不要求用户选择。"""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Clock = 7, Deck remains non-empty -> only Level Up is available.
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            7,
            "test_setup_clock",
        )

        def should_not_be_called(pid, rules):
            raise AssertionError("单一中断规则不应调用选择钩子")

        session._choose_interrupt_rule = should_not_be_called
        session._resolve_interrupt_rules(player_id)

        self.assertLess(len(player.clock), 7)
        self.assertEqual(1, len(player.level))

    def test_invalid_simultaneous_choice_is_atomic(self):
        """同时中断时若选择无效规则，必须在任何规则结算前失败。"""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Build Clock = 6.
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            6,
            "test_setup_clock",
        )

        # Leave Deck = 1 and make Waiting Room non-empty.
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            len(player.deck) - 1,
            "test_setup_waiting",
        )

        # Final Deck card -> Clock gives Deck = 0 and Clock = 7.
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            reason="test_simultaneous",
        )

        before = deepcopy(
            (
                session.state,
                session.events,
                session.actions,
                session.hashes,
            )
        )

        session._choose_interrupt_rule = (
            lambda pid, rules: "not-a-valid-rule"
        )

        with self.assertRaises(ValueError):
            session._resolve_interrupt_rules(player_id)

        after = (
            session.state,
            session.events,
            session.actions,
            session.hashes,
        )
        self.assertEqual(before, after)

    def test_interrupts_are_rescanned_after_each_resolution(self):
        """处理一个中断后，必须根据新状态重新扫描，而不是使用旧候选列表。"""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            6,
            "test_setup_clock",
        )
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            len(player.deck) - 1,
            "test_setup_waiting",
        )

        session._move_card(
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            reason="test_simultaneous",
        )

        calls = []

        def choose_refresh_first(pid, rules):
            calls.append(tuple(rules))
            return InterruptRule.REFRESH

        session._choose_interrupt_rule = choose_refresh_first
        session.events.clear()

        session._resolve_interrupt_rules(player_id)

        # Choice happens only for the initial simultaneous state.
        self.assertEqual(1, len(calls))

        kinds = [event["kind"] for event in session.events]
        self.assertIn("refresh_completed", kinds)
        self.assertIn("level_up_completed", kinds)
        self.assertLess(
            kinds.index("refresh_completed"),
            kinds.index("level_up_completed"),
        )

    def test_empty_deck_and_empty_waiting_room_is_not_a_refresh(self):
        """Deck 与 Waiting Room 都为空时，不能凭空执行 Refresh。"""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Move the entire Deck somewhere that is not Waiting Room.
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.MEMORY,
            len(player.deck),
            "test_setup_memory",
        )

        self.assertEqual([], player.deck)
        self.assertEqual([], player.waiting_room)

        before = deepcopy(
            (
                session.state,
                session.events,
                session.actions,
                session.hashes,
            )
        )

        session._resolve_interrupt_rules(player_id)

        after = (
            session.state,
            session.events,
            session.actions,
            session.hashes,
        )
        self.assertEqual(before, after)

        with self.assertRaises(ValueError):
            session._draw_one(player_id, reason="test_draw")

    def test_one_card_refresh_can_chain_into_level_and_second_refresh(self):
        """极端边界：1张 Waiting Room 的刷新可经 Level Up 再产生第二次 Refresh。"""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Clock = 6.
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            6,
            "test_setup_clock",
        )

        # Keep exactly one card in Waiting Room and move all remaining Deck
        # cards to Memory, so Deck is empty and Refresh has exactly one card.
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            reason="test_setup_waiting",
        )
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.MEMORY,
            len(player.deck),
            "test_setup_memory",
        )

        self.assertEqual(0, len(player.deck))
        self.assertEqual(1, len(player.waiting_room))
        self.assertEqual(6, len(player.clock))

        session.events.clear()
        session._resolve_interrupt_rules(player_id)

        kinds = [event["kind"] for event in session.events]

        # First refresh point makes Clock = 7 -> Level Up.
        self.assertGreaterEqual(kinds.count("refresh_completed"), 2)
        self.assertGreaterEqual(kinds.count("level_up_completed"), 1)

        first_refresh = kinds.index("refresh_completed")
        first_level = kinds.index("level_up_completed")
        second_refresh = kinds.index(
            "refresh_completed",
            first_refresh + 1,
        )

        self.assertLess(first_refresh, first_level)
        self.assertLess(first_level, second_refresh)

    def test_available_interrupt_rules_reports_exact_current_state(self):
        """候选集合本身也应准确反映当前状态。"""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        self.assertEqual((), session._available_interrupt_rules(player_id))

        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            7,
            "test_setup_clock",
        )
        self.assertEqual(
            (InterruptRule.LEVEL_UP,),
            session._available_interrupt_rules(player_id),
        )

        # Move the remaining Deck to Waiting Room so Refresh also becomes valid.
        move_n(
            session,
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            len(player.deck),
            "test_setup_waiting",
        )

        self.assertEqual(
            {InterruptRule.LEVEL_UP, InterruptRule.REFRESH},
            set(session._available_interrupt_rules(player_id)),
        )


if __name__ == "__main__":
    unittest.main()
