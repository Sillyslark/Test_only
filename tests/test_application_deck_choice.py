from copy import deepcopy
import unittest

from actions import StartGameAction
from application import Application
from deck_loader import DEFAULT_TEST_DECK


CHOOSE_DECK = "TEST/Test_All_T_001_Choose.json"


class ApplicationDeckChoiceTests(unittest.TestCase):
    def test_start_game_defaults_to_original_deck(self):
        app = Application()

        snapshot = app.dispatch(
            StartGameAction(seed=42)
        )

        self.assertEqual(
            {
                "P1": DEFAULT_TEST_DECK,
                "P2": DEFAULT_TEST_DECK,
            },
            app._session.deck_sources,
        )

        for player in snapshot.state.players.values():
            cards = player.hand + player.deck
            self.assertEqual(50, len(cards))
            self.assertTrue(
                all(card.definition.card_number == "T-001" for card in cards)
            )

    def test_start_game_can_choose_decks_independently(self):
        app = Application()

        app.dispatch(
            StartGameAction(
                seed=42,
                p1_deck=CHOOSE_DECK,
                p2_deck=DEFAULT_TEST_DECK,
            )
        )

        self.assertEqual(
            CHOOSE_DECK,
            app._session.deck_sources["P1"],
        )
        self.assertEqual(
            DEFAULT_TEST_DECK,
            app._session.deck_sources["P2"],
        )

    def test_invalid_selected_deck_does_not_replace_existing_match(self):
        app = Application()

        app.dispatch(
            StartGameAction(seed=42)
        )

        before = deepcopy(app._session.__dict__)

        with self.assertRaises(FileNotFoundError):
            app.dispatch(
                StartGameAction(
                    seed=99,
                    p1_deck="TEST/does_not_exist.json",
                    p2_deck=DEFAULT_TEST_DECK,
                )
            )

        self.assertEqual(
            before,
            app._session.__dict__,
        )

    def test_start_game_action_is_immutable(self):
        action = StartGameAction(
            seed=42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        with self.assertRaises(Exception):
            action.p1_deck = DEFAULT_TEST_DECK


if __name__ == "__main__":
    unittest.main()
