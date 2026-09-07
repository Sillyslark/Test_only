import json
from pathlib import Path
import tempfile
import unittest

from cards import CardDefinition
from deck_loader import (
    TEST_ALL_T_001,
    build_deck,
    load_deck,
    load_deck_definitions,
    load_deck_recipe,
    validate_deck,
)


class DeckLoaderTests(unittest.TestCase):
    def test_existing_test_deck_recipe_loads(self):
        recipe = load_deck("TEST/Test_All_T_001.json")

        self.assertEqual(
            "Test_All_T_001",
            recipe["name"],
        )
        self.assertEqual(
            [
                {
                    "card": "TEST/T-001.json",
                    "count": 50,
                }
            ],
            recipe["cards"],
        )

    def test_existing_test_deck_expands_to_50_t001_definitions(self):
        recipe, definitions = load_deck_definitions(
            TEST_ALL_T_001
        )

        self.assertEqual(
            "Test_All_T_001",
            recipe["name"],
        )
        self.assertEqual(50, len(definitions))
        self.assertTrue(
            all(
                isinstance(definition, CardDefinition)
                for definition in definitions
            )
        )
        self.assertTrue(
            all(
                definition.code == "T-001"
                for definition in definitions
            )
        )

    def test_build_deck_creates_unique_match_instances(self):
        cards = build_deck(
            TEST_ALL_T_001,
            "P1",
        )

        self.assertEqual(50, len(cards))
        self.assertEqual(
            list(range(1, 51)),
            [card.number for card in cards],
        )
        self.assertEqual(
            50,
            len({card.instance_id for card in cards}),
        )
        self.assertEqual(
            "P1-01",
            cards[0].instance_id,
        )
        self.assertEqual(
            "P1-50",
            cards[-1].instance_id,
        )
        self.assertTrue(
            all(
                card.definition.code == "T-001"
                for card in cards
            )
        )

    def test_two_players_receive_distinct_instance_ids(self):
        p1 = build_deck(
            TEST_ALL_T_001,
            "P1",
        )
        p2 = build_deck(
            TEST_ALL_T_001,
            "P2",
        )

        self.assertTrue(
            {card.instance_id for card in p1}.isdisjoint(
                {card.instance_id for card in p2}
            )
        )

    def test_validate_deck_rejects_wrong_total(self):
        _, definitions = load_deck_definitions(
            TEST_ALL_T_001
        )

        with self.assertRaises(ValueError):
            validate_deck(definitions[:-1])

        with self.assertRaises(ValueError):
            validate_deck(definitions + [definitions[0]])

    def test_count_must_be_positive_integer(self):
        for bad_count in (0, -1, 1.5, "50", True):
            recipe = {
                "name": "bad",
                "cards": [
                    {
                        "card": "TEST/T-001.json",
                        "count": bad_count,
                    }
                ],
            }

            with self.subTest(count=bad_count), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bad.json"
                path.write_text(
                    json.dumps(
                        recipe,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                with self.assertRaises(ValueError):
                    load_deck_definitions(path)

    def test_missing_card_file_fails_during_loading(self):
        recipe = {
            "name": "missing-card",
            "cards": [
                {
                    "card": "TEST/DOES-NOT-EXIST.json",
                    "count": 50,
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            path.write_text(
                json.dumps(
                    recipe,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(FileNotFoundError):
                load_deck_definitions(path)

    def test_malformed_recipe_is_rejected_before_building_cards(self):
        cases = (
            {},
            {"name": "bad", "cards": "not-a-list"},
            {"name": "bad", "cards": [42]},
            {"name": "bad", "cards": [{"count": 50}]},
            {"name": "bad", "cards": [{"card": "TEST/T-001.json"}]},
            {"name": "bad", "cards": [{"card": "", "count": 50}]},
        )

        for recipe in cases:
            with self.subTest(recipe=recipe), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bad.json"
                path.write_text(
                    json.dumps(
                        recipe,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                with self.assertRaises(ValueError):
                    load_deck_definitions(path)


if __name__ == "__main__":
    unittest.main()
