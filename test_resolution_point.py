from copy import deepcopy
import unittest
from unittest.mock import patch

from actions import PlayCardAction
from engine import Session
from match_result import MatchResult
from resolution import ResolutionContext
from rule_resolution import STAGE_SLOTS
from test_play import at_main
from test_turns import opened
from zones import Zone


class ResolutionPointTests(unittest.TestCase):
    def test_check_rule_does_not_run_before_resolution_point(self):
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

        self.assertEqual(MatchResult.ONGOING, session.state.result)

        session._resolve_resolution_point()

        self.assertNotEqual(MatchResult.ONGOING, session.state.result)

    def test_empty_resolution_point_is_noop(self):
        session = opened()
        before_state = deepcopy(session.state)
        before_events = deepcopy(session.events)
        before_actions = deepcopy(session.actions)
        before_hashes = deepcopy(session.hashes)

        session._resolve_resolution_point()

        self.assertEqual(before_state, session.state)
        self.assertEqual(before_events, session.events)
        self.assertEqual(before_actions, session.actions)
        self.assertEqual(before_hashes, session.hashes)

    def test_stage_overlap_is_resolved_through_unified_entry(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]

        cards = player.hand[:3]
        del player.hand[:3]
        player.stage["back_left"] = list(cards)

        session._resolve_resolution_point(
            stage_player_ids=(player_id,),
        )

        self.assertEqual(cards[:1], player.stage["back_left"])
        self.assertEqual(cards[1:], player.waiting_room)

    def test_same_timing_defeat_snapshot_survives_stage_overlap(self):
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

        cards = player.hand[:2]
        del player.hand[:2]
        player.stage["front_left"] = list(cards)

        session._resolve_resolution_point(
            stage_player_ids=(player_id,),
        )

        self.assertEqual(1, len(player.waiting_room))
        self.assertNotEqual(MatchResult.ONGOING, session.state.result)

    def test_play_card_uses_exactly_one_resolution_point(self):
        session = at_main()
        state = session.state
        player = state.players[state.current_player]
        card = player.hand[0]

        with patch.object(
            session,
            "_resolve_resolution_point",
            wraps=session._resolve_resolution_point,
        ) as resolver:
            session.dispatch(
                PlayCardAction(
                    state.current_player,
                    card.instance_id,
                    STAGE_SLOTS[0],
                )
            )

        resolver.assert_called_once()

    def test_trigger_collection_sees_check_rule_events_before_timing_event(self):
        session = at_main()
        state = session.state
        player_id = state.current_player
        player = state.players[player_id]

        # Put one existing card on Stage, then play another into the same slot.
        existing = player.hand[0]
        player.hand.pop(0)
        player.stage[STAGE_SLOTS[0]] = [existing]

        played = player.hand[0]
        captured = []

        def fake_collect(events, context):
            captured.extend(events)
            return []

        with patch("engine.collect_triggers", side_effect=fake_collect):
            session.dispatch(
                PlayCardAction(
                    player_id,
                    played.instance_id,
                    STAGE_SLOTS[0],
                )
            )

        kinds = [event["kind"] for event in captured]
        reasons = [event.get("reason") for event in captured]

        self.assertEqual(
            ["card_moved", "card_moved", "card_played"],
            kinds,
        )
        self.assertEqual("play", reasons[0])
        self.assertEqual("stage_overlap", reasons[1])

    def test_resolution_context_captures_whole_timing_once(self):
        session = opened()
        player_id = session.state.current_player

        context = ResolutionContext(
            turn_player=player_id,
            non_turn_player="P2" if player_id == "P1" else "P1",
            event_cursor=len(session.events),
        )

        session._resolve_resolution_point(
            context,
            timing_events=(
                {"kind": "test_timing_event", "player": player_id},
            ),
        )

        self.assertEqual(
            ["test_timing_event"],
            [event["kind"] for event in context.events],
        )

        # Calling capture again must not duplicate already-seen events.
        self.assertEqual([], context.capture_new_events(session.events))


if __name__ == "__main__":
    unittest.main()
