import unittest
from card_loader import load_card

class CardInformationBoundaryTests(unittest.TestCase):
    def test_character_fields(self):
        c = load_card("TEST/T-001.json")
        for name in ("level","cost","power","soul","traits","card_icons","trigger_icons"):
            self.assertTrue(hasattr(c, name), name)

    def test_event_fields(self):
        c = load_card("TEST/T-003.json")
        for name in ("level","cost","card_icons","trigger_icons"):
            self.assertTrue(hasattr(c, name), name)
        for name in ("power","soul","traits"):
            self.assertFalse(hasattr(c, name), name)

    def test_climax_fields(self):
        c = load_card("TEST/T-002.json")
        self.assertTrue(hasattr(c, "trigger_icons"))
        for name in ("level","cost","power","soul","traits","card_icons"):
            self.assertFalse(hasattr(c, name), name)

if __name__ == "__main__": unittest.main()
