"""Shared action boundary for UI and future clients; no GUI dependencies."""
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import secrets

from actions import (
    StartGameAction,
    MulliganAction,
    AdvancePhaseAction,
    ClockAction,
    PlayCardAction,
    SaveReplayAction,
    LoadReplayAction,
)
from engine import GameState, Session


@dataclass(frozen=True)
class Snapshot:
    state: GameState
    events: tuple[dict, ...]
    legal_actions: tuple[object, ...]


class Application:
    def __init__(self):
        self._session = None

    def snapshot(self):
        """Detached display data: consumers cannot mutate the actual match."""
        if self._session is None:
            raise ValueError("尚未开始游戏")
        state = deepcopy(self._session.state)
        active_player = state.actor or state.current_player
        legal_actions = (
            self._session.legal_actions(active_player)
            if active_player is not None
            else ()
        )
        return Snapshot(
            state,
            tuple(deepcopy(self._session.events)),
            tuple(deepcopy(legal_actions)),
        )

    def dispatch(self, action):
        if isinstance(action, StartGameAction):
            seed = secrets.randbits(63) if action.seed is None else action.seed

            # Construct first, then publish.  If deck loading / validation fails,
            # an already-running match is not replaced by a partial new session.
            new_session = Session(
                seed,
                p1_deck=action.p1_deck,
                p2_deck=action.p2_deck,
            )
            self._session = new_session

        elif isinstance(action, LoadReplayAction):
            data = json.loads(
                Path(action.path).read_text(encoding="utf-8")
            )
            session = Session.from_replay(data)
            self._session = session

        elif isinstance(
            action,
            (
                MulliganAction,
                AdvancePhaseAction,
                ClockAction,
                PlayCardAction,
                SaveReplayAction,
            ),
        ):
            if self._session is None:
                raise ValueError("尚未开始游戏")

            if isinstance(
                action,
                (
                    MulliganAction,
                    AdvancePhaseAction,
                    ClockAction,
                    PlayCardAction,
                ),
            ):
                self._session.dispatch(action)
            else:
                Path(action.path).write_text(
                    json.dumps(
                        self._session.replay_data(),
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
        else:
            raise ValueError("未知操作")

        return self.snapshot()
