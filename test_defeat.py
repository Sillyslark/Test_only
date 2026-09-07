from copy import deepcopy
import unittest

from actions import AdvancePhaseAction
from engine import Session
from match_result import MatchResult
from test_turns import opened
from zones import Zone


def leave_one_deck_card_elsewhere(session, player_id, destination):
    """Move all but one Deck card out, preserving the final card for the test."""
    player = session.state.players[player_id]
    while len(player.deck) > 1:
        session._move_card(
            player_id,
            Zone.DECK,
            destination,
            reason="test_setup",
        )


class DefeatTests(unittest.TestCase):
    def test_last_deck_card_to_clock_loses_at_check_timing(self):
        """Deck 1 / Waiting 0 -> last card to Clock -> lose only at check timing."""
        session = opened()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        leave_one_deck_card_elsewhere(session, player_id, Zone.MEMORY)
        self.assertEqual(1, len(player.deck))
        self.assertEqual(0, len(player.waiting_room))

        session._move_card(
            player_id,
            Zone.DECK,
            Zone.CLOCK,
            reason="test_effect",
        )

        # The defeat condition exists, but this is a check-type rule.
        self.assertEqual(MatchResult.ONGOING, session.state.result)

        session._resolve_check_timing()

        expected = (
            MatchResult.P2_WIN
            if player_id == "P1"
            else MatchResult.P1_WIN
        )
        self.assertEqual(expected, session.state.result)

    def test_one_card_refresh_loses_at_next_check_timing(self):
        """Deck 1 / Waiting 0 -> last card to Waiting -> Refresh -> lose at next check timing."""
        session = opened()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        leave_one_deck_card_elsewhere(
            session,
            player_id,
            Zone.MEMORY,
        )

        self.assertEqual(1, len(player.deck))
        self.assertEqual(0, len(player.waiting_room))

        # Effect moves the final Deck card to Waiting Room.
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            reason="test_effect",
        )

        self.assertEqual(0, len(player.deck))
        self.assertEqual(1, len(player.waiting_room))

        # Refresh is interrupt-type and resolves first.
        session._resolve_interrupt_rules(player_id)

        # The only Waiting Room card was shuffled into Deck and then moved
        # to Clock as the Refresh Point.
        self.assertEqual(0, len(player.deck))
        self.assertEqual(0, len(player.waiting_room))

        # Defeat is check-type, so Refresh itself must NOT immediately end
        # the game.
        self.assertEqual(
            MatchResult.ONGOING,
            session.state.result,
        )

        # At the next check timing, Deck and Waiting Room are both empty.
        session._resolve_check_timing()

        expected = (
            MatchResult.P2_WIN
            if player_id == "P1"
            else MatchResult.P1_WIN
        )

        self.assertEqual(
            expected,
            session.state.result,
        )

    def test_two_card_refresh_does_not_lose_at_next_check_timing(self):
        """Deck 1 / Waiting 1 -> last card to Waiting -> Refresh -> still has Deck card."""
        session = opened()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        # Put one card in Waiting Room first.
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            reason="test_setup",
        )

        # Leave exactly one card in Deck.
        while len(player.deck) > 1:
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.MEMORY,
                reason="test_setup",
            )

        self.assertEqual(1, len(player.deck))
        self.assertEqual(1, len(player.waiting_room))

        # Effect moves the final Deck card to Waiting Room.
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.WAITING_ROOM,
            reason="test_effect",
        )

        self.assertEqual(0, len(player.deck))
        self.assertEqual(2, len(player.waiting_room))

        # Interrupt-type Refresh resolves.
        session._resolve_interrupt_rules(player_id)

        # Two cards were shuffled into Deck; one became the Refresh Point,
        # so one card must remain in Deck.
        self.assertEqual(1, len(player.deck))
        self.assertEqual(0, len(player.waiting_room))

        self.assertEqual(
            MatchResult.ONGOING,
            session.state.result,
        )

        # Reaching check timing must still not cause defeat.
        session._resolve_check_timing()

        self.assertEqual(
            MatchResult.ONGOING,
            session.state.result,
        )

    def test_condition_does_not_lose_before_check_timing(self):
        """Merely satisfying Deck=0/Waiting=0 must not immediately end the game."""
        session = opened()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        leave_one_deck_card_elsewhere(session, player_id, Zone.MEMORY)
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.MEMORY,
            reason="test_effect",
        )

        self.assertEqual([], player.deck)
        self.assertEqual([], player.waiting_room)
        self.assertEqual(MatchResult.ONGOING, session.state.result)

    def test_one_player_defeated_gives_opponent_win(self):
        session = opened()

        player = session.state.players["P1"]
        while player.deck:
            session._move_card(
                "P1",
                Zone.DECK,
                Zone.MEMORY,
                reason="test_setup",
            )

        session._resolve_check_timing()

        self.assertEqual(MatchResult.P2_WIN, session.state.result)

    def test_both_players_defeated_at_same_check_timing_both_lose(self):
        """Both conditions are evaluated from the same check-timing snapshot."""
        session = opened()

        for player_id in ("P1", "P2"):
            player = session.state.players[player_id]
            while player.deck:
                session._move_card(
                    player_id,
                    Zone.DECK,
                    Zone.MEMORY,
                    reason="test_setup",
                )

        session._resolve_check_timing()

        self.assertEqual(MatchResult.BOTH_LOSE, session.state.result)
        event = session.events[-1]
        self.assertEqual("match_result_changed", event["kind"])
        self.assertEqual({"P1", "P2"}, set(event["defeated_players"]))

    def test_stage_overlap_cannot_erase_defeat_condition_at_same_check_timing(self):
        """Check-rule conditions are snapshotted before check-rule mutations."""
        session = opened()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Make Deck and Waiting Room empty.
        while player.deck:
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.MEMORY,
                reason="test_setup",
            )

        # Create a temporary Stage overlap manually for the same check timing.
        cards = player.hand[:2]
        del player.hand[:2]
        player.stage["front_left"] = list(cards)

        self.assertEqual([], player.waiting_room)

        session._resolve_check_timing(
            stage_player_ids=(player_id,),
        )

        # Overlap creates a Waiting Room card, but defeat was already true at
        # the start of this check timing and must still apply.
        self.assertEqual(1, len(player.waiting_room))
        self.assertNotEqual(MatchResult.ONGOING, session.state.result)

    def test_dispatch_rejects_normal_actions_after_match_end(self):
        session = opened()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        while player.deck:
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.MEMORY,
                reason="test_setup",
            )

        session._resolve_check_timing()
        before = deepcopy(session.__dict__)

        with self.assertRaises(ValueError):
            session.dispatch(AdvancePhaseAction(player_id))

        self.assertEqual(before, session.__dict__)


if __name__ == "__main__":
    unittest.main()
