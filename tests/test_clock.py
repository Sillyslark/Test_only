from copy import deepcopy
import json
import unittest
from tests.helpers import at_clock
from actions import AdvancePhaseAction, ClockAction
from card_definition import Card
from card_loader import load_card
from engine import Session, other, state_hash
from tests.helpers import opened

TEST_CARD = load_card("TEST/T-001.json")



class ClockTests(unittest.TestCase):
    def test_clock_moves_to_top_and_draws_two_in_order(self):
        session = at_clock()
        state = session.state
        player = state.players[state.current_player]
        before = deepcopy(player)
        chosen = player.hand[2]

        session.dispatch(
            ClockAction(
                state.current_player,
                chosen.instance_id,
            )
        )

        self.assertEqual([chosen], player.clock)
        self.assertEqual(
            before.hand[:2] + before.hand[3:] + before.deck[:2],
            player.hand,
        )
        self.assertEqual(before.deck[2:], player.deck)
        self.assertEqual("clock", state.phase)
        self.assertTrue(state.clock_used)
        self.assertEqual(
            50,
            len({
                card.instance_id
                for card in (
                    player.hand
                    + player.deck
                    + player.waiting_room
                    + player.clock
                )
            }),
        )

        restored = Session.from_replay(
            json.loads(json.dumps(session.replay_data()))
        )
        self.assertEqual(state, restored.state)
        self.assertEqual(session.events, restored.events)

        for match in (session, restored):
            match.dispatch(
                AdvancePhaseAction(state.current_player)
            )

        self.assertEqual(session.state, restored.state)

    def test_invalid_operations_are_atomic(self):
        for case in (
            "phase",
            "opponent",
            "missing",
            "used",
            "full",
            "short_deck",
        ):
            session = at_clock()
            state = session.state
            player = state.players[state.current_player]
            actor = state.current_player
            cid = player.hand[0].instance_id

            if case == "phase":
                state.phase = "main"
            elif case == "opponent":
                actor = other(actor)
            elif case == "missing":
                cid = "missing"
            elif case == "used":
                session.dispatch(ClockAction(actor, cid))
                cid = player.hand[0].instance_id
            elif case == "full":
                player.clock = [
                    Card(
                        f"extra-{i}",
                        i,
                        definition=TEST_CARD,
                    )
                    for i in range(50)
                ]
            else:
                player.deck = player.deck[:1]

            before = deepcopy(session.__dict__)

            with self.subTest(case=case), self.assertRaises(ValueError):
                session.dispatch(
                    ClockAction(
                        actor,
                        cid,
                    )
                )

            self.assertEqual(before, session.__dict__)

    def test_skip_and_reset_on_next_turn(self):
        session = at_clock()
        player = session.state.players[session.state.current_player]
        before = deepcopy(player)

        session.dispatch(
            AdvancePhaseAction(session.state.current_player)
        )

        self.assertEqual(before, player)

        while session.state.phase != "clock":
            session.dispatch(
                AdvancePhaseAction(session.state.current_player)
            )

        player = session.state.players[session.state.current_player]

        session.dispatch(
            ClockAction(
                session.state.current_player,
                player.hand[0].instance_id,
            )
        )

        while session.state.phase != "stand":
            session.dispatch(
                AdvancePhaseAction(session.state.current_player)
            )

        self.assertFalse(session.state.clock_used)

    def test_version_two_replay(self):
        session = Session(42)

        from actions import MulliganAction

        hashes = [
            state_hash(
                session.state,
                version=2,
            )
        ]

        for _ in range(2):
            session.dispatch(
                MulliganAction(
                    session.state.actor,
                    (),
                )
            )
            hashes.append(
                state_hash(
                    session.state,
                    version=2,
                )
            )

        for _ in range(4):
            session.dispatch(
                AdvancePhaseAction(
                    session.state.current_player,
                )
            )
            hashes.append(
                state_hash(
                    session.state,
                    version=2,
                )
            )

        data = session.replay_data()

        # V2 did not contain deck-selection information.
        data["config"].pop("decks")

        data.update(
            version=2,
            state_hashes=hashes,
        )

        self.assertEqual(
            session.state,
            Session.from_replay(data).state,
        )


if __name__ == "__main__":
    unittest.main()
