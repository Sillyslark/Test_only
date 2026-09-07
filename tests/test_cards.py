import json
from pathlib import Path
import tempfile
import unittest

from cards import (
    CARD_ROOT,
    CardDefinition,
    load_card,
    load_card_definition,
)


class CardLoadingTests(unittest.TestCase):
    def test_t001_loads_from_json(self):
        definition = load_card("TEST/T-001.json")

        self.assertIsInstance(definition, CardDefinition)
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

    def test_same_json_loads_to_equal_definition(self):
        a = load_card("TEST/T-001.json")
        b = load_card("TEST/T-001.json")

        self.assertEqual(a, b)
        self.assertIsNot(a, b)

    def test_load_card_uses_card_root(self):
        direct = load_card_definition(
            CARD_ROOT / "TEST" / "T-001.json"
        )
        relative = load_card("TEST/T-001.json")

        self.assertEqual(direct, relative)

    def test_missing_required_field_is_rejected(self):
        data = {
            "code": "BROKEN",
            "name": "broken",
            "kind": "character",
            "color": "yellow",
            "level": 0,
            "cost": 0,
            "power": 500,
            "traits": [],
            "trigger_marks": [],
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False),
                encoding="utf-8",
            )

            with self.assertRaises(KeyError):
                load_card_definition(path)


if __name__ == "__main__":
    unittest.main()
