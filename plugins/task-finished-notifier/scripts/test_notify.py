import io
import unittest
from unittest.mock import patch
import notify


class NotificationTests(unittest.TestCase):
    def test_only_main_stop(self):
        self.assertTrue(notify.should_notify({'hook_event_name': 'Stop'}))
        self.assertFalse(notify.should_notify({'hook_event_name': 'SubagentStop'}))
        self.assertFalse(notify.should_notify({'hook_event_name': 'Stop', 'agent_id': 'child'}))
        self.assertFalse(notify.should_notify([]))

    def test_hook_json_and_malformed_input(self):
        for raw, count in [('{"hook_event_name":"Stop"}', 1), ('bad json', 0)]:
            with patch('sys.argv', ['notify.py']), patch('sys.stdin', io.StringIO(raw)), \
                    patch('sys.stdout', new_callable=io.StringIO) as out, \
                    patch('sys.stderr', new_callable=io.StringIO), \
                    patch.object(notify, 'launch_popup') as launch:
                notify.main()
                self.assertEqual(count, launch.call_count)
                self.assertEqual('{}', out.getvalue().strip())


if __name__ == '__main__':
    unittest.main()
