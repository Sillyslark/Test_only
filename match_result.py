"""Stable match-result values used by engine, UI, replay and AI layers."""

from enum import Enum


class MatchResult(str, Enum):
    ONGOING = "ongoing"
    P1_WIN = "p1_win"
    P2_WIN = "p2_win"
    BOTH_LOSE = "both_lose"
