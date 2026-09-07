import unittest

from actions import AdvancePhaseAction, ClockAction, ClockOptions, MulliganAction
from engine import Session, other

from zones import Zone

class TurnClockPhaseTests(unittest.TestCase):
    def open_clock_phase(self, seed=61):
        session = Session(seed)

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        current = session.state.current_player
        session.dispatch(AdvancePhaseAction(current))  # Stand -> Draw
        session.dispatch(AdvancePhaseAction(current))  # Draw -> Clock
        return session

    def test_clock_phase_lifecycle_reaches_action_window(self):
        session = self.open_clock_phase()
        self.assertEqual("clock", session.state.phase)

        lifecycle = [
            event
            for event in session.events
            if (
                event["kind"] in {
                    "phase_started",
                    "phase_processed",
                    "action_window_opened",
                }
                and event.get("phase") == "clock"
            )
        ]

        self.assertGreaterEqual(len(lifecycle), 3)
        self.assertEqual(
            [
                "phase_started",
                "phase_processed",
                "action_window_opened",
            ],
            [event["kind"] for event in lifecycle[-3:]],
        )

    def test_clock_options_expose_current_hand_and_skip(self):
        session = self.open_clock_phase(62)
        current = session.state.current_player
        player = session.state.players[current]

        legal = session.legal_actions(current)

        self.assertEqual(1, len(legal))
        self.assertIsInstance(legal[0], ClockOptions)

        options = legal[0]
        self.assertEqual(current, options.player_id)
        self.assertTrue(options.can_skip)
        self.assertEqual(
            tuple(card.instance_id for card in player.hand),
            options.selectable_card_ids,
        )
        self.assertEqual((), session.legal_actions(other(current)))

    def test_skip_clock_ends_clock_and_enters_main(self):
        session = self.open_clock_phase(63)
        current = session.state.current_player
        player = session.state.players[current]

        hand_before = list(player.hand)
        clock_before = list(player.clock)
        deck_before = list(player.deck)

        start = len(session.events)
        session.dispatch(AdvancePhaseAction(current))
        events = session.events[start:]

        self.assertEqual("main", session.state.phase)
        self.assertEqual(hand_before, player.hand)
        self.assertEqual(clock_before, player.clock)
        self.assertEqual(deck_before, player.deck)

        clock_end = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "phase_ended" and event["phase"] == "clock"
        )
        main_start = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "phase_started" and event["phase"] == "main"
        )
        self.assertLess(clock_end, main_start)

    def test_clock_action_moves_selected_card_and_draws_two(self):
        session = self.open_clock_phase(64)
        current = session.state.current_player
        player = session.state.players[current]

        chosen = player.hand[1]
        hand_before = list(player.hand)
        deck_before = list(player.deck)

        session.dispatch(
            ClockAction(
                current,
                chosen.instance_id,
            )
        )

        self.assertTrue(session.state.clock_used)
        self.assertEqual(chosen, player.clock[0])
        self.assertEqual(
            hand_before[:1] + hand_before[2:] + deck_before[:2],
            player.hand,
        )
        self.assertEqual(deck_before[2:], player.deck)

        self.assertEqual(
            (AdvancePhaseAction(current),),
            session.legal_actions(current),
        )

    def test_wrong_player_has_no_clock_options(self):
        session = self.open_clock_phase(65)
        current = session.state.current_player
        self.assertEqual((), session.legal_actions(other(current)))

    def test_clock_action_level_up_then_draw_refresh_then_second_draw(self):
        """
        Initial:
            Clock = 6
            Deck = 1
            Waiting Room = 8
            Hand = 1

        Expected order:
            selected Hand card -> Clock
            Level Up
            first draw empties Deck
            Refresh
            Refresh Point -> Clock
            second draw
            ClockAction completes
        """
        session = self.open_clock_phase(66)

        current = session.state.current_player
        player = session.state.players[current]

        # --------------------------------------------------
        # Test setup
        # --------------------------------------------------

        # 保留当前手牌中的1张，其他手牌暂时移入 Memory。
        chosen = player.hand[0]

        for card in list(player.hand[1:]):
            session._move_card(
                current,
                Zone.HAND,
                Zone.MEMORY,
                card_id=card.instance_id,
                reason="test_setup",
            )

        # 把 Deck 全部暂时移入 Memory。
        while player.deck:
            session._move_card(
                current,
                Zone.DECK,
                Zone.MEMORY,
                reason="test_setup",
            )

        # 从 Memory 构造 Clock 6。
        for _ in range(6):
            session._move_card(
                current,
                Zone.MEMORY,
                Zone.CLOCK,
                reason="test_setup",
            )

        # 构造 Waiting Room 8。
        for _ in range(8):
            session._move_card(
                current,
                Zone.MEMORY,
                Zone.WAITING_ROOM,
                reason="test_setup",
            )

        # 构造 Deck 1。
        session._move_card(
            current,
            Zone.MEMORY,
            Zone.DECK,
            destination_index=0,
            reason="test_setup",
        )

        self.assertEqual(1, len(player.hand))
        self.assertEqual(6, len(player.clock))
        self.assertEqual(1, len(player.deck))
        self.assertEqual(8, len(player.waiting_room))

        first_draw_card = player.deck[0]

        # --------------------------------------------------
        # Execute ClockAction
        # --------------------------------------------------

        start = len(session.events)

        session.dispatch(
            ClockAction(
                current,
                chosen.instance_id,
            )
        )

        events = session.events[start:]

        # --------------------------------------------------
        # Final state
        # --------------------------------------------------

        self.assertTrue(session.state.clock_used)

        # 原手牌进入Clock后参与升级，因此最终手牌来自两次抽牌。
        self.assertEqual(2, len(player.hand))

        # 第一张抽出的牌必须是原本唯一的Deck牌。
        self.assertIn(
            first_draw_card.instance_id,
            [card.instance_id for card in player.hand],
        )

        self.assertEqual(1, len(player.level))

        # Level Up 后原Clock清空，
        # Refresh Point重新建立1张Clock。
        self.assertEqual(1, len(player.clock))

        self.assertEqual(0, len(player.waiting_room))

        # Level Up送6张到Waiting：
        #
        # 原 Waiting 8 + Level Up 6 = 14
        #
        # Refresh后：
        # 14 - Refresh Point 1 - 第二次抽牌 1 = 12
        self.assertEqual(12, len(player.deck))

        # --------------------------------------------------
        # Event ordering
        # --------------------------------------------------

        clock_move = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "card_moved"
                and event.get("reason") == "clock"
            )
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

        draws = [
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "card_moved"
                and event.get("reason") == "clock_draw"
            )
        ]

        self.assertEqual(2, len(draws))

        first_draw, second_draw = draws

        refresh_started = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "refresh_started"
        )

        refresh_point = next(
            i
            for i, event in enumerate(events)
            if (
                event["kind"] == "card_moved"
                and event.get("reason") == "refresh_point"
            )
        )

        refresh_completed = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "refresh_completed"
        )

        clock_completed = next(
            i
            for i, event in enumerate(events)
            if event["kind"] == "card_clocked"
        )

        self.assertLess(
            clock_move,
            level_started,
        )

        self.assertLess(
            level_started,
            level_completed,
        )

        self.assertLess(
            level_completed,
            first_draw,
        )

        self.assertLess(
            first_draw,
            refresh_started,
        )

        self.assertLess(
            refresh_started,
            refresh_point,
        )

        self.assertLess(
            refresh_point,
            refresh_completed,
        )

        self.assertLess(
            refresh_completed,
            second_draw,
        )

        self.assertLess(
            second_draw,
            clock_completed,
        )

if __name__ == "__main__":
    unittest.main()
