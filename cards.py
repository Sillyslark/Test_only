"""Card data models and JSON loading helpers.

Concrete cards live under card/**/*.json.  CardDefinition stores immutable
printed/base card information; current card information belongs to the query
layer and is intentionally not calculated here.
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
from typing import ClassVar, TypeAlias

CARD_ROOT = Path(__file__).resolve().parent / "card"

class CardType(str, Enum):
    CHARACTER = "character"
    EVENT = "event"
    CLIMAX = "climax"

class CardColor(str, Enum):
    YELLOW = "yellow"
    GREEN = "green"
    RED = "red"
    BLUE = "blue"

class CardIcon(str, Enum):
    COUNTER = "counter"
    CLOCK = "clock"

class TriggerIcon(str, Enum):
    SOUL = "soul"
    RETURN = "return"
    POOL = "pool"
    SHOT = "shot"
    TREASURE = "treasure"
    COMEBACK = "comeback"
    DRAW = "draw"
    STANDBY = "standby"
    CHOICE = "choice"

class CardOrientation(str, Enum):
    STAND = "stand"
    REST = "rest"
    REVERSE = "reverse"

class CardFaceState(str, Enum):
    FACE_UP = "face_up"
    FACE_DOWN = "face_down"

@dataclass(frozen=True)
class CardDefinition:
    card_number: str
    name: str
    color: CardColor
    trigger_icons: tuple[TriggerIcon, ...]
    card_type: ClassVar[CardType]

    # Transitional read-only compatibility for existing code/tests/replays.
    @property
    def code(self) -> str:
        return self.card_number

    @property
    def kind(self) -> str:
        return self.card_type.value

    @property
    def trigger_marks(self) -> tuple[str, ...]:
        return tuple(icon.value for icon in self.trigger_icons)

@dataclass(frozen=True)
class CharacterDefinition(CardDefinition):
    level: int
    cost: int
    power: int
    soul: int
    traits: tuple[str, ...]
    card_icons: tuple[CardIcon, ...]
    card_type: ClassVar[CardType] = CardType.CHARACTER

@dataclass(frozen=True)
class EventDefinition(CardDefinition):
    level: int
    cost: int
    card_icons: tuple[CardIcon, ...]
    card_type: ClassVar[CardType] = CardType.EVENT

@dataclass(frozen=True)
class ClimaxDefinition(CardDefinition):
    card_type: ClassVar[CardType] = CardType.CLIMAX

# Transitional alias only. New code should type against CardDefinition.
AnyCardDefinition: TypeAlias = CardDefinition

@dataclass(frozen=True)
class Card:
    instance_id: str
    number: int  # Debug copy number; distinct from definition.card_number.
    definition: CardDefinition
    face_up: bool = True  # Runtime migration to CardFaceState is still pending.


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
    """Load one concrete card definition from JSON.

    The loader currently accepts the repository's legacy JSON keys
    (code/kind/trigger_marks/icons) while exposing only the new typed model.
    This keeps deck fixtures usable during the schema migration.
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    card_type = _enum_value(CardType, data["kind"], "card_type")
    color = _enum_value(CardColor, data["color"], "color")
    common = dict(
        card_number=data["code"],
        name=data["name"],
        color=color,
        trigger_icons=_tuple_enum(data, "trigger_marks", TriggerIcon),
    )

    if card_type is CardType.CHARACTER:
        return CharacterDefinition(
            **common,
            level=data["level"],
            cost=data["cost"],
            power=data["power"],
            soul=data["soul"],
            traits=tuple(data.get("traits", [])),
            card_icons=_tuple_enum(data, "icons", CardIcon),
        )
    if card_type is CardType.EVENT:
        return EventDefinition(
            **common,
            level=data["level"],
            cost=data["cost"],
            card_icons=_tuple_enum(data, "icons", CardIcon),
        )
    if card_type is CardType.CLIMAX:
        return ClimaxDefinition(**common)
    raise AssertionError("unreachable CardType")


def load_card(relative_path: Path | str) -> CardDefinition:
    """Load one card by a path relative to the project's card/ directory."""
    relative_path = Path(relative_path)
    if relative_path.is_absolute():
        raise ValueError("卡片路径必须相对于 card/ 目录")
    root = CARD_ROOT.resolve()
    resolved = (CARD_ROOT / relative_path).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("卡片路径不能离开 card/ 目录")
    return load_card_definition(resolved)
