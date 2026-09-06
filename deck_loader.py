"""Load deck recipes and build match card instances."""

from pathlib import Path
import json

from cards import Card, load_card_definition


ROOT = Path(__file__).resolve().parent
CARD_ROOT = ROOT / "card"
DECK_ROOT = ROOT / "deck"


def load_deck_recipe(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_deck(deck_path: Path, player_id: str) -> list[Card]:
    recipe = load_deck_recipe(deck_path)

    definitions = []

    for entry in recipe["cards"]:
        definition = load_card_definition(
            CARD_ROOT / entry["card"]
        )

        definitions.extend(
            [definition] * entry["count"]
        )

    if len(definitions) != 50:
        raise ValueError("卡组必须正好包含 50 张牌")

    return [
        Card(
            instance_id=f"{player_id}-{number:02}",
            number=number,
            definition=definition,
        )
        for number, definition in enumerate(
            definitions,
            start=1,
        )
    ]


TEST_ALL_T_001 = (
    DECK_ROOT
    / "TEST"
    / "Test_All_T_001.json"
)