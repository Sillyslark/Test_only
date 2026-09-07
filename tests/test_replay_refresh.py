import json
import unittest

from actions import AdvancePhaseAction, ClockAction
from engine import Session
from tests.helpers import opened


def play_until_refresh(session, max_steps=500):
    """Advance only through replayable Actions until the first Refresh occurs.

    At every Clock phase the current player performs Clock once, so Clock cards
    eventually create Level Up / Waiting Room cards and Deck consumption is fast
    enough to reach a real Refresh without any direct state mutation.
    """
    for _ in range(max_steps):
        if any(event["kind"] == "refresh_completed" for event in session.events):
            return

        state = session.state
        player = state.players[state.current_player]

        if state.phase == "clock" and not state.clock_used:
            if not player.hand:
                raise AssertionError("测试流程意外出现空手牌，无法继续 ClockAction")
            session.dispatch(
                ClockAction(
                    state.current_player,
                    player.hand[0].instance_id,
                )
            )
        else:
            session.dispatch(AdvancePhaseAction(state.current_player))

    raise AssertionError("在 max_steps 内没有触发牌库刷新")


def perform_one_replayable_step(session):
    """Perform one deterministic normal Action from the current state."""
    state = session.state
    player = state.players[state.current_player]

    if state.phase == "clock" and not state.clock_used:
        if not player.hand:
            raise AssertionError("测试流程意外出现空手牌")
        return session.dispatch(
            ClockAction(
                state.current_player,
                player.hand[0].instance_id,
            )
        )

    return session.dispatch(AdvancePhaseAction(state.current_player))


class RefreshReplayTests(unittest.TestCase):
    def test_refresh_replay_reproduces_state_events_and_rng(self):
        """A real Action trace containing Refresh must replay identically."""
        session = opened()
        play_until_refresh(session)

        self.assertTrue(
            any(event["kind"] == "refresh_completed" for event in session.events)
        )
        self.assertTrue(
            any(event["kind"] == "deck_shuffled" for event in session.events)
        )

        replay = json.loads(json.dumps(session.replay_data()))
        restored = Session.from_replay(replay)

        # Full game state, including Deck order and rng_state, must match.
        self.assertEqual(session.state, restored.state)

        # Event history must also reproduce exactly.
        self.assertEqual(session.events, restored.events)

        # Re-serializing the restored session must yield the same Replay.
        self.assertEqual(session.replay_data(), restored.replay_data())

        # Explicitly protect the two refresh-sensitive pieces.
        for player_id in session.state.players:
            original = session.state.players[player_id]
            replayed = restored.state.players[player_id]
            self.assertEqual(
                [card.instance_id for card in original.deck],
                [card.instance_id for card in replayed.deck],
            )

        self.assertEqual(session.state.rng_state, restored.state.rng_state)

    def test_replay_can_continue_identically_after_refresh(self):
        """Original and restored matches must stay deterministic after Refresh."""
        session = opened()
        play_until_refresh(session)

        replay = json.loads(json.dumps(session.replay_data()))
        restored = Session.from_replay(replay)

        # Continue several normal Actions after the refresh. This catches cases
        # where the saved state looks equal but the future RNG/action timeline
        # has diverged.
        for _ in range(12):
            self.assertEqual(session.state, restored.state)

            perform_one_replayable_step(session)
            perform_one_replayable_step(restored)

            self.assertEqual(session.state, restored.state)
            self.assertEqual(session.events, restored.events)
            self.assertEqual(session.replay_data(), restored.replay_data())

    def test_refresh_does_not_create_a_synthetic_action(self):
        """Refresh/Level Up remain rule resolutions inside their parent Action."""
        session = opened()

        play_until_refresh(session)

        action_kinds = [
            entry["kind"]
            for entry in session.replay_data()["actions"]
        ]

        self.assertNotIn("refresh", action_kinds)
        self.assertNotIn("level_up", action_kinds)

        # But the rule resolutions must still be visible in the event history.
        self.assertTrue(
            any(event["kind"] == "refresh_completed" for event in session.events)
        )


if __name__ == "__main__":
    unittest.main()
