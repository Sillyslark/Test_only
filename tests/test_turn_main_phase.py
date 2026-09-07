import unittest

from actions import (
    AdvancePhaseAction,
    PlayCardAction,
    StageSwapOptions,
    SwapStageSlotsAction,
)
from engine import other
from resolution import ResolutionContext, TriggeredEffect
from tests.helpers import at_main
from copy import deepcopy
from actions import (
    AdvancePhaseAction,
    PlayCardAction,
    StageSwapOptions,
    SwapStageSlotsAction,
)
from resolution import (
    ResolutionContext,
    TriggeredEffect,
)
from actions import (
    AdvancePhaseAction,
    StageSwapOptions,
)

import engine
from engine import other
from resolution import TriggeredEffect
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

    def test_main_play_reopens_action_window_when_no_effect_is_pending(self):
        session = at_main(76)
        current = session.state.current_player
        player = session.state.players[current]
        card = player.hand[0]

        before_count = sum(
            event["kind"] == "action_window_opened"
            and event.get("phase") == "main"
            for event in session.events
        )

        session.dispatch(
            PlayCardAction(
                current,
                card.instance_id,
                "front_left",
            )
        )

        after_count = sum(
            event["kind"] == "action_window_opened"
            and event.get("phase") == "main"
            for event in session.events
        )

        self.assertEqual(before_count + 1, after_count)
        self.assertFalse(session._has_pending_effects())

    def test_main_swap_reopens_action_window_when_no_effect_is_pending(self):
        session = at_main(77)
        current = session.state.current_player

        before_count = sum(
            event["kind"] == "action_window_opened"
            and event.get("phase") == "main"
            for event in session.events
        )

        session.dispatch(
            SwapStageSlotsAction(
                current,
                "front_left",
                "back_left",
            )
        )

        after_count = sum(
            event["kind"] == "action_window_opened"
            and event.get("phase") == "main"
            for event in session.events
        )

        self.assertEqual(before_count + 1, after_count)
        self.assertFalse(session._has_pending_effects())

    def test_pending_effect_blocks_normal_main_legal_actions(self):
        session = at_main(78)
        current = session.state.current_player

        context = ResolutionContext(
            turn_player=current,
            non_turn_player=other(current),
            event_cursor=len(session.events),
        )
        context.add_effect(
            TriggeredEffect(
                effect_id="TEST-PENDING",
                controller=current,
            )
        )
        session.pending_resolution_context = context

        self.assertTrue(session._has_pending_effects())
        self.assertEqual((), session.legal_actions(current))
        self.assertEqual((), session.legal_actions(other(current)))

    def test_pending_effect_prevents_main_action_window_from_reopening(self):
        session = at_main(79)
        current = session.state.current_player

        context = ResolutionContext(
            turn_player=current,
            non_turn_player=other(current),
            event_cursor=len(session.events),
        )
        context.add_effect(
            TriggeredEffect(
                effect_id="TEST-PENDING",
                controller=current,
            )
        )
        session.pending_resolution_context = context

        before_count = sum(
            event["kind"] == "action_window_opened"
            and event.get("phase") == "main"
            for event in session.events
        )

        opened = session._open_action_window("main")

        after_count = sum(
            event["kind"] == "action_window_opened"
            and event.get("phase") == "main"
            for event in session.events
        )

        self.assertFalse(opened)
        self.assertEqual(before_count, after_count)

    def test_pending_effect_blocks_direct_main_dispatch(self):
        for case in (
            "play_card",
            "swap_stage",
            "advance_phase",
        ):
            with self.subTest(case=case):
                session = at_main(80)

                current = session.state.current_player
                player = session.state.players[current]

                # -----------------------------------------
                # 构造一个尚未处理的效果。
                # -----------------------------------------

                context = ResolutionContext(
                    turn_player=current,
                    non_turn_player=other(current),
                    event_cursor=len(session.events),
                )

                context.add_effect(
                    TriggeredEffect(
                        effect_id="TEST-PENDING",
                        controller=current,
                    )
                )

                session.pending_resolution_context = context

                # -----------------------------------------
                # 构造试图绕过 legal_actions 的 Action。
                # -----------------------------------------

                if case == "play_card":
                    action = PlayCardAction(
                        current,
                        player.hand[0].instance_id,
                        "front_left",
                    )

                elif case == "swap_stage":
                    action = SwapStageSlotsAction(
                        current,
                        "front_left",
                        "back_left",
                    )

                else:
                    action = AdvancePhaseAction(
                        current
                    )

                before = deepcopy(
                    session.__dict__
                )

                with self.assertRaisesRegex(
                    ValueError,
                    "待处理效果",
                ):
                    session.dispatch(action)

                # 被拒绝后必须完全 atomic。
                self.assertEqual(
                    before,
                    session.__dict__,
                )

    def test_main_start_event_enters_resolution_point(self):
        original = engine.collect_triggers

        captured = []

        def fake_collect(
            events,
            context,
        ):
            captured.extend(events)
            return []

        engine.collect_triggers = fake_collect

        try:
            session = at_main(81)

            main_start_events = [
                event
                for event in captured
                if (
                    event["kind"]
                    == "phase_started"
                    and event["phase"]
                    == "main"
                )
            ]

            self.assertEqual(
                1,
                len(main_start_events),
            )

        finally:
            engine.collect_triggers = original

    def test_main_start_pending_effect_blocks_main_process_and_action_window(self):
        original = engine.collect_triggers

        def fake_collect(
            events,
            context,
        ):
            for event in events:
                if (
                    event["kind"]
                    == "phase_started"
                    and event["phase"]
                    == "main"
                ):
                    context.add_effect(
                        TriggeredEffect(
                            effect_id="MAIN-START",
                            controller=context.turn_player,
                        )
                    )

            return []

        engine.collect_triggers = fake_collect

        try:
            session = at_main(82)

            self.assertEqual(
                "main",
                session.state.phase,
            )

            self.assertTrue(
                session._has_pending_effects()
            )

            self.assertEqual(
                (
                    "phase_start",
                    "main",
                ),
                session.pending_continuation,
            )

            main_processed = [
                event
                for event in session.events
                if (
                    event["kind"]
                    == "phase_processed"
                    and event["phase"]
                    == "main"
                )
            ]

            main_windows = [
                event
                for event in session.events
                if (
                    event["kind"]
                    == "action_window_opened"
                    and event["phase"]
                    == "main"
                )
            ]

            self.assertEqual(
                [],
                main_processed,
            )

            self.assertEqual(
                [],
                main_windows,
            )

        finally:
            engine.collect_triggers = original

    def test_main_end_event_enters_resolution_point(self):
        session = at_main(83)

        original = engine.collect_triggers
        captured = []

        def fake_collect(
            events,
            context,
        ):
            captured.extend(events)
            return []

        engine.collect_triggers = fake_collect

        try:
            current = session.state.current_player

            session.dispatch(
                AdvancePhaseAction(current)
            )

            main_end_events = [
                event
                for event in captured
                if (
                    event["kind"]
                    == "phase_ended"
                    and event["phase"]
                    == "main"
                )
            ]

            self.assertEqual(
                1,
                len(main_end_events),
            )

        finally:
            engine.collect_triggers = original

    def test_main_end_pending_effect_blocks_climax_start(self):
        session = at_main(84)

        original = engine.collect_triggers

        def fake_collect(
            events,
            context,
        ):
            for event in events:
                if (
                    event["kind"]
                    == "phase_ended"
                    and event["phase"]
                    == "main"
                ):
                    context.add_effect(
                        TriggeredEffect(
                            effect_id="MAIN-END",
                            controller=context.turn_player,
                        )
                    )

            return []

        engine.collect_triggers = fake_collect

        try:
            current = session.state.current_player

            start = len(session.events)

            session.dispatch(
                AdvancePhaseAction(current)
            )

            events = session.events[start:]

            self.assertEqual(
                "main",
                session.state.phase,
            )

            self.assertTrue(
                session._has_pending_effects()
            )

            self.assertEqual(
                (
                    "phase_end",
                    "main",
                ),
                session.pending_continuation,
            )

            self.assertFalse(
                any(
                    event["kind"]
                    == "phase_started"
                    and event.get("phase")
                    == "climax"
                    for event in events
                )
            )

        finally:
            engine.collect_triggers = original

if __name__ == "__main__":
    unittest.main()
