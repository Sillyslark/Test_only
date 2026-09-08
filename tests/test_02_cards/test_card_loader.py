import unittest
from cards import CardType, load_card

class CardLoaderTests(unittest.TestCase):
    def test_test_folder_covers_all_three_card_types(self):
        cards = [load_card(f"TEST/T-00{i}.json") for i in (1,2,3)]
        self.assertEqual({CardType.CHARACTER, CardType.CLIMAX, CardType.EVENT}, {c.card_type for c in cards})

    def test_card_number_migrates_from_test_json_code(self):
        self.assertEqual("T-001", load_card("TEST/T-001.json").card_number)
        self.assertEqual("T-002", load_card("TEST/T-002.json").card_number)
        self.assertEqual("T-003", load_card("TEST/T-003.json").card_number)

if __name__ == "__main__": unittest.main()
