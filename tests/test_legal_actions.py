import unittest

from actions import MulliganAction, MulliganOptions, StartGameAction
from application import Application
from engine import Session


class MulliganLegalActionsTests(unittest.TestCase):
    def test_only_current_actor_receives_mulligan_options(self):
        session = Session(42)
        actor = session.state.actor
        other_player = "P2" if actor == "P1" else "P1"

        legal = session.legal_actions(actor)

        self.assertEqual(1, len(legal))
        self.assertIsInstance(legal[0], MulliganOptions)

        options = legal[0]
        hand = session.state.players[actor].hand

        self.assertEqual(actor, options.player_id)
        self.assertEqual(
            tuple(card.instance_id for card in hand),
            options.selectable_card_ids,
        )
        self.assertEqual(0, options.min_select)
        self.assertEqual(len(hand), options.max_select)
        self.assertEqual((), session.legal_actions(other_player))

    def test_zero_card_mulligan_is_legal(self):
        session = Session(43)
        actor = session.state.actor
        options = session.legal_actions(actor)

        self.assertEqual(0, options[0].min_select)
        session.dispatch(MulliganAction(actor, ()))
        self.assertEqual(1, session.state.mulligans_completed)

    def test_options_move_to_second_actor(self):
        session = Session(44)
        first_actor = session.state.actor
        session.dispatch(MulliganAction(first_actor, ()))

        second_actor = session.state.actor
        self.assertEqual((), session.legal_actions(first_actor))
        legal = session.legal_actions(second_actor)

        self.assertEqual(1, len(legal))
        self.assertIsInstance(legal[0], MulliganOptions)
        self.assertEqual(second_actor, legal[0].player_id)

    def test_no_mulligan_options_after_both_confirm(self):
        session = Session(45)

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(
                MulliganAction(actor, ())
            )

        for player_id in ("P1", "P2"):
            legal = session.legal_actions(player_id)

            self.assertFalse(
                any(
                    isinstance(action, MulliganOptions)
                    for action in legal
                )
            )

    def test_application_snapshot_exposes_legal_actions(self):
        app = Application()
        view = app.dispatch(StartGameAction(46))

        self.assertEqual(1, len(view.legal_actions))
        self.assertIsInstance(view.legal_actions[0], MulliganOptions)
        self.assertEqual(view.state.actor, view.legal_actions[0].player_id)

    def test_invalid_player_is_rejected(self):
        session = Session(47)
        with self.assertRaises(ValueError):
            session.legal_actions("P3")


if __name__ == "__main__":
    unittest.main()
