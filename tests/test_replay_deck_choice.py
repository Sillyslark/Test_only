from copy import deepcopy
import json
import unittest

from actions import AdvancePhaseAction, MulliganAction
from deck_loader import DEFAULT_TEST_DECK
from engine import Session, VERSION, state_hash


CHOOSE_DECK = "TEST/Test_All_T_001_Choose.json"


class ReplayDeckChoiceTests(unittest.TestCase):
    def test_current_replay_version_is_seven(self):
        self.assertEqual(7, VERSION)

    def test_current_replay_records_both_selected_decks(self):
        session = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        data = session.replay_data()

        self.assertEqual(7, data["version"])
        self.assertEqual(
            {
                "P1": CHOOSE_DECK,
                "P2": DEFAULT_TEST_DECK,
            },
            data["config"]["decks"],
        )

    def test_current_replay_restores_selected_decks(self):
        session = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        for _ in range(2):
            session.dispatch(
                MulliganAction(session.state.actor, ())
            )
        session.dispatch(
            AdvancePhaseAction(session.state.current_player)
        )

        data = json.loads(
            json.dumps(session.replay_data())
        )
        restored = Session.from_replay(data)

        self.assertEqual(session.deck_sources, restored.deck_sources)
        self.assertEqual(session.state, restored.state)
        self.assertEqual(session.events, restored.events)
        self.assertEqual(session.hashes, restored.hashes)
        self.assertEqual(session.replay_data(), restored.replay_data())

    def test_current_replay_missing_deck_file_fails_instead_of_falling_back(self):
        session = Session(
            42,
            p1_deck=CHOOSE_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )
        data = deepcopy(session.replay_data())
        data["config"]["decks"]["P1"] = "TEST/does_not_exist.json"

        with self.assertRaises(FileNotFoundError):
            Session.from_replay(data)

    def test_current_replay_missing_or_malformed_deck_config_is_rejected(self):
        session = Session(42)

        cases = []

        missing = deepcopy(session.replay_data())
        del missing["config"]["decks"]
        cases.append(missing)

        missing_player = deepcopy(session.replay_data())
        del missing_player["config"]["decks"]["P2"]
        cases.append(missing_player)

        extra_player = deepcopy(session.replay_data())
        extra_player["config"]["decks"]["P3"] = DEFAULT_TEST_DECK
        cases.append(extra_player)

        wrong_type = deepcopy(session.replay_data())
        wrong_type["config"]["decks"] = []
        cases.append(wrong_type)

        for data in cases:
            with self.subTest(config=data["config"]):
                with self.assertRaises(ValueError):
                    Session.from_replay(data)

    def test_v5_replay_without_deck_config_uses_default_decks(self):
        session = Session(42)

        hashes = [
            state_hash(session.state, version=5)
        ]

        for _ in range(2):
            session.dispatch(
                MulliganAction(session.state.actor, ())
            )
            hashes.append(
                state_hash(session.state, version=5)
            )

        data = session.replay_data()
        data["version"] = 5
        data["config"].pop("decks")
        data["state_hashes"] = hashes

        restored = Session.from_replay(
            json.loads(json.dumps(data))
        )

        self.assertEqual(
            {
                "P1": DEFAULT_TEST_DECK,
                "P2": DEFAULT_TEST_DECK,
            },
            restored.deck_sources,
        )
        self.assertEqual(session.state, restored.state)


if __name__ == "__main__":
    unittest.main()
