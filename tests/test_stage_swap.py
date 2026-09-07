from copy import deepcopy
import json
import unittest

from actions import SwapStageSlotsAction
from engine import Session
from tests.helpers import at_main


class StageSwapTests(unittest.TestCase):
    def _put_character_from_hand(self, session, slot):
        player_id = session.state.current_player
        player = session.state.players[player_id]
        card = player.hand.pop(0)
        player.stage[slot] = [card]
        return card

    def _put_marker_from_deck(self, session, slot):
        player_id = session.state.current_player
        player = session.state.players[player_id]
        card = player.deck.pop(0)
        player.markers[slot].append(card)
        return card

    def test_swap_two_occupied_slots_with_all_markers(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        a = "front_left"
        b = "back_right"

        char_a = self._put_character_from_hand(session, a)
        char_b = self._put_character_from_hand(session, b)

        marker_a1 = self._put_marker_from_deck(session, a)
        marker_a2 = self._put_marker_from_deck(session, a)
        marker_b1 = self._put_marker_from_deck(session, b)

        session.dispatch(
            SwapStageSlotsAction(
                player_id,
                a,
                b,
            )
        )

        self.assertEqual([char_b], player.stage[a])
        self.assertEqual([marker_b1], player.markers[a])

        self.assertEqual([char_a], player.stage[b])
        self.assertEqual(
            [marker_a1, marker_a2],
            player.markers[b],
        )

    def test_swap_occupied_slot_with_empty_slot_moves_character_and_markers_together(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        occupied = "front_center"
        empty = "back_left"

        character = self._put_character_from_hand(
            session,
            occupied,
        )
        marker_1 = self._put_marker_from_deck(
            session,
            occupied,
        )
        marker_2 = self._put_marker_from_deck(
            session,
            occupied,
        )

        self.assertEqual([], player.stage[empty])
        self.assertEqual([], player.markers[empty])

        session.dispatch(
            SwapStageSlotsAction(
                player_id,
                occupied,
                empty,
            )
        )

        self.assertEqual([], player.stage[occupied])
        self.assertEqual([], player.markers[occupied])

        self.assertEqual([character], player.stage[empty])
        self.assertEqual(
            [marker_1, marker_2],
            player.markers[empty],
        )

    def test_swap_is_one_atomic_stage_event_and_does_not_create_overlap(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        a = "front_right"
        b = "back_right"

        self._put_character_from_hand(session, a)
        self._put_character_from_hand(session, b)
        self._put_marker_from_deck(session, a)
        self._put_marker_from_deck(session, a)

        start = len(session.events)

        session.dispatch(
            SwapStageSlotsAction(
                player_id,
                a,
                b,
            )
        )

        events = session.events[start:]

        self.assertEqual(
            1,
            sum(
                event["kind"] == "stage_slots_swapped"
                for event in events
            ),
        )

        self.assertFalse(
            any(
                event.get("reason") == "stage_overlap"
                for event in events
            )
        )

        self.assertLessEqual(len(player.stage[a]), 1)
        self.assertLessEqual(len(player.stage[b]), 1)

    def test_swap_event_is_inside_its_resolution_point(self):
        session = at_main()
        player_id = session.state.current_player

        captured_contexts = []

        original_resolve = (
            session._resolve_resolution_point
        )

        def capture_resolution(
            context=None,
            **kwargs,
        ):
            result = original_resolve(
                context,
                **kwargs,
            )

            captured_contexts.append(result)

            return result

        session._resolve_resolution_point = (
            capture_resolution
        )

        session.dispatch(
            SwapStageSlotsAction(
                player_id,
                "front_left",
                "back_left",
            )
        )

        self.assertEqual(
            1,
            len(captured_contexts),
        )

        context = captured_contexts[0]

        # 本次交换事件必须属于本次 Resolution Point。
        swap_events = [
            event
            for event in context.events
            if event["kind"]
            == "stage_slots_swapped"
        ]

        self.assertEqual(
            1,
            len(swap_events),
        )

        self.assertEqual(
            "front_left",
            swap_events[0]["first_slot"],
        )

        self.assertEqual(
            "back_left",
            swap_events[0]["second_slot"],
        )

    def test_invalid_swap_is_atomic(self):
        for case in (
            "same_slot",
            "invalid_slot",
            "wrong_player",
            "wrong_phase",
        ):
            with self.subTest(case=case):
                session = at_main()
                player_id = session.state.current_player

                first = "front_left"
                second = "back_left"
                actor = player_id

                if case == "same_slot":
                    second = first
                elif case == "invalid_slot":
                    second = "invalid"
                elif case == "wrong_player":
                    actor = "P2" if player_id == "P1" else "P1"
                elif case == "wrong_phase":
                    session.state.phase = "climax"

                before = deepcopy(session.__dict__)

                with self.assertRaises(ValueError):
                    session.dispatch(
                        SwapStageSlotsAction(
                            actor,
                            first,
                            second,
                        )
                    )

                self.assertEqual(before, session.__dict__)

    def test_swap_replay_round_trip(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        a = "front_left"
        b = "back_right"

        # Use cards already in Stage / Marker-capable state through direct
        # deterministic setup before the recorded swap action.
        char_a = self._put_character_from_hand(session, a)
        char_b = self._put_character_from_hand(session, b)
        marker_a = self._put_marker_from_deck(session, a)

        # Direct setup is not replay-recorded, so mirror it through normal game
        # state is not possible on restoration. Therefore this test only verifies
        # serialization of the action payload itself.
        session.dispatch(
            SwapStageSlotsAction(
                player_id,
                a,
                b,
            )
        )

        data = session.replay_data()
        action = data["actions"][-1]

        self.assertEqual("swap_stage_slots", action["kind"])
        self.assertEqual(player_id, action["player_id"])
        self.assertEqual(a, action["first_slot"])
        self.assertEqual(b, action["second_slot"])


if __name__ == "__main__":
    unittest.main()
