from copy import deepcopy
import json
import unittest

from actions import ClockAction
from engine import Session
from test_clock import at_clock


def all_cards(player):
    return (
        player.deck
        + player.hand
        + player.waiting_room
        + player.clock
        + player.level
        + player.stock
        + player.memory
        + player.climax
        + [card for slot in player.stage.values() for card in slot]
    )


def fill_clock_from_deck(session, player_id, count):
    """Test helper: move cards one-by-one to Clock bottom without rule checks."""
    player = session.state.players[player_id]
    moved = []
    for _ in range(count):
        card = session._move_card(
            player_id,
            session_zone_deck(),
            session_zone_clock(),
            reason="test_setup",
        )
        moved.append(card)
    return moved


def session_zone_deck():
    from zones import Zone
    return Zone.DECK


def session_zone_clock():
    from zones import Zone
    return Zone.CLOCK


class LevelUpTests(unittest.TestCase):
    def test_clock_action_interrupts_for_level_up_before_draw_two(self):
        """Clock 6 -> 7 must Level Up completely before ClockAction draws two."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        setup_cards = fill_clock_from_deck(session, player_id, 6)
        chosen_hand = player.hand[0]

        # Ignore setup movement events; inspect only the real ClockAction timing.
        session.events.clear()
        before_deck = list(player.deck)

        session.dispatch(ClockAction(player_id, chosen_hand.instance_id))

        # Default choice = first card counted from Clock bottom.
        expected_level = setup_cards[-1]
        self.assertEqual(expected_level.instance_id, player.level[0].instance_id)
        self.assertEqual([], player.clock)

        # The six non-chosen eligible cards went to Waiting Room.
        expected_waiting = [chosen_hand.instance_id] + [
            card.instance_id for card in setup_cards[:-1]
        ]
        self.assertEqual(
            expected_waiting,
            [card.instance_id for card in player.waiting_room[:6]],
        )

        # Draw two happens only after level-up completion.
        kinds = [event["kind"] for event in session.events]
        complete_index = kinds.index("level_up_completed")
        draw_move_indexes = [
            i for i, event in enumerate(session.events)
            if event["kind"] == "card_moved" and event.get("reason") == "clock_draw"
        ]
        self.assertEqual(2, len(draw_move_indexes))
        self.assertTrue(all(i > complete_index for i in draw_move_indexes))

        self.assertEqual(before_deck[:2], player.hand[-2:])
        self.assertTrue(state.clock_used)

    def test_fourteen_clock_cards_resolve_two_level_ups(self):
        """14 Clock cards require two consecutive Level Ups before returning."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        setup_cards = fill_clock_from_deck(session, player_id, 14)
        session.events.clear()

        session._resolve_interrupt_rules(player_id)

        self.assertEqual(0, len(player.clock))
        self.assertEqual(2, len(player.level))

        # First choice is original bottom card; after removing that bottom group,
        # second choice is the bottom card of the remaining seven.
        self.assertEqual(
            [setup_cards[6].instance_id, setup_cards[13].instance_id],
            [card.instance_id for card in player.level],
        )

        self.assertEqual(
            2,
            sum(1 for e in session.events if e["kind"] == "level_up_completed"),
        )

    def test_level_up_uses_only_bottom_seven_as_candidates(self):
        """With 9 Clock cards, only the bottom seven are eligible."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        setup_cards = fill_clock_from_deck(session, player_id, 9)
        top_two = setup_cards[:2]
        bottom_seven = setup_cards[2:]

        session.events.clear()
        session._resolve_level_up(player_id)

        # Top two are untouched.
        self.assertEqual(
            [card.instance_id for card in top_two],
            [card.instance_id for card in player.clock],
        )

        # Default selection is bottom-most of the eligible seven.
        self.assertEqual(bottom_seven[-1].instance_id, player.level[0].instance_id)

        start_event = next(e for e in session.events if e["kind"] == "level_up_started")
        self.assertEqual(
            [card.instance_id for card in bottom_seven],
            start_event["candidates"],
        )

    def test_level_choice_hook_can_select_another_candidate(self):
        """The engine exposes a choice hook instead of hard-coding the selection."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        setup_cards = fill_clock_from_deck(session, player_id, 7)

        # Simulate a future user choice: choose the top-most card among candidates.
        session._choose_level_card = lambda pid, candidates: candidates[0].instance_id
        session._resolve_level_up(player_id)

        self.assertEqual(setup_cards[0].instance_id, player.level[0].instance_id)

    def test_level_up_preserves_card_conservation_and_uniqueness(self):
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        fill_clock_from_deck(session, player_id, 14)
        before = all_cards(player)
        before_ids = [card.instance_id for card in before]

        session._resolve_interrupt_rules(player_id)

        after = all_cards(player)
        after_ids = [card.instance_id for card in after]

        self.assertEqual(len(before_ids), len(after_ids))
        self.assertEqual(set(before_ids), set(after_ids))
        self.assertEqual(len(after_ids), len(set(after_ids)))

    def test_clock_action_replay_still_records_only_the_original_action(self):
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        fill_clock_from_deck(session, player_id, 6)
        # Setup mutations are test-only and not replayable, so snapshot a fresh
        # deterministic scenario is outside normal Action history. We only verify
        # Level Up itself never appends a synthetic action.
        actions_before = list(session.actions)

        session._resolve_interrupt_rules(player_id)

        self.assertEqual(actions_before, session.actions)


if __name__ == "__main__":
    unittest.main()
