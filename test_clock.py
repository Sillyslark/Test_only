from copy import deepcopy
import json
import unittest

from actions import AdvancePhaseAction, ClockAction
from engine import Card, Session, other, state_hash
from test_turns import opened
from ui.zones import clock_slots


def at_clock():
    session = opened()
    for _ in range(2):
        session.dispatch(AdvancePhaseAction(session.state.current_player))
    return session


class ClockTests(unittest.TestCase):
    def test_clock_moves_to_top_and_draws_two_in_order(self):
        session = at_clock()
        state = session.state
        player = state.players[state.current_player]
        before = deepcopy(player)
        chosen = player.hand[2]
        session.dispatch(ClockAction(state.current_player, chosen.instance_id))
        self.assertEqual([chosen], player.clock)
        self.assertEqual(before.hand[:2] + before.hand[3:] + before.deck[:2], player.hand)
        self.assertEqual(before.deck[2:], player.deck)
        self.assertEqual('clock', state.phase)
        self.assertTrue(state.clock_used)
        self.assertEqual(50, len({c.instance_id for c in player.hand + player.deck + player.control_room + player.clock}))
        restored = Session.from_replay(json.loads(json.dumps(session.replay_data())))
        self.assertEqual(state, restored.state)
        self.assertEqual(session.events, restored.events)
        for match in (session, restored):
            match.dispatch(AdvancePhaseAction(state.current_player))
        self.assertEqual(session.state, restored.state)

    def test_invalid_operations_are_atomic(self):
        for case in ('phase', 'opponent', 'missing', 'used', 'full', 'short_deck'):
            session = at_clock()
            state = session.state
            player = state.players[state.current_player]
            actor, cid = state.current_player, player.hand[0].instance_id
            if case == 'phase':
                state.phase = 'main'
            elif case == 'opponent':
                actor = other(actor)
            elif case == 'missing':
                cid = 'missing'
            elif case == 'used':
                session.dispatch(ClockAction(actor, cid))
                cid = player.hand[0].instance_id
            elif case == 'full':
                player.clock = [Card(f'extra-{i}', i) for i in range(50)]
            else:
                player.deck = player.deck[:1]
            before = deepcopy(session.__dict__)
            with self.subTest(case=case), self.assertRaises(ValueError):
                session.dispatch(ClockAction(actor, cid))
            self.assertEqual(before, session.__dict__)

    def test_skip_and_reset_on_next_turn(self):
        session = at_clock()
        player = session.state.players[session.state.current_player]
        before = deepcopy(player)
        session.dispatch(AdvancePhaseAction(session.state.current_player))
        self.assertEqual(before, player)
        while session.state.phase != 'clock':
            session.dispatch(AdvancePhaseAction(session.state.current_player))
        player = session.state.players[session.state.current_player]
        session.dispatch(ClockAction(session.state.current_player, player.hand[0].instance_id))
        while session.state.phase != 'stand':
            session.dispatch(AdvancePhaseAction(session.state.current_player))
        self.assertFalse(session.state.clock_used)

    def test_bottom_six_keep_top_based_positions(self):
        cards = [Card(str(i), i) for i in range(50)]
        self.assertEqual([None] * 6, clock_slots([]))
        self.assertEqual([(1, cards[0])] + [None] * 5, clock_slots(cards[:1]))
        self.assertEqual(list(reversed(list(enumerate(cards, 1))))[:6], clock_slots(cards))
        self.assertEqual([50, 49, 48, 47, 46, 45], [slot[0] for slot in clock_slots(cards)])

    def test_version_two_replay(self):
        session = opened()
        # Generate an independent version-2-compatible trace from the initial state.
        session = Session(42)
        from actions import MulliganAction
        hashes = [state_hash(session.state, version=2)]
        for _ in range(2):
            session.dispatch(MulliganAction(session.state.actor, ()))
            hashes.append(state_hash(session.state, version=2))
        for _ in range(4):
            session.dispatch(AdvancePhaseAction(session.state.current_player))
            hashes.append(state_hash(session.state, version=2))
        data = session.replay_data()
        data.update(version=2, state_hashes=hashes)
        self.assertEqual(session.state, Session.from_replay(data).state)


if __name__ == '__main__':
    unittest.main()
