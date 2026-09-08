"""Card data models.

CardDefinition stores immutable printed/base card information. Current card
information belongs to the query layer and is intentionally not calculated here.
"""
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


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


@dataclass(frozen=True)
class Card:
    instance_id: str
    number: int  # Debug copy number; distinct from definition.card_number.
    definition: CardDefinition
    face_up: bool = True  # Runtime migration to CardFaceState is still pending.
