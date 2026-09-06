"""UI-independent game and application commands."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MulliganAction:
    player_id: str
    card_ids: tuple[str, ...]


@dataclass(frozen=True)
class AdvancePhaseAction:
    player_id: str


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
class StartGameAction:
    seed: int | None = None


@dataclass(frozen=True)
class SaveReplayAction:
    path: str


@dataclass(frozen=True)
class LoadReplayAction:
    path: str
