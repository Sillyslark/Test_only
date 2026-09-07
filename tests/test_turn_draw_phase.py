import unittest

from actions import AdvancePhaseAction, MulliganAction
from engine import Session, other
from zones import Zone


class TurnDrawPhaseTests(unittest.TestCase):
    def open_draw_phase(self, seed=42):
        session = Session(seed)

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        current = session.state.current_player
        session.dispatch(AdvancePhaseAction(current))

        return session

    def test_draw_phase_lifecycle_and_mandatory_draw(self):
        """Draw START -> mandatory draw -> Draw PROCESS -> action window."""
        session = Session(51)

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        current = session.state.current_player
        player = session.state.players[current]
        expected = player.deck[0]
        hand_before = list(player.hand)
        deck_before = list(player.deck)

        start = len(session.events)
        session.dispatch(AdvancePhaseAction(current))
        events = session.events[start:]

        self.assertEqual("draw", session.state.phase)
        self.assertEqual(
            hand_before + [expected],
            player.hand,
        )
        self.assertEqual(
            deck_before[1:],
            player.deck,
        )

        draw_start = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "phase_started" and event["phase"] == "draw"
        )
        draw_move = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "card_moved" and event.get("reason") == "draw"
        )
        card_drawn = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "card_drawn"
        )
        draw_processed = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "phase_processed" and event["phase"] == "draw"
        )
        action_window = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "action_window_opened" and event["phase"] == "draw"
        )

        self.assertLess(draw_start, draw_move)
        self.assertLess(draw_move, card_drawn)
        self.assertLess(card_drawn, draw_processed)
        self.assertLess(draw_processed, action_window)

        self.assertEqual(expected.instance_id, events[card_drawn]["card_id"])

    def test_draw_action_window_only_allows_advance_to_clock(self):
        session = self.open_draw_phase(52)
        current = session.state.current_player

        self.assertEqual(
            (AdvancePhaseAction(current),),
            session.legal_actions(current),
        )
        self.assertEqual(
            (),
            session.legal_actions(other(current)),
        )

    def test_draw_advance_emits_draw_end_before_clock_start(self):
        """This test stops conceptually at Clock Phase START."""
        session = self.open_draw_phase(53)
        current = session.state.current_player

        start = len(session.events)
        session.dispatch(AdvancePhaseAction(current))
        events = session.events[start:]

        self.assertEqual("clock", session.state.phase)

        draw_end = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "phase_ended" and event["phase"] == "draw"
        )
        clock_start = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "phase_started" and event["phase"] == "clock"
        )

        self.assertLess(draw_end, clock_start)

    def test_draw_phase_refreshes_before_mandatory_draw_when_needed(self):
        """If Deck is empty and Waiting has cards, Refresh interrupts before draw."""
        session = Session(54)

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        current = session.state.current_player
        player = session.state.players[current]

        # Move the whole Deck to Waiting Room before leaving Stand.
        while player.deck:
            session._move_card(
                current,
                Zone.DECK,
                Zone.WAITING_ROOM,
                reason="test_setup",
            )

        hand_before = len(player.hand)
        start = len(session.events)

        session.dispatch(AdvancePhaseAction(current))
        events = session.events[start:]

        refresh_started = next(
            i for i, event in enumerate(events)
            if event["kind"] == "refresh_started"
        )
        refresh_completed = next(
            i for i, event in enumerate(events)
            if event["kind"] == "refresh_completed"
        )
        draw_move = next(
            i for i, event in enumerate(events)
            if event["kind"] == "card_moved" and event.get("reason") == "draw"
        )

        self.assertLess(refresh_started, refresh_completed)
        self.assertLess(refresh_completed, draw_move)
        self.assertEqual(hand_before + 1, len(player.hand))
        self.assertEqual("draw", session.state.phase)

    def test_wrong_player_cannot_end_draw_phase(self):
        session = self.open_draw_phase(55)
        current = session.state.current_player

        with self.assertRaises(ValueError):
            session.dispatch(
                AdvancePhaseAction(other(current))
            )

    def test_last_draw_refresh_point_causes_level_up_before_action_window(self):
        """
        Clock 6, Deck 1, Waiting Room 8.

        Draw the final Deck card:
        1. mandatory draw empties Deck
        2. Refresh rebuilds Deck from Waiting Room
        3. Refresh Point makes Clock reach 7
        4. Level Up resolves
        5. only then may the Draw action window open
        """
        session = Session(56)

        # 完成双方换牌，停在 Stand Phase。
        for _ in range(2):
            actor = session.state.actor
            session.dispatch(
                MulliganAction(actor, ())
            )

        current = session.state.current_player
        player = session.state.players[current]

        # --------------------------------------------------
        # Test setup
        # --------------------------------------------------

        # 先把当前玩家除手牌外的卡全部集中到 Waiting Room。
        while player.deck:
            session._move_card(
                current,
                Zone.DECK,
                Zone.WAITING_ROOM,
                reason="test_setup",
            )

        # 从 Waiting Room 构造：
        # Clock = 6
        # Deck = 1
        #
        # Waiting Room 最终至少还需要 8 张。
        for _ in range(6):
            session._move_card(
                current,
                Zone.WAITING_ROOM,
                Zone.CLOCK,
                reason="test_setup",
            )

        session._move_card(
            current,
            Zone.WAITING_ROOM,
            Zone.DECK,
            destination_index=0,
            reason="test_setup",
        )

        # 当前卡组原本有足够的牌，因此 Waiting 会远多于 8。
        # 为了严格构造 Waiting = 8，
        # 多余卡暂时放入 Memory。
        while len(player.waiting_room) > 8:
            session._move_card(
                current,
                Zone.WAITING_ROOM,
                Zone.MEMORY,
                reason="test_setup",
            )

        self.assertEqual(6, len(player.clock))
        self.assertEqual(1, len(player.deck))
        self.assertEqual(8, len(player.waiting_room))

        last_deck_card = player.deck[0]
        hand_before = len(player.hand)

        # --------------------------------------------------
        # Enter Draw Phase
        # --------------------------------------------------

        start = len(session.events)

        session.dispatch(
            AdvancePhaseAction(current)
        )

        events = session.events[start:]

        # --------------------------------------------------
        # Final state
        # --------------------------------------------------

        self.assertEqual("draw", session.state.phase)

        # 最后一张 Deck 卡确实完成了规则抽牌。
        self.assertIn(
            last_deck_card.instance_id,
            [card.instance_id for card in player.hand],
        )

        self.assertEqual(
            hand_before + 1,
            len(player.hand),
        )

        # Refresh Point 使 Clock 达到 7，
        # 随后 Level Up 已经完成。
        self.assertEqual(1, len(player.level))

        # Level Up 后 Clock 的 7 张已经全部离开 Clock：
        # 1 → Level
        # 6 → Waiting Room
        self.assertEqual(0, len(player.clock))

        # --------------------------------------------------
        # Event ordering
        # --------------------------------------------------

        draw_move = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "card_moved"
                and event.get("reason") == "draw"
            )
        )

        refresh_started = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "refresh_started"
        )

        refresh_completed = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "refresh_completed"
        )

        level_started = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "level_up_started"
        )

        level_completed = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "level_up_completed"
        )

        draw_processed = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "phase_processed"
                and event["phase"] == "draw"
            )
        )

        action_window = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "action_window_opened"
                and event["phase"] == "draw"
            )
        )

        self.assertLess(
            draw_move,
            refresh_started,
        )

        self.assertLess(
            refresh_started,
            refresh_completed,
        )

        self.assertLess(
            refresh_completed,
            level_started,
        )

        self.assertLess(
            level_started,
            level_completed,
        )

        self.assertLess(
            level_completed,
            draw_processed,
        )

        self.assertLess(
            draw_processed,
            action_window,
        )

if __name__ == "__main__":
    unittest.main()
