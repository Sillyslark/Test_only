"""Deck JSON loading, validation, and match-instance construction."""

from pathlib import Path
import json

from cards import Card, ClimaxDefinition, load_card


ROOT = Path(__file__).resolve().parent
DECK_ROOT = ROOT / "deck"

DEFAULT_TEST_DECK = "TEST/Test_All_T_001.json"
TEST_ALL_T_001 = DECK_ROOT / DEFAULT_TEST_DECK
TEST_42_T_001_8_T_002 = DECK_ROOT / "TEST/Test_42_T_001_8_T_002.json"


def resolve_deck_path(relative_path: Path | str) -> Path:
    relative_path = Path(relative_path)
    if relative_path.is_absolute():
        raise ValueError("卡组路径必须相对于 deck/ 目录")
    root = DECK_ROOT.resolve()
    resolved = (DECK_ROOT / relative_path).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("卡组路径不能离开 deck/ 目录")
    return resolved


def load_deck_recipe(path: Path | str) -> dict:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_deck(relative_path: Path | str) -> dict:
    return load_deck_recipe(resolve_deck_path(relative_path))


def load_deck_definitions(path: Path | str):
    recipe = load_deck_recipe(path)
    entries = recipe.get("cards")
    if not isinstance(entries, list):
        raise ValueError("卡组文件中的 cards 必须是列表")

    definitions = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("卡组条目必须是对象")
        if "card" not in entry or "count" not in entry:
            raise ValueError("卡组条目必须包含 card 和 count")

        card_path = entry["card"]
        count = entry["count"]

        if not isinstance(card_path, str) or not card_path:
            raise ValueError("card 必须是非空字符串")
        if type(count) is not int or count <= 0:
            raise ValueError("count 必须是正整数")

        definition = load_card(card_path)
        definitions.extend([definition] * count)

    return recipe, definitions


def validate_deck(definitions) -> None:
    """Current simulator deck rules: exactly 50 cards, at most 8 Climax."""
    if len(definitions) != 50:
        raise ValueError("卡组必须正好包含 50 张牌")

    climax_count = sum(
        isinstance(definition, ClimaxDefinition)
        for definition in definitions
    )
    if climax_count > 8:
        raise ValueError("卡组中的高潮卡不能超过 8 张")


def build_deck(deck_path: Path | str, player_id: str) -> list[Card]:
    _, definitions = load_deck_definitions(deck_path)
    validate_deck(definitions)

    return [
        Card(
            instance_id=f"{player_id}-{number:02}",
            number=number,
            definition=definition,
        )
        for number, definition in enumerate(definitions, start=1)
    ]
