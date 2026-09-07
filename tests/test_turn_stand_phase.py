import unittest

from actions import AdvancePhaseAction, MulliganAction
from engine import Session, other


class TurnStandPhaseTests(unittest.TestCase):
    def open_first_turn(self, seed=42):
        session = Session(seed)

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        return session

    def test_turn_start_then_stand_phase_start(self):
        """Opening both Mulligans starts turn 1, then enters Stand Phase."""
        session = self.open_first_turn()
        state = session.state

        self.assertEqual(1, state.turn_number)
        self.assertEqual(state.first_player, state.current_player)
        self.assertEqual("stand", state.phase)

        lifecycle = [
            event
            for event in session.events
            if event["kind"] in {
                "turn_started",
                "phase_started",
                "phase_processed",
                "action_window_opened",
            }
        ]

        self.assertGreaterEqual(len(lifecycle), 4)

        turn_started, stand_started, stand_processed, action_window = lifecycle[-4:]

        self.assertEqual("turn_started", turn_started["kind"])
        self.assertEqual(state.current_player, turn_started["player"])
        self.assertEqual(1, turn_started["turn"])

        self.assertEqual("phase_started", stand_started["kind"])
        self.assertEqual("stand", stand_started["phase"])

        self.assertEqual("phase_processed", stand_processed["kind"])
        self.assertEqual("stand", stand_processed["phase"])

        self.assertEqual("action_window_opened", action_window["kind"])
        self.assertEqual("stand", action_window["phase"])

    def test_stand_phase_process_is_currently_noop(self):
        """Stand processing currently has no card-orientation implementation."""
        session = Session(43)

        before = {
            player_id: {
                "deck": list(player.deck),
                "hand": list(player.hand),
                "waiting_room": list(player.waiting_room),
                "clock": list(player.clock),
                "level": list(player.level),
                "stock": list(player.stock),
                "memory": list(player.memory),
                "climax": list(player.climax),
                "resolution_zone": list(player.resolution_zone),
                "stage": {
                    slot: list(cards)
                    for slot, cards in player.stage.items()
                },
            }
            for player_id, player in session.state.players.items()
        }

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        after = {
            player_id: {
                "deck": list(player.deck),
                "hand": list(player.hand),
                "waiting_room": list(player.waiting_room),
                "clock": list(player.clock),
                "level": list(player.level),
                "stock": list(player.stock),
                "memory": list(player.memory),
                "climax": list(player.climax),
                "resolution_zone": list(player.resolution_zone),
                "stage": {
                    slot: list(cards)
                    for slot, cards in player.stage.items()
                },
            }
            for player_id, player in session.state.players.items()
        }

        # Both Mulligans selected 0 cards, so entering/processing Stand must not
        # move any card in the current implementation.
        self.assertEqual(before, after)

    def test_stand_action_window_only_allows_advance_to_draw(self):
        session = self.open_first_turn(44)
        current = session.state.current_player
        opponent = other(current)

        self.assertEqual(
            (AdvancePhaseAction(current),),
            session.legal_actions(current),
        )
        self.assertEqual(
            (),
            session.legal_actions(opponent),
        )

    def test_stand_advance_emits_stand_end_before_draw_start(self):
        """This test stops conceptually at Draw Phase START.

        It does not test Draw Phase processing, the mandatory draw, or the Draw
        action window. Those belong in test_turn_draw_phase.py.
        """
        session = self.open_first_turn(45)
        current = session.state.current_player

        start = len(session.events)
        session.dispatch(AdvancePhaseAction(current))
        new_events = session.events[start:]

        stand_end_index = next(
            i
            for i, event in enumerate(new_events)
            if (
                event["kind"] == "phase_ended"
                and event["phase"] == "stand"
            )
        )
        draw_start_index = next(
            i
            for i, event in enumerate(new_events)
            if (
                event["kind"] == "phase_started"
                and event["phase"] == "draw"
            )
        )

        self.assertLess(stand_end_index, draw_start_index)

        # The Stand test only establishes the hand-off boundary:
        # Stand END -> Draw START.
        self.assertEqual("draw", new_events[draw_start_index]["phase"])
        self.assertEqual(current, new_events[draw_start_index]["player"])

    def test_wrong_player_cannot_end_stand_phase(self):
        session = self.open_first_turn(46)
        current = session.state.current_player

        with self.assertRaises(ValueError):
            session.dispatch(
                AdvancePhaseAction(other(current))
            )


if __name__ == "__main__":
    unittest.main()
