import json
from pathlib import Path
import tempfile
import unittest

from card_definition import CardIcon, CardType, TriggerIcon
from card_loader import (
    CardJsonSyntaxError,
    CardSchemaError,
    DuplicateCardFieldError,
    InvalidCardValueError,
    load_card,
    load_card_definition,
)


class CardLoaderTests(unittest.TestCase):
    def _load_data(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "card.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return load_card_definition(path)

    def test_test_folder_covers_all_three_card_types(self):
        cards = [load_card(f"TEST/T-00{i}.json") for i in (1, 2, 3)]
        self.assertEqual(
            {CardType.CHARACTER, CardType.CLIMAX, CardType.EVENT},
            {card.card_type for card in cards},
        )

    def test_object_field_order_has_no_meaning(self):
        data = {
            "trigger_icons": [],
            "card_icons": [],
            "traits": [],
            "soul": 1,
            "power": 500,
            "cost": 0,
            "level": 0,
            "color": "yellow",
            "name": "测试",
            "card_number": "ORDER",
            "card_type": "character",
        }
        card = self._load_data(data)
        self.assertEqual("ORDER", card.card_number)
        self.assertIs(CardType.CHARACTER, card.card_type)

    def test_duplicate_json_field_is_rejected_before_dict_loss(self):
        raw = """{
          "card_number": "DUP",
          "name": "dup",
          "card_type": "climax",
          "color": "yellow",
          "trigger_icons": [],
          "card_number": "DUP-2"
        }"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(DuplicateCardFieldError) as ctx:
                load_card_definition(path)
            self.assertIn("card_number", str(ctx.exception))
            self.assertIn(str(path), str(ctx.exception))

    def test_missing_and_unexpected_fields_are_reported_together(self):
        data = {
            "card_number": "SCHEMA",
            "name": "schema",
            "card_type": "character",
            "color": "yellow",
            "level": 0,
            "cost": 0,
            "soul": 1,
            "traits": [],
            "card_icons": [],
            "trigger_icons": [],
            "unexpected": 123,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "schema.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(CardSchemaError) as ctx:
                load_card_definition(path)
            self.assertEqual(("power",), ctx.exception.missing_fields)
            self.assertEqual(("unexpected",), ctx.exception.unexpected_fields)
            self.assertIn("card_number: SCHEMA", str(ctx.exception))

    def test_climax_rejects_character_only_fields(self):
        data = {
            "card_number": "BAD-CX",
            "name": "bad cx",
            "card_type": "climax",
            "color": "yellow",
            "trigger_icons": [],
            "power": 1000,
        }
        with self.assertRaises(CardSchemaError) as ctx:
            self._load_data(data)
        self.assertEqual(("power",), ctx.exception.unexpected_fields)

    def test_missing_card_type_is_reported_precisely(self):
        data = {
            "card_number": "NO-TYPE",
            "name": "no type",
            "color": "yellow",
            "trigger_icons": [],
        }
        with self.assertRaises(CardSchemaError) as ctx:
            self._load_data(data)
        self.assertEqual(("card_type",), ctx.exception.missing_fields)

    def test_invalid_card_type_reports_legal_values(self):
        data = {
            "card_number": "BAD-TYPE",
            "name": "bad type",
            "card_type": "monster",
            "color": "yellow",
            "trigger_icons": [],
        }
        with self.assertRaises(InvalidCardValueError) as ctx:
            self._load_data(data)
        message = str(ctx.exception)
        for value in ("character", "event", "climax"):
            self.assertIn(value, message)

    def test_wrong_value_type_is_reported_precisely(self):
        data = {
            "card_number": "BAD-LEVEL",
            "name": "bad level",
            "card_type": "character",
            "color": "yellow",
            "level": "0",
            "cost": 0,
            "power": 500,
            "soul": 1,
            "traits": [],
            "card_icons": [],
            "trigger_icons": [],
        }
        with self.assertRaises(InvalidCardValueError) as ctx:
            self._load_data(data)
        message = str(ctx.exception)
        self.assertIn('字段 "level"', message)
        self.assertIn("期望 int", message)
        self.assertIn("实际 str", message)

    def test_bool_is_not_accepted_as_int(self):
        data = {
            "card_number": "BOOL-LEVEL",
            "name": "bool level",
            "card_type": "character",
            "color": "yellow",
            "level": True,
            "cost": 0,
            "power": 500,
            "soul": 1,
            "traits": [],
            "card_icons": [],
            "trigger_icons": [],
        }
        with self.assertRaises(InvalidCardValueError):
            self._load_data(data)

    def test_trigger_icon_list_preserves_order_and_duplicates(self):
        data = {
            "card_number": "TRIGGER-ORDER",
            "name": "trigger order",
            "card_type": "climax",
            "color": "yellow",
            "trigger_icons": ["soul", "shot", "soul"],
        }
        card = self._load_data(data)
        self.assertEqual(
            (TriggerIcon.SOUL, TriggerIcon.SHOT, TriggerIcon.SOUL),
            card.trigger_icons,
        )

    def test_card_icon_list_preserves_order(self):
        data = {
            "card_number": "ICON-ORDER",
            "name": "icon order",
            "card_type": "event",
            "color": "yellow",
            "level": 0,
            "cost": 0,
            "card_icons": ["counter", "clock"],
            "trigger_icons": [],
        }
        card = self._load_data(data)
        self.assertEqual((CardIcon.COUNTER, CardIcon.CLOCK), card.card_icons)

    def test_json_syntax_error_has_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-json.json"
            path.write_text('{"card_number": "BAD",', encoding="utf-8")
            with self.assertRaises(CardJsonSyntaxError) as ctx:
                load_card_definition(path)
            message = str(ctx.exception)
            self.assertIn(str(path), message)
            self.assertIn("line", message)
            self.assertIn("column", message)


if __name__ == "__main__":
    unittest.main()
