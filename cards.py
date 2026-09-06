"""Serializable card definitions, separate from individual match instances."""

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


def load_card_definition(path: Path) -> CardDefinition:
    """Load one card definition from a JSON file."""
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


T_001 = load_card_definition(
    CARD_ROOT / "TEST" / "T-001.json"
)