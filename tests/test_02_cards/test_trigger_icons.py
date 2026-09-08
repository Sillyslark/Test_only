import unittest
from dataclasses import FrozenInstanceError
from card_definition import TriggerIcon
from card_loader import load_card

class TriggerIconTests(unittest.TestCase):
    def test_test_cards_can_have_empty_trigger_icons(self):
        for filename in ("T-001.json","T-002.json","T-003.json"):
            self.assertEqual((), load_card(f"TEST/{filename}").trigger_icons)

    def test_definition_is_frozen(self):
        c = load_card("TEST/T-001.json")
        with self.assertRaises(FrozenInstanceError):
            c.trigger_icons = (TriggerIcon.SOUL,)

if __name__ == "__main__": unittest.main()
