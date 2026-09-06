import tempfile
from pathlib import Path
import unittest

from actions import StartGameAction, MulliganAction, SaveReplayAction, LoadReplayAction
from application import Application


class ApplicationTests(unittest.TestCase):
    def test_snapshot_cannot_change_match(self):
        app = Application()
        view = app.dispatch(StartGameAction(42))
        expected = app.snapshot()
        view.state.players['P1'].hand.clear()
        view.events[0]['seed'] = 999
        self.assertEqual(expected, app.snapshot())

    def test_action_save_load_and_failure_preserves_match(self):
        app = Application()
        view = app.dispatch(StartGameAction(12))
        actor = view.state.actor
        app.dispatch(MulliganAction(actor, (view.state.players[actor].hand[0].instance_id,)))
        expected = app.snapshot()
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / 'replay.json'
            app.dispatch(SaveReplayAction(str(path)))
            app.dispatch(StartGameAction(99))
            app.dispatch(LoadReplayAction(str(path)))
            self.assertEqual(expected, app.snapshot())
            path.write_text('{}', encoding='utf-8')
            with self.assertRaises(ValueError):
                app.dispatch(LoadReplayAction(str(path)))
            self.assertEqual(expected, app.snapshot())


if __name__ == '__main__':
    unittest.main()
