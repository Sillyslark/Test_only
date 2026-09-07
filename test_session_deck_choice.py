import unittest
from unittest.mock import patch

from deck_loader import DEFAULT_TEST_DECK
from engine import Session


CHOOSE_DECK = "TEST/Test_All_T_001_Choose.json"


class SessionDeckChoiceTests(unittest.TestCase):
    def test_default_session_still_uses_original_test_deck(self):
        session = Session(42)

        self.assertEqual(
            {
                "P1": DEFAULT_TEST_DECK,
                "P2": DEFAULT_TEST_DECK,
            },
            session.deck_sources,
        )

        for player in session.state.players.values():
            cards = player.hand + player.deck
            self.assertEqual(50, len(cards))
            self.assertTrue(
                all(card.definition.code == "T-001" for card in cards)
            )

    def test_p1_and_p2_can_select_decks_independently(self):
        session = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        self.assertEqual(CHOOSE_DECK, session.deck_sources["P1"])
        self.assertEqual(DEFAULT_TEST_DECK, session.deck_sources["P2"])

    def test_both_players_can_select_choose_copy(self):
        session = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=CHOOSE_DECK,
        )

        self.assertEqual(
            {
                "P1": CHOOSE_DECK,
                "P2": CHOOSE_DECK,
            },
            session.deck_sources,
        )

    def test_selected_paths_are_actually_passed_to_build_deck(self):
        original_build = __import__("engine").build_deck
        seen = []

        def recording_build(path, player_id):
            seen.append((path.name, player_id))
            return original_build(path, player_id)

        with patch("engine.build_deck", side_effect=recording_build):
            Session(
                42,
                p1_deck=CHOOSE_DECK,
                p2_deck=DEFAULT_TEST_DECK,
            )

        self.assertEqual(
            [
                ("Test_All_T_001_Choose.json", "P1"),
                ("Test_All_T_001.json", "P2"),
            ],
            seen,
        )

    def test_same_seed_and_same_selected_decks_are_deterministic(self):
        a = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )
        b = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        self.assertEqual(a.state, b.state)
        self.assertEqual(a.deck_sources, b.deck_sources)

    def test_missing_deck_fails_before_match_creation(self):
        with self.assertRaises(FileNotFoundError):
            Session(
                42,
                p1_deck="TEST/does_not_exist.json",
                p2_deck=DEFAULT_TEST_DECK,
            )

    def test_deck_path_cannot_escape_deck_directory(self):
        with self.assertRaises(ValueError):
            Session(
                42,
                p1_deck="../card/TEST/T-001.json",
                p2_deck=DEFAULT_TEST_DECK,
            )


if __name__ == "__main__":
    unittest.main()
