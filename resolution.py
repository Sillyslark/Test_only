"""Resolution-point scaffolding for rules and triggered effects."""

from dataclasses import dataclass, field
from typing import Callable, Any
from enum import Enum


@dataclass
class TriggeredEffect:
    """Placeholder representation of a triggered effect.

    Real card-effect data can replace/extend this later.
    """
    effect_id: str
    controller: str
    source_card_id: str | None = None
    trigger_kind: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionContext:
    """One timing / resolution point.

    event_cursor marks the first Session.events entry belonging to this timing.
    Each player has an independent pending pool.
    """
    turn_player: str
    non_turn_player: str
    event_cursor: int
    events: list[dict] = field(default_factory=list)
    turn_player_pool: list[TriggeredEffect] = field(default_factory=list)
    non_turn_player_pool: list[TriggeredEffect] = field(default_factory=list)

    def pool_for(self, player_id: str) -> list[TriggeredEffect]:
        if player_id == self.turn_player:
            return self.turn_player_pool
        if player_id == self.non_turn_player:
            return self.non_turn_player_pool
        raise ValueError("玩家不属于当前结算时点")

    def add_effect(self, effect: TriggeredEffect):
        self.pool_for(effect.controller).append(effect)

    def has_pending_effects(self) -> bool:
        return bool(
            self.turn_player_pool
            or self.non_turn_player_pool
        )

    def capture_new_events(self, session_events: list[dict]) -> list[dict]:
        """Capture only events not yet seen by this resolution point."""
        new_events = session_events[self.event_cursor:]
        if new_events:
            self.events.extend(new_events)
            self.event_cursor = len(session_events)
        return list(new_events)


def collect_triggers(events: list[dict], context: ResolutionContext):
    """Placeholder trigger collector.

    Later this will inspect events such as:
    - card_moved hand -> stage
    - card_moved stage -> waiting_room
    - card_played
    and add TriggeredEffect objects to the proper player's pool.
    """
    return []


def resolve_pending_effects(
    context: ResolutionContext,
    *,
    choose_effect: Callable[[str, list[TriggeredEffect]], TriggeredEffect] | None = None,
    resolve_effect: Callable[[TriggeredEffect, ResolutionContext], None] | None = None,
):
    """Resolve turn player's pool completely, then non-turn player's pool.

    If resolving one effect adds more effects for the same player, the while-loop
    keeps that player active until their pool is empty.

    With the current placeholder trigger collector both pools remain empty, so
    no chooser/resolver is required yet.
    """
    for player_id in (context.turn_player, context.non_turn_player):
        pool = context.pool_for(player_id)

        while pool:
            if choose_effect is None or resolve_effect is None:
                raise RuntimeError("存在待处理效果，但尚未提供效果选择/结算器")

            effect = choose_effect(player_id, list(pool))
            if effect not in pool:
                raise ValueError("选择的效果不在当前玩家待处理池中")

            pool.remove(effect)
            resolve_effect(effect, context)



class InterruptRule(str, Enum):
    LEVEL_UP = "level_up"
    REFRESH = "refresh"
