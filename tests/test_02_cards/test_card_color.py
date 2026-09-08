import unittest
from cards import CardColor, load_card

class CardColorTests(unittest.TestCase):
    def test_test_cards_load_typed_color(self):
        for filename in ("T-001.json","T-002.json","T-003.json"):
            with self.subTest(filename=filename):
                self.assertIs(load_card(f"TEST/{filename}").color, CardColor.YELLOW)

    def test_supported_colors_are_explicit(self):
        self.assertEqual({"yellow","green","red","blue"}, {c.value for c in CardColor})

if __name__ == "__main__": unittest.main()
