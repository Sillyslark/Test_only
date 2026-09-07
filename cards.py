"""Card data models and JSON loading helpers.

Concrete cards live under card/**/*.json. This module defines the supported
card-definition shapes and converts JSON data into typed definitions. It does
not register any specific card such as T-001 or T-002.
"""

from dataclasses import dataclass
from pathlib import Path
import json
from typing import TypeAlias


CARD_ROOT = Path(__file__).resolve().parent / "card"


@dataclass(frozen=True)
class CharacterDefinition:
    level: int
    cost: int
    trigger_marks: tuple[str, ...]
    power: int
    soul: int
    name: str
    color: str
    traits: tuple[str, ...]
    code: str
    kind: str = "character"

@dataclass(frozen=True)
class ClimaxDefinition:
    name: str
    color: str
    code: str
    trigger_marks: tuple[str, ...]
    kind: str = "climax"

# Backward-compatible alias: existing imports that refer to CardDefinition
# currently mean the character-card definition shape.
CardDefinition = CharacterDefinition

AnyCardDefinition: TypeAlias = CharacterDefinition | ClimaxDefinition


@dataclass(frozen=True)
class Card:
    instance_id: str
    number: int  # Debug copy number, distinct from definition.code.
    definition: AnyCardDefinition
    face_up: bool = True


def load_card_definition(path: Path | str) -> AnyCardDefinition:
    """Load one concrete card definition from a JSON file."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    kind = data["kind"]

    if kind == "character":
        return CharacterDefinition(
            level=data["level"],
            cost=data["cost"],
            trigger_marks=tuple(data.get("trigger_marks", [])),
            power=data["power"],
            soul=data["soul"],
            name=data["name"],
            color=data["color"],
            traits=tuple(data.get("traits", [])),
            code=data["code"],
            kind="character",
        )

    if kind == "climax":
        return ClimaxDefinition(
            name=data["name"],
            color=data["color"],
            code=data["code"],
            trigger_marks=tuple(data.get("trigger_marks", [])),
            kind="climax",
        )

    raise ValueError(f"未知卡牌种类: {kind}")


def load_card(relative_path: Path | str) -> AnyCardDefinition:
    """Load one card by a path relative to the project's ``card/`` directory.

    Example:
        load_card("TEST/T-001.json")
        load_card("TEST/T-002.json")
    """
    return load_card_definition(CARD_ROOT / relative_path)
