import json
from pathlib import Path
import tempfile
import unittest

from card_definition import CardType
from card_loader import load_card, load_card_definition


class CardLoaderTests(unittest.TestCase):
    def test_test_folder_covers_all_three_card_types(self):
        cards = [load_card(f"TEST/T-00{i}.json") for i in (1, 2, 3)]
        self.assertEqual(
            {CardType.CHARACTER, CardType.CLIMAX, CardType.EVENT},
            {card.card_type for card in cards},
        )

    def test_card_number_loads_from_current_schema(self):
        self.assertEqual("T-001", load_card("TEST/T-001.json").card_number)
        self.assertEqual("T-002", load_card("TEST/T-002.json").card_number)
        self.assertEqual("T-003", load_card("TEST/T-003.json").card_number)

    def test_legacy_card_type_key_is_rejected(self):
        data = {
            "card_number": "BROKEN",
            "name": "broken",
            "kind": "character",
            "color": "yellow",
            "level": 0,
            "cost": 0,
            "power": 500,
            "soul": 1,
            "traits": [],
            "card_icons": [],
            "trigger_icons": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(KeyError):
                load_card_definition(path)

    def test_legacy_card_number_key_is_rejected(self):
        data = {
            "code": "BROKEN",
            "name": "broken",
            "card_type": "climax",
            "color": "yellow",
            "trigger_icons": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(KeyError):
                load_card_definition(path)


if __name__ == "__main__":
    unittest.main()
