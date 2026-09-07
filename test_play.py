from copy import deepcopy
from dataclasses import replace
import json
import unittest

from actions import AdvancePhaseAction, PlayCardAction
from cards import CardDefinition, load_card
from engine import Session, Zone, other
from rule_resolution import STAGE_SLOTS, resolve_stage_overlaps
from test_turns import opened


TEST_CARD = load_card("TEST/T-001.json")


def at_main():
    session = opened()
    for _ in range(3):
        session.dispatch(AdvancePhaseAction(session.state.current_player))
    return session


class PlayTests(unittest.TestCase):
    def test_all_slots_replacement_and_replay(self):
        session = at_main()
        state = session.state
        player = state.players[state.current_player]

        self.assertEqual(
            TEST_CARD,
            player.hand[0].definition,
        )

        for slot in STAGE_SLOTS:
            card = player.hand[0]
            session.dispatch(
                PlayCardAction(
                    state.current_player,
                    card.instance_id,
                    slot,
                )
            )
            self.assertEqual([card], player.stage[slot])
            self.assertTrue(player.stage[slot][0].face_up)

        old = player.stage[STAGE_SLOTS[0]][0]
        new = player.hand[0]
        start = len(session.events)

        session.dispatch(
            PlayCardAction(
                state.current_player,
                new.instance_id,
                STAGE_SLOTS[0],
            )
        )

        self.assertEqual([new], player.stage[STAGE_SLOTS[0]])
        self.assertEqual(old, player.waiting_room[0])

        events = session.events[start:]
        self.assertEqual(
            ["card_moved", "card_moved", "card_played"],
            [event["kind"] for event in events],
        )
        self.assertEqual("stage_overlap", events[1]["reason"])

        cards = (
            player.deck
            + player.hand
            + player.clock
            + player.waiting_room
            + [card for zone in player.stage.values() for card in zone]
        )
        self.assertEqual(50, len(cards))
        self.assertEqual(50, len({card.instance_id for card in cards}))

        restored = Session.from_replay(
            json.loads(json.dumps(session.replay_data()))
        )
        self.assertEqual(state, restored.state)
        self.assertEqual(session.events, restored.events)

    def test_multiple_overlaps_resolve_before_entry(self):
        session = at_main()
        player = session.state.players[session.state.current_player]
        cards = player.hand[:3]
        del player.hand[:3]
        player.stage["back_left"] = list(cards)

        start = len(session.events)

        resolve_stage_overlaps(
            player,
            session.state.current_player,
            lambda source_slot, card_id, destination_index: session._move_card(
                session.state.current_player,
                Zone.STAGE,
                Zone.WAITING_ROOM,
                card_id=card_id,
                source_slot=source_slot,
                destination_index=destination_index,
                reason="stage_overlap",
            ),
        )

        self.assertEqual(cards[:1], player.stage["back_left"])
        self.assertEqual(cards[1:], player.waiting_room)

        events = session.events[start:]
        self.assertEqual(2, len(events))
        self.assertTrue(
            all(event["kind"] == "card_moved" for event in events)
        )
        self.assertTrue(
            all(event["reason"] == "stage_overlap" for event in events)
        )

    def test_invalid_play_is_atomic(self):
        for case in (
            "phase",
            "player",
            "slot",
            "card",
            "kind",
            "cost",
            "level",
        ):
            session = at_main()
            state = session.state
            player = state.players[state.current_player]

            actor = state.current_player
            slot = STAGE_SLOTS[0]
            cid = player.hand[0].instance_id

            if case == "phase":
                state.phase = "clock"
            elif case == "player":
                actor = other(actor)
            elif case == "slot":
                slot = "invalid"
            elif case == "card":
                cid = "invalid"
            else:
                definition = replace(
                    player.hand[0].definition,
                    **{case: "event" if case == "kind" else 1},
                )
                player.hand[0] = replace(
                    player.hand[0],
                    definition=definition,
                )

            before = deepcopy(session.__dict__)

            with self.subTest(case=case), self.assertRaises(ValueError):
                session.dispatch(
                    PlayCardAction(
                        actor,
                        cid,
                        slot,
                    )
                )

            self.assertEqual(before, session.__dict__)


if __name__ == "__main__":
    unittest.main()
