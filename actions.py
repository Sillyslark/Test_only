"""UI-independent game and application commands."""
from dataclasses import dataclass

from deck_loader import DEFAULT_TEST_DECK


@dataclass(frozen=True)
class MulliganOptions:
    player_id: str
    selectable_card_ids: tuple[str, ...]
    min_select: int
    max_select: int


@dataclass(frozen=True)
class MulliganAction:
    player_id: str
    card_ids: tuple[str, ...]


@dataclass(frozen=True)
class AdvancePhaseAction:
    player_id: str

@dataclass(frozen=True)
class ClockOptions:
    player_id: str
    selectable_card_ids: tuple[str, ...]
    can_skip: bool = True

@dataclass(frozen=True)
class ClockAction:
    player_id: str
    card_id: str


@dataclass(frozen=True)
class PlayCardAction:
    player_id: str
    card_id: str
    target_slot: str

@dataclass(frozen=True)
class StageSwapOptions:
    player_id: str
    selectable_slots: tuple[str, ...]


@dataclass(frozen=True)
class SwapStageSlotsAction:
    player_id: str
    first_slot: str
    second_slot: str

@dataclass(frozen=True)
class StartGameAction:
    seed: int | None = None
    p1_deck: str = DEFAULT_TEST_DECK
    p2_deck: str = DEFAULT_TEST_DECK


@dataclass(frozen=True)
class SaveReplayAction:
    path: str


@dataclass(frozen=True)
class LoadReplayAction:
    path: str
