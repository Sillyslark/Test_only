import unittest
from cards import CardIcon, load_card

class CardIconTests(unittest.TestCase):
    def test_character_and_event_have_empty_card_icons_in_test_data(self):
        self.assertEqual((), load_card("TEST/T-001.json").card_icons)
        self.assertEqual((), load_card("TEST/T-003.json").card_icons)

    def test_climax_has_no_card_icons_information(self):
        self.assertFalse(hasattr(load_card("TEST/T-002.json"), "card_icons"))

    def test_current_icon_enum(self):
        self.assertEqual({CardIcon.COUNTER, CardIcon.CLOCK}, set(CardIcon))

if __name__ == "__main__": unittest.main()
