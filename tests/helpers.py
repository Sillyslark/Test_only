from actions import AdvancePhaseAction, MulliganAction
from engine import Session


def opened(seed: int = 42) -> Session:
    session = Session(seed)
    for _ in range(2):
        session.dispatch(MulliganAction(session.state.actor, ()))
    return session


def at_clock(seed: int = 42) -> Session:
    session = opened(seed)
    for _ in range(2):
        session.dispatch(AdvancePhaseAction(session.state.current_player))
    return session


def at_main(seed: int = 42) -> Session:
    session = opened(seed)
    for _ in range(3):
        session.dispatch(AdvancePhaseAction(session.state.current_player))
    return session
