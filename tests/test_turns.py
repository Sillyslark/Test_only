from copy import deepcopy
import json
import unittest
from tests.helpers import opened
from actions import AdvancePhaseAction, MulliganAction, StartGameAction
from application import Application
from engine import Session, VERSION, other, state_hash
from phases import PHASES



class TurnTests(unittest.TestCase):
    def test_two_complete_turns_and_draw_order(self):
        session = opened()
        state = session.state
        first = state.first_player
        self.assertEqual((first, 1, 'stand'), (state.current_player, state.turn_number, state.phase))
        for side in (first, other(first)):
            player = state.players[side]
            before = deepcopy(player)
            for phase in PHASES[1:]:
                session.dispatch(AdvancePhaseAction(side))
                self.assertEqual(phase, state.phase)
                self.assertEqual(before.hand + before.deck[:1], player.hand)
                self.assertEqual(before.deck[1:], player.deck)
                self.assertEqual(before.waiting_room, player.waiting_room)
                self.assertEqual(50, len(player.hand + player.deck + player.waiting_room))
            session.dispatch(AdvancePhaseAction(side))
            self.assertEqual((other(side), 'stand'), (state.current_player, state.phase))
        self.assertEqual(3, state.turn_number)
        self.assertEqual(first, state.current_player)
        self.assertEqual(2, sum(e['kind'] == 'card_drawn' for e in session.events))

    def test_illegal_phase_actions_leave_everything_unchanged(self):
        session = Session(42)
        before = deepcopy(session.__dict__)
        with self.assertRaises(ValueError):
            session.dispatch(AdvancePhaseAction(session.state.first_player))
        self.assertEqual(before, session.__dict__)
        session = opened()
        before = deepcopy(session.__dict__)
        with self.assertRaises(ValueError):
            session.dispatch(AdvancePhaseAction(other(session.state.current_player)))
        self.assertEqual(before, session.__dict__)
        session.state.players[session.state.current_player].deck.clear()
        before = deepcopy(session.__dict__)
        with self.assertRaises(ValueError):
            session.dispatch(AdvancePhaseAction(session.state.current_player))
        self.assertEqual(before, session.__dict__)

    def test_turn_replay_resume_and_application_boundary(self):
        app = Application()
        view = app.dispatch(StartGameAction(42))
        for _ in range(2):
            view = app.dispatch(MulliganAction(view.state.actor, ()))
        view = app.dispatch(AdvancePhaseAction(view.state.current_player))
        self.assertEqual('draw', view.state.phase)
        session = opened()
        for _ in range(9):
            session.dispatch(AdvancePhaseAction(session.state.current_player))
        replay = json.loads(json.dumps(session.replay_data()))
        restored = Session.from_replay(replay)
        for match in (session, restored):
            match.dispatch(AdvancePhaseAction(match.state.current_player))
        self.assertEqual(session.state, restored.state)
        self.assertEqual(session.events, restored.events)
        self.assertEqual(session.replay_data(), restored.replay_data())

    def test_version_one_replay_migrates_to_first_turn(self):
        session = Session(42)
        hashes = [state_hash(session.state, legacy=True)]
        for _ in range(2):
            session.dispatch(MulliganAction(session.state.actor, ()))
            hashes.append(state_hash(session.state, legacy=True))
        data = session.replay_data()

        # V1 predates selectable decks.
        data["config"].pop("decks")

        data["version"] = 1
        data["state_hashes"] = hashes

        for action in data["actions"]:
            del action["kind"]
        restored = Session.from_replay(data)
        self.assertEqual(session.state, restored.state)
        self.assertEqual(
            VERSION,
            restored.replay_data()["version"],
        )

if __name__ == '__main__':
    unittest.main()
