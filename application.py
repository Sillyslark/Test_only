"""Shared action boundary for UI and future clients; no GUI dependencies."""
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import secrets

from actions import StartGameAction, MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction, SaveReplayAction, LoadReplayAction
from engine import GameState, Session


@dataclass(frozen=True)
class Snapshot:
    state: GameState
    events: tuple[dict, ...]


class Application:
    def __init__(self):
        self._session = None

    def snapshot(self):
        """Detached display data: consumers cannot mutate the actual match."""
        if self._session is None:
            raise ValueError("尚未开始游戏")
        return Snapshot(deepcopy(self._session.state), tuple(deepcopy(self._session.events)))

    def dispatch(self, action):
        if isinstance(action, StartGameAction):
            seed = secrets.randbits(63) if action.seed is None else action.seed
            self._session = Session(seed)
        elif isinstance(action, LoadReplayAction):
            data = json.loads(Path(action.path).read_text(encoding="utf-8"))
            session = Session.from_replay(data)
            self._session = session
        elif isinstance(action, (MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction, SaveReplayAction)):
            if self._session is None:
                raise ValueError("尚未开始游戏")
            if isinstance(action, (MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction)):
                self._session.dispatch(action)
            else:
                Path(action.path).write_text(
                    json.dumps(self._session.replay_data(), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        else:
            raise ValueError("未知操作")
        return self.snapshot()
