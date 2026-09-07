import unittest

from actions import ClockAction
from engine import Session
from resolution import InterruptRule
from tests.helpers import at_clock
from zones import Zone


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


def move_deck_to_waiting(session, player_id, count):
    moved = []
    for _ in range(count):
        moved.append(
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.WAITING_ROOM,
                reason="test_setup",
            )
        )
    return moved


def move_deck_to_clock_bottom(session, player_id, count):
    moved = []
    for _ in range(count):
        moved.append(
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.CLOCK,
                reason="test_setup_clock",
            )
        )
    return moved


class RefreshTests(unittest.TestCase):
    def test_last_draw_refreshes_before_next_atomic_step(self):
        """Drawing the final Deck card immediately resolves Refresh."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        move_deck_to_waiting(session, player_id, len(player.deck) - 1)
        last_deck_card = player.deck[0]

        session.events.clear()
        drawn = session._draw_one(player_id, reason="test_draw")

        self.assertEqual(last_deck_card.instance_id, drawn.instance_id)
        self.assertTrue(player.deck)
        self.assertEqual([], player.waiting_room)

        kinds = [event["kind"] for event in session.events]
        self.assertIn("refresh_started", kinds)
        self.assertIn("deck_shuffled", kinds)
        self.assertIn("refresh_completed", kinds)

        refresh_complete = kinds.index("refresh_completed")
        draw_move = next(
            i for i, event in enumerate(session.events)
            if event["kind"] == "card_moved" and event.get("reason") == "test_draw"
        )
        self.assertGreater(refresh_complete, draw_move)

    def test_clock_draw_two_refreshes_between_first_and_second_draw(self):
        """If draw 1 empties Deck, Refresh resolves before draw 2."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        move_deck_to_waiting(session, player_id, len(player.deck) - 1)
        chosen = player.hand[0]

        session.events.clear()
        session.dispatch(ClockAction(player_id, chosen.instance_id))

        draw_indexes = [
            i for i, event in enumerate(session.events)
            if event["kind"] == "card_moved" and event.get("reason") == "clock_draw"
        ]
        refresh_index = next(
            i for i, event in enumerate(session.events)
            if event["kind"] == "refresh_completed"
        )

        self.assertEqual(2, len(draw_indexes))
        self.assertLess(draw_indexes[0], refresh_index)
        self.assertLess(refresh_index, draw_indexes[1])

    def test_refresh_point_can_interrupt_with_level_up(self):
        """Refresh point causing Clock 7 must Level Up before the action continues."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        move_deck_to_clock_bottom(session, player_id, 5)
        move_deck_to_waiting(session, player_id, len(player.deck) - 1)
        chosen = player.hand[0]

        session.events.clear()
        session.dispatch(ClockAction(player_id, chosen.instance_id))

        kinds = [event["kind"] for event in session.events]
        refresh_complete = kinds.index("refresh_completed")
        level_complete = kinds.index("level_up_completed")
        draw_indexes = [
            i for i, event in enumerate(session.events)
            if event["kind"] == "card_moved" and event.get("reason") == "clock_draw"
        ]

        self.assertLess(refresh_complete, level_complete)
        self.assertLess(level_complete, draw_indexes[1])
        self.assertEqual(1, len(player.level))

    def test_simultaneous_refresh_and_level_up_requires_choice(self):
        """Deck 1 -> Clock with Clock 6 makes Refresh and Level Up simultaneous."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Clock = 6.
        move_deck_to_clock_bottom(session, player_id, 6)

        # Leave Deck = 1 and make Waiting Room non-empty so Refresh is valid.
        move_deck_to_waiting(session, player_id, len(player.deck) - 1)

        seen_choices = []

        def choose_interrupt(pid, rules):
            seen_choices.append((pid, tuple(rules)))
            # Deterministic test default: Refresh first.
            return InterruptRule.REFRESH

        session._choose_interrupt_rule = choose_interrupt

        session.events.clear()

        # Atomic movement creates both conditions at the same checkpoint:
        # Deck becomes 0, Clock becomes 7.
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            reason="test_simultaneous",
        )
        session._resolve_interrupt_rules(player_id)

        self.assertEqual(1, len(seen_choices))
        self.assertEqual(player_id, seen_choices[0][0])
        self.assertEqual(
            {InterruptRule.REFRESH, InterruptRule.LEVEL_UP},
            set(seen_choices[0][1]),
        )

        choice_event = next(
            event for event in session.events
            if event["kind"] == "interrupt_rule_chosen"
        )
        self.assertEqual(
            {"refresh", "level_up"},
            set(choice_event["options"]),
        )
        self.assertEqual("refresh", choice_event["chosen"])

        # Refresh first adds one refresh point to Clock, then Level Up resolves.
        kinds = [event["kind"] for event in session.events]
        self.assertLess(kinds.index("refresh_completed"), kinds.index("level_up_completed"))

    def test_simultaneous_choice_can_select_level_up_first(self):
        """The same simultaneous state also supports choosing Level Up first."""
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        move_deck_to_clock_bottom(session, player_id, 6)
        move_deck_to_waiting(session, player_id, len(player.deck) - 1)

        session._choose_interrupt_rule = (
            lambda pid, rules: InterruptRule.LEVEL_UP
        )

        session.events.clear()
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            reason="test_simultaneous",
        )
        session._resolve_interrupt_rules(player_id)

        kinds = [event["kind"] for event in session.events]
        self.assertLess(kinds.index("level_up_completed"), kinds.index("refresh_completed"))

        # Level Up first clears those seven Clock cards; Refresh point then leaves
        # a single card in Clock.
        self.assertEqual(1, len(player.clock))

    def test_refresh_moves_waiting_room_cards_individually_and_conserves_cards(self):
        session = at_clock()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        move_deck_to_waiting(session, player_id, len(player.deck))
        before_ids = [card.instance_id for card in all_cards(player)]
        recycled_count = len(player.waiting_room)

        session.events.clear()
        session._resolve_interrupt_rules(player_id)

        after_ids = [card.instance_id for card in all_cards(player)]
        rebuild_moves = [
            event for event in session.events
            if event["kind"] == "card_moved" and event.get("reason") == "refresh_rebuild"
        ]

        self.assertEqual(recycled_count, len(rebuild_moves))
        self.assertEqual(len(before_ids), len(after_ids))
        self.assertEqual(set(before_ids), set(after_ids))
        self.assertEqual(len(after_ids), len(set(after_ids)))

    def test_refresh_shuffle_is_deterministic_from_rng_state(self):
        """Same state + RNG state must produce the same refreshed Deck order."""
        a = at_clock()
        b = at_clock()

        for session in (a, b):
            player_id = session.state.current_player
            player = session.state.players[player_id]
            move_deck_to_waiting(session, player_id, len(player.deck))
            session.events.clear()
            session._resolve_interrupt_rules(player_id)

        pa = a.state.players[a.state.current_player]
        pb = b.state.players[b.state.current_player]

        self.assertEqual(
            [card.instance_id for card in pa.deck],
            [card.instance_id for card in pb.deck],
        )
        self.assertEqual(a.state.rng_state, b.state.rng_state)


if __name__ == "__main__":
    unittest.main()
