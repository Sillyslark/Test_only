import unittest

from actions import PlayCardAction
from engine import Zone
from rule_resolution import STAGE_SLOTS
from tests.helpers import at_main


class MarkerTests(unittest.TestCase):
    def make_host(self, session, slot="front_center"):
        player_id = session.state.current_player
        player = session.state.players[player_id]
        host = player.hand[0]

        session.dispatch(
            PlayCardAction(
                player_id,
                host.instance_id,
                slot,
            )
        )

        return player_id, player, host

    def test_multiple_markers_can_exist_under_one_stage_slot(self):
        session = at_main()
        player_id, player, host = self.make_host(session)

        slot = "front_center"
        marker_1 = player.deck[0]
        marker_2 = player.deck[1]

        session._move_card(
            player_id,
            Zone.DECK,
            Zone.MARKER,
            card_id=marker_1.instance_id,
            destination_slot=slot,
            reason="test_marker",
        )
        session._move_card(
            player_id,
            Zone.DECK,
            Zone.MARKER,
            card_id=marker_2.instance_id,
            destination_slot=slot,
            reason="test_marker",
        )

        self.assertEqual([host], player.stage[slot])
        self.assertEqual([marker_1, marker_2], player.markers[slot])

    def test_moving_deck_card_to_marker_does_not_trigger_stage_overlap(self):
        session = at_main()
        player_id, player, host = self.make_host(session)

        slot = "front_center"
        marker = player.deck[0]
        start = len(session.events)

        session._move_card(
            player_id,
            Zone.DECK,
            Zone.MARKER,
            card_id=marker.instance_id,
            destination_slot=slot,
            reason="test_marker",
        )

        session._resolve_resolution_point(
            stage_player_ids=(player_id,),
        )

        self.assertEqual([host], player.stage[slot])
        self.assertEqual([marker], player.markers[slot])

        new_events = session.events[start:]
        self.assertFalse(
            any(
                event.get("reason") == "stage_overlap"
                for event in new_events
            )
        )

    def test_marker_keeps_original_card_identity_and_definition(self):
        session = at_main()
        player_id, player, _ = self.make_host(session)

        slot = "front_center"
        marker = player.deck[0]

        session._move_card(
            player_id,
            Zone.DECK,
            Zone.MARKER,
            card_id=marker.instance_id,
            destination_slot=slot,
            reason="test_marker",
        )

        stored = player.markers[slot][0]

        self.assertIs(marker, stored)
        self.assertEqual(marker.instance_id, stored.instance_id)
        self.assertEqual(marker.definition, stored.definition)

    def test_marker_destination_requires_valid_stage_slot(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]
        marker = player.deck[0]

        with self.assertRaises(ValueError):
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.MARKER,
                card_id=marker.instance_id,
                destination_slot="invalid",
                reason="test_marker",
            )

    def test_marker_destination_requires_character_in_that_slot(self):
        session = at_main()
        player_id = session.state.current_player
        player = session.state.players[player_id]
        marker = player.deck[0]
        empty_slot = STAGE_SLOTS[0]

        self.assertEqual([], player.stage[empty_slot])

        with self.assertRaises(ValueError):
            session._move_card(
                player_id,
                Zone.DECK,
                Zone.MARKER,
                card_id=marker.instance_id,
                destination_slot=empty_slot,
                reason="test_marker",
            )


if __name__ == "__main__":
    unittest.main()
