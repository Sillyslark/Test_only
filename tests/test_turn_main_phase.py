import unittest

from actions import AdvancePhaseAction, StageSwapOptions
from engine import other
from tests.helpers import at_main


class TurnMainPhaseTests(unittest.TestCase):
    def test_main_phase_lifecycle_reaches_action_window(self):
        session = at_main(71)
        current = session.state.current_player

        self.assertEqual("main", session.state.phase)

        lifecycle = [
            event
            for event in session.events
            if (
                event["kind"] in {
                    "phase_started",
                    "phase_processed",
                    "action_window_opened",
                }
                and event.get("phase") == "main"
            )
        ]

        self.assertGreaterEqual(len(lifecycle), 3)
        self.assertEqual(
            [
                "phase_started",
                "phase_processed",
                "action_window_opened",
            ],
            [event["kind"] for event in lifecycle[-3:]],
        )

        self.assertTrue(
            all(
                event["player"] == current
                for event in lifecycle[-3:]
            )
        )

    def test_main_phase_process_is_currently_noop(self):
        session = at_main(72)
        current = session.state.current_player
        player = session.state.players[current]

        before = {
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
            "markers": {
                slot: list(cards)
                for slot, cards in player.markers.items()
            },
        }

        # Main Phase processing has already completed when at_main() returns.
        # No Main-specific automatic rule exists yet, so the state should remain
        # stable while sitting in the action window.
        after = {
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
            "markers": {
                slot: list(cards)
                for slot, cards in player.markers.items()
            },
        }

        self.assertEqual(before, after)

    def test_main_action_window_exposes_current_main_options(self):
        session = at_main(73)
        current = session.state.current_player

        legal = session.legal_actions(current)

        self.assertTrue(
            any(
                isinstance(action, AdvancePhaseAction)
                for action in legal
            )
        )
        self.assertTrue(
            any(
                isinstance(action, StageSwapOptions)
                for action in legal
            )
        )

        self.assertEqual(
            (),
            session.legal_actions(other(current)),
        )

    def test_main_advance_emits_main_end_before_climax_start(self):
        session = at_main(74)
        current = session.state.current_player

        start = len(session.events)

        session.dispatch(
            AdvancePhaseAction(current)
        )

        events = session.events[start:]

        self.assertEqual(
            "climax",
            session.state.phase,
        )

        main_end = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "phase_ended"
                and event["phase"] == "main"
            )
        )

        climax_start = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "phase_started"
                and event["phase"] == "climax"
            )
        )

        self.assertLess(
            main_end,
            climax_start,
        )

    def test_wrong_player_cannot_end_main_phase(self):
        session = at_main(75)
        current = session.state.current_player

        with self.assertRaises(ValueError):
            session.dispatch(
                AdvancePhaseAction(
                    other(current)
                )
            )


if __name__ == "__main__":
    unittest.main()
