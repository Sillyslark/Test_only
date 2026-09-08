"""Card JSON loading helpers.

Concrete card data lives under cards/**/*.json. This module owns filesystem
resolution, JSON parsing, validation, and JSON -> CardDefinition construction.
"""
from pathlib import Path
import json

from card_definition import (
    CardColor,
    CardDefinition,
    CardIcon,
    CardType,
    CharacterDefinition,
    ClimaxDefinition,
    EventDefinition,
    TriggerIcon,
)


CARD_ROOT = Path(__file__).resolve().parent / "cards"


def _enum_value(enum_type, raw, field_name):
    try:
        return enum_type(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"未知 {field_name}: {raw}") from exc


def _tuple_enum(data, key, enum_type):
    raw = data.get(key, [])
    if not isinstance(raw, list):
        raise ValueError(f"{key} 必须是列表")
    return tuple(_enum_value(enum_type, item, key) for item in raw)


def load_card_definition(path: Path | str) -> CardDefinition:
    """Load one concrete CardDefinition from the current card JSON schema."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    card_type = _enum_value(CardType, data["card_type"], "card_type")
    color = _enum_value(CardColor, data["color"], "color")
    common = dict(
        card_number=data["card_number"],
        name=data["name"],
        color=color,
        trigger_icons=_tuple_enum(data, "trigger_icons", TriggerIcon),
    )

    if card_type is CardType.CHARACTER:
        return CharacterDefinition(
            **common,
            level=data["level"],
            cost=data["cost"],
            power=data["power"],
            soul=data["soul"],
            traits=tuple(data.get("traits", [])),
            card_icons=_tuple_enum(data, "card_icons", CardIcon),
        )
    if card_type is CardType.EVENT:
        return EventDefinition(
            **common,
            level=data["level"],
            cost=data["cost"],
            card_icons=_tuple_enum(data, "card_icons", CardIcon),
        )
    if card_type is CardType.CLIMAX:
        return ClimaxDefinition(**common)
    raise AssertionError("unreachable CardType")


def load_card(relative_path: Path | str) -> CardDefinition:
    """Load one card by a path relative to the project's cards/ directory."""
    relative_path = Path(relative_path)
    if relative_path.is_absolute():
        raise ValueError("卡片路径必须相对于 cards/ 目录")
    root = CARD_ROOT.resolve()
    resolved = (CARD_ROOT / relative_path).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("卡片路径不能离开 cards/ 目录")
    return load_card_definition(resolved)
