import json
from pathlib import Path
import tempfile
import unittest

from card_definition import (
    CardDefinition,
    CharacterDefinition,
    ClimaxDefinition,
)
from card_loader import (
    CARD_ROOT,
    load_card,
    load_card_definition,
)


class CardLoadingTests(unittest.TestCase):
    def test_t001_loads_from_json(self):
        definition = load_card("TEST/T-001.json")

        self.assertIsInstance(definition, CardDefinition)
        self.assertIsInstance(definition, CharacterDefinition)
        self.assertEqual("T-001", definition.code)
        self.assertEqual("测试", definition.name)
        self.assertEqual("character", definition.kind)
        self.assertEqual("yellow", definition.color)
        self.assertEqual(0, definition.level)
        self.assertEqual(0, definition.cost)
        self.assertEqual(500, definition.power)
        self.assertEqual(1, definition.soul)
        self.assertEqual((), definition.traits)
        self.assertEqual((), definition.trigger_marks)

    def test_t002_climax_loads_from_json(self):
        definition = load_card("TEST/T-002.json")

        self.assertIsInstance(definition, ClimaxDefinition)
        self.assertEqual("T-002", definition.code)
        self.assertEqual("测试CX", definition.name)
        self.assertEqual("climax", definition.kind)
        self.assertEqual("yellow", definition.color)
        self.assertEqual((), definition.trigger_marks)

    def test_t002_has_no_character_only_fields(self):
        definition = load_card("TEST/T-002.json")

        for field_name in ("level", "cost", "power", "soul", "traits"):
            with self.subTest(field=field_name):
                self.assertFalse(hasattr(definition, field_name))

    def test_same_json_loads_to_equal_definition(self):
        a = load_card("TEST/T-001.json")
        b = load_card("TEST/T-001.json")
        self.assertEqual(a, b)
        self.assertIsNot(a, b)

    def test_same_climax_json_loads_to_equal_definition(self):
        a = load_card("TEST/T-002.json")
        b = load_card("TEST/T-002.json")
        self.assertEqual(a, b)
        self.assertIsNot(a, b)

    def test_load_card_uses_card_root(self):
        direct = load_card_definition(CARD_ROOT / "TEST" / "T-001.json")
        relative = load_card("TEST/T-001.json")
        self.assertEqual(direct, relative)

    def test_missing_required_character_field_is_rejected(self):
        data = {
            "card_number": "BROKEN",
            "name": "broken",
            "card_type": "character",
            "color": "yellow",
            "level": 0,
            "cost": 0,
            "power": 500,
            "traits": [],
            "trigger_icons": [],
            "card_icons": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(KeyError):
                load_card_definition(path)

    def test_missing_required_climax_field_is_rejected(self):
        data = {
            "card_number": "BROKEN-CX",
            "name": "broken cx",
            "card_type": "climax",
            "trigger_icons": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken-cx.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(KeyError):
                load_card_definition(path)

    def test_unknown_card_type_is_rejected(self):
        data = {
            "card_number": "UNKNOWN",
            "name": "unknown",
            "card_type": "unknown",
            "color": "yellow",
            "trigger_icons": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unknown.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_card_definition(path)


if __name__ == "__main__":
    unittest.main()
