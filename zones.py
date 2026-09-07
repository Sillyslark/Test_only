"""Zone definitions shared by the engine and rule modules."""

from enum import Enum


class Zone(str, Enum):
    DECK = "deck"
    HAND = "hand"
    WAITING_ROOM = "waiting_room"
    CLOCK = "clock"
    LEVEL = "level"
    STOCK = "stock"
    MEMORY = "memory"
    CLIMAX = "climax"
    RESOLUTION = "resolution_zone"
    STAGE = "stage"
