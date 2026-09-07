import copy
import json
import unittest

from engine import Session, MulliganAction, PLAYERS, other, state_hash


class OpeningTests(unittest.TestCase):
    def test_setup_and_shuffle(self):
        a, b = Session(42), Session(42)
        self.assertEqual(a.state, b.state)
        self.assertNotEqual(a.state.players, Session(43).state.players)
        for player in a.state.players.values():
            self.assertEqual((5, 45, 0), (len(player.hand), len(player.deck), len(player.waiting_room)))
            self.assertEqual(list(range(1, 51)), sorted(c.number for c in player.hand + player.deck))
        self.assertEqual({"P1", "P2"}, {Session(seed).state.first_player for seed in range(30)})

    def test_mulligan_order_and_conservation(self):
        session = Session(12)
        first = session.state.actor
        player = session.state.players[first]
        hand, deck = list(player.hand), list(player.deck)
        session.dispatch(MulliganAction(first, (hand[3].instance_id, hand[1].instance_id)))
        self.assertEqual([hand[1], hand[3]], player.waiting_room)
        self.assertEqual([hand[0], hand[2], hand[4]] + deck[:2], player.hand)
        self.assertEqual(deck[2:], player.deck)
        self.assertEqual(other(first), session.state.actor)
        second = session.state.actor
        session.dispatch(MulliganAction(second, tuple(c.instance_id for c in session.state.players[second].hand)))
        self.assertIsNone(session.state.actor)
        for player in session.state.players.values():
            cards = player.hand + player.deck + player.waiting_room
            self.assertEqual(50, len({c.instance_id for c in cards}))
            self.assertEqual(list(range(1, 51)), sorted(c.number for c in cards))
            self.assertEqual(5, len(player.hand))

    def test_invalid_actions_are_atomic(self):
        session = Session(5)
        actor = session.state.actor
        cid = session.state.players[actor].hand[0].instance_id
        for action in (MulliganAction(other(actor), ()), MulliganAction(actor, (cid, cid)), MulliganAction(actor, ("missing",))):
            before = copy.deepcopy((session.state, session.events, session.replay_data()))
            with self.assertRaises(ValueError):
                session.dispatch(action)
            self.assertEqual(before, (session.state, session.events, session.replay_data()))

    def test_replay_and_resume(self):
        session = Session(2026)
        session.dispatch(MulliganAction(session.state.actor, ()))
        restored = Session.from_replay(json.loads(json.dumps(session.replay_data())))
        actor = restored.state.actor
        action = MulliganAction(actor, tuple(c.instance_id for c in restored.state.players[actor].hand))
        for match in (session, restored):
            match.dispatch(action)
        self.assertEqual(session.state, restored.state)
        self.assertEqual(session.events, restored.events)
        self.assertEqual(session.state, Session.from_replay(session.replay_data()).state)
        with self.assertRaises(ValueError):
            restored.dispatch(action)
        data = session.replay_data()
        data["state_hashes"][-1] = "tampered"
        with self.assertRaises(ValueError):
            Session.from_replay(data)


if __name__ == "__main__":
    unittest.main()
