from copy import deepcopy
import unittest

from engine import Session, Zone, state_hash


class MoveCardTests(unittest.TestCase):

    def test_deck_top_to_hand(self):
        """未指定 card_id 时，从来源区域顶部移动。"""
        session = Session(42)
        player = session.state.players["P1"]

        before_hand = list(player.hand)
        before_deck = list(player.deck)
        top_card = before_deck[0]

        moved = session._move_card(
            "P1",
            Zone.DECK,
            Zone.HAND,
            reason="test_draw",
        )

        self.assertEqual(top_card, moved)

        # 卡组顶部被移除
        self.assertEqual(before_deck[1:], player.deck)

        # 新牌追加到手牌数据末尾
        self.assertEqual(before_hand + [top_card], player.hand)


    def test_specific_hand_card_to_clock_top(self):
        """按 card_id 移动指定手牌，并插入 Clock 顶部。"""
        session = Session(42)
        player = session.state.players["P1"]

        before_hand = list(player.hand)
        chosen = before_hand[2]

        moved = session._move_card(
            "P1",
            Zone.HAND,
            Zone.CLOCK,
            card_id=chosen.instance_id,
            destination_index=0,
            reason="test_clock",
        )

        self.assertEqual(chosen, moved)

        # 指定卡进入 Clock 顶部
        self.assertEqual([chosen], player.clock)

        # 其他手牌保持原顺序
        self.assertEqual(
            before_hand[:2] + before_hand[3:],
            player.hand,
        )


    def test_hand_to_stage_slot(self):
        """手牌可以移动到指定 Stage 槽位。"""
        session = Session(42)
        player = session.state.players["P1"]

        chosen = player.hand[1]

        moved = session._move_card(
            "P1",
            Zone.HAND,
            Zone.STAGE,
            card_id=chosen.instance_id,
            destination_slot="front_center",
            destination_index=0,
            face_up=True,
            reason="test_play",
        )

        self.assertEqual(chosen.instance_id, moved.instance_id)

        stage_card = player.stage["front_center"][0]

        self.assertEqual(chosen.instance_id, stage_card.instance_id)
        self.assertTrue(stage_card.face_up)

        self.assertNotIn(
            chosen.instance_id,
            [card.instance_id for card in player.hand],
        )


    def test_other_cards_keep_relative_order(self):
        """移动中间的卡时，来源区域其他卡牌顺序不能变化。"""
        session = Session(42)
        player = session.state.players["P1"]

        before = list(player.hand)
        chosen = before[2]

        session._move_card(
            "P1",
            Zone.HAND,
            Zone.CLOCK,
            card_id=chosen.instance_id,
            destination_index=0,
            reason="test",
        )

        expected = before[:2] + before[3:]

        self.assertEqual(expected, player.hand)


    def test_missing_card_is_atomic(self):
        """不存在的 card_id 必须失败，并且不能留下任何状态变化。"""
        session = Session(42)

        before = deepcopy(
            (
                session.state,
                session.events,
                session.actions,
                session.hashes,
            )
        )

        with self.assertRaises(ValueError):
            session._move_card(
                "P1",
                Zone.HAND,
                Zone.CLOCK,
                card_id="missing-card",
                destination_index=0,
                reason="test",
            )

        after = (
            session.state,
            session.events,
            session.actions,
            session.hashes,
        )

        self.assertEqual(before, after)


    def test_invalid_stage_slot_is_atomic(self):
        """目标 Stage 槽位无效时，不能先把卡从手牌删除。"""
        session = Session(42)

        player = session.state.players["P1"]
        chosen = player.hand[0]

        before = deepcopy(
            (
                session.state,
                session.events,
                session.actions,
                session.hashes,
            )
        )

        with self.assertRaises(ValueError):
            session._move_card(
                "P1",
                Zone.HAND,
                Zone.STAGE,
                card_id=chosen.instance_id,
                destination_slot="not_a_slot",
                destination_index=0,
                reason="test",
            )

        after = (
            session.state,
            session.events,
            session.actions,
            session.hashes,
        )

        self.assertEqual(before, after)


    def test_card_moved_event(self):
        """成功移动必须产生正确的 card_moved 事件。"""
        session = Session(42)
        player = session.state.players["P1"]

        card = player.deck[0]

        session._move_card(
            "P1",
            Zone.DECK,
            Zone.HAND,
            reason="draw",
        )

        event = session.events[-1]

        self.assertEqual("card_moved", event["kind"])
        self.assertEqual("P1", event["player"])
        self.assertEqual(card.instance_id, event["card_id"])
        self.assertEqual("deck", event["source"])
        self.assertEqual("hand", event["destination"])
        self.assertEqual("draw", event["reason"])


    def test_card_conservation(self):
        """移动前后玩家拥有的卡牌总数和 instance_id 集合必须一致。"""
        session = Session(42)
        player = session.state.players["P1"]

        before_ids = {
            card.instance_id
            for card in (
                player.deck
                + player.hand
                + player.control_room
                + player.clock
                + sum(player.stage.values(), [])
            )
        }

        session._move_card(
            "P1",
            Zone.DECK,
            Zone.HAND,
            reason="test",
        )

        after_ids = {
            card.instance_id
            for card in (
                player.deck
                + player.hand
                + player.control_room
                + player.clock
                + sum(player.stage.values(), [])
            )
        }

        self.assertEqual(before_ids, after_ids)
        self.assertEqual(50, len(after_ids))


if __name__ == "__main__":
    unittest.main()