"""Serializable card definitions, separate from individual match instances.

A future editor can produce new definitions without changing play rules.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CardDefinition:
    level: int = 0
    cost: int = 0
    trigger_marks: tuple[str, ...] = ()
    power: int = 500
    soul: int = 1
    name: str = "测试"
    color: str = "yellow"
    traits: tuple[str, ...] = ()
    code: str = "T-001"
    kind: str = "character"


@dataclass(frozen=True)
class Card:
    instance_id: str
    number: int  # Debug copy number 1-50, distinct from definition.code.
    definition: CardDefinition = field(default_factory=CardDefinition)
    face_up: bool = True
