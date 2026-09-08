from card_definition import CardType
import json
import unittest

from actions import AdvancePhaseAction, MulliganAction
from card_definition import ClimaxDefinition
from deck_loader import DEFAULT_TEST_DECK
from engine import Session


MIXED_DECK = "TEST/Test_42_T_001_8_T_002.json"


def all_player_cards(player):
    cards = (
        player.deck
        + player.hand
        + player.waiting_room
        + player.clock
        + player.level
        + player.stock
        + player.memory
        + player.climax
    )
    for slot_cards in player.stage.values():
        cards += slot_cards
    return cards


class MixedDeckSessionTests(unittest.TestCase):
    def test_one_player_can_start_with_mixed_deck(self):
        session = Session(
            42,
            p1_deck=MIXED_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        p1_cards = all_player_cards(session.state.players["P1"])
        p2_cards = all_player_cards(session.state.players["P2"])

        self.assertEqual(50, len(p1_cards))
        self.assertEqual(8, sum(
            isinstance(card.definition, ClimaxDefinition)
            for card in p1_cards
        ))
        self.assertEqual(50, len(p2_cards))
        self.assertEqual(0, sum(
            isinstance(card.definition, ClimaxDefinition)
            for card in p2_cards
        ))

    def test_both_players_can_start_with_mixed_decks(self):
        session = Session(
            42,
            p1_deck=MIXED_DECK,
            p2_deck=MIXED_DECK,
        )

        for player in session.state.players.values():
            cards = all_player_cards(player)
            self.assertEqual(50, len(cards))
            self.assertEqual(50, len({card.instance_id for card in cards}))
            self.assertEqual(8, sum(
                card.definition.card_number == "T-002"
                for card in cards
            ))

        p1_ids = {
            card.instance_id
            for card in all_player_cards(session.state.players["P1"])
        }
        p2_ids = {
            card.instance_id
            for card in all_player_cards(session.state.players["P2"])
        }
        self.assertTrue(p1_ids.isdisjoint(p2_ids))

    def test_mixed_deck_initialization_is_safe_across_many_seeds(self):
        saw_climax_in_opening_hand = False
        saw_climax_on_deck_top = False

        for seed in range(64):
            session = Session(
                seed,
                p1_deck=MIXED_DECK,
                p2_deck=MIXED_DECK,
            )

            for player in session.state.players.values():
                if any(
                    card.definition.card_type is CardType.CLIMAX
                    for card in player.hand
                ):
                    saw_climax_in_opening_hand = True

                if (
                    player.deck
                    and player.deck[0].definition.card_type is CardType.CLIMAX
                ):
                    saw_climax_on_deck_top = True

                self.assertEqual(
                    50,
                    len(all_player_cards(player)),
                )

        self.assertTrue(saw_climax_in_opening_hand)
        self.assertTrue(saw_climax_on_deck_top)

    def test_climax_card_can_be_mulliganed_as_a_card(self):
        session = None
        climax = None

        for seed in range(256):
            candidate = Session(
                seed,
                p1_deck=MIXED_DECK,
                p2_deck=DEFAULT_TEST_DECK,
            )
            actor = candidate.state.actor
            if actor == "P1":
                climax = next(
                    (
                        card
                        for card in candidate.state.players["P1"].hand
                        if card.definition.card_type is CardType.CLIMAX
                    ),
                    None,
                )
                if climax is not None:
                    session = candidate
                    break

        self.assertIsNotNone(session)
        self.assertIsNotNone(climax)

        before_ids = {
            card.instance_id
            for card in all_player_cards(session.state.players["P1"])
        }

        session.dispatch(
            MulliganAction("P1", (climax.instance_id,))
        )

        player = session.state.players["P1"]
        after_ids = {
            card.instance_id
            for card in all_player_cards(player)
        }

        self.assertEqual(before_ids, after_ids)
        self.assertEqual(50, len(after_ids))
        self.assertIn(
            climax.instance_id,
            {card.instance_id for card in player.waiting_room},
        )

    def test_mixed_deck_can_complete_mulligan_and_enter_turn_framework(self):
        session = Session(
            42,
            p1_deck=MIXED_DECK,
            p2_deck=MIXED_DECK,
        )

        for _ in range(2):
            actor = session.state.actor
            session.dispatch(MulliganAction(actor, ()))

        self.assertEqual(2, session.state.mulligans_completed)
        self.assertEqual(1, session.state.turn_number)
        self.assertEqual("stand", session.state.phase)

        # Stand -> Draw. Drawing a Climax must still be safe because drawing is
        # a generic card movement and does not inspect character-only fields.
        session.dispatch(
            AdvancePhaseAction(session.state.current_player)
        )

        self.assertEqual("draw", session.state.phase)

        for player in session.state.players.values():
            cards = all_player_cards(player)
            self.assertEqual(50, len(cards))
            self.assertEqual(50, len({card.instance_id for card in cards}))

    def test_replay_distinguishes_mixed_deck_from_default_deck(self):
        session = Session(
            42,
            p1_deck=MIXED_DECK,
            p2_deck=DEFAULT_TEST_DECK,
        )

        for _ in range(2):
            session.dispatch(
                MulliganAction(session.state.actor, ())
            )

        session.dispatch(
            AdvancePhaseAction(session.state.current_player)
        )

        data = json.loads(json.dumps(session.replay_data()))
        restored = Session.from_replay(data)

        self.assertEqual(
            {
                "P1": MIXED_DECK,
                "P2": DEFAULT_TEST_DECK,
            },
            restored.deck_sources,
        )
        self.assertEqual(session.state, restored.state)
        self.assertEqual(session.events, restored.events)
        self.assertEqual(session.hashes, restored.hashes)

        p1_cards = all_player_cards(restored.state.players["P1"])
        p2_cards = all_player_cards(restored.state.players["P2"])

        self.assertEqual(
            8,
            sum(card.definition.card_number == "T-002" for card in p1_cards),
        )
        self.assertEqual(
            0,
            sum(card.definition.card_number == "T-002" for card in p2_cards),
        )


if __name__ == "__main__":
    unittest.main()
