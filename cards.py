"""Card data models and JSON loading helpers.

Concrete cards live under card/**/*.json.  This module deliberately does not
register or import any specific card such as T-001.
"""

from dataclasses import dataclass
from pathlib import Path
import json


CARD_ROOT = Path(__file__).resolve().parent / "card"


@dataclass(frozen=True)
class CardDefinition:
    level: int
    cost: int
    trigger_marks: tuple[str, ...]
    power: int
    soul: int
    name: str
    color: str
    traits: tuple[str, ...]
    code: str
    kind: str


@dataclass(frozen=True)
class Card:
    instance_id: str
    number: int  # Debug copy number 1-50, distinct from definition.code.
    definition: CardDefinition
    face_up: bool = True


def load_card_definition(path: Path | str) -> CardDefinition:
    """Load one concrete card definition from a JSON file.

    ``path`` may be a Path or string.  Relative paths are interpreted relative
    to the caller's working directory; deck_loader normally supplies an
    absolute path rooted at CARD_ROOT.
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    return CardDefinition(
        level=data["level"],
        cost=data["cost"],
        trigger_marks=tuple(data.get("trigger_marks", [])),
        power=data["power"],
        soul=data["soul"],
        name=data["name"],
        color=data["color"],
        traits=tuple(data.get("traits", [])),
        code=data["code"],
        kind=data["kind"],
    )


def load_card(relative_path: Path | str) -> CardDefinition:
    """Load one card by a path relative to the project's ``card/`` directory.

    Example:
        load_card("TEST/T-001.json")
    """
    return load_card_definition(CARD_ROOT / relative_path)
