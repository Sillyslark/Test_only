import unittest
from cards import CardDefinition, CharacterDefinition, EventDefinition, ClimaxDefinition, load_card

class CardDefinitionTests(unittest.TestCase):
    def test_three_test_cards_use_common_base(self):
        cases = (("T-001.json", CharacterDefinition), ("T-002.json", ClimaxDefinition), ("T-003.json", EventDefinition))
        for filename, expected in cases:
            with self.subTest(filename=filename):
                card = load_card(f"TEST/{filename}")
                self.assertIsInstance(card, CardDefinition)
                self.assertIsInstance(card, expected)

if __name__ == "__main__": unittest.main()
