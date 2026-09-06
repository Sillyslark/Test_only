"""Zone definitions shared by the engine and rule modules."""

from enum import Enum


class Zone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    CONTROL_ROOM = "control_room"
    CLOCK = "clock"
    STAGE = "stage"
