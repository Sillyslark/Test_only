import unittest

from resolution import ResolutionContext, TriggeredEffect, resolve_pending_effects


class ResolutionTests(unittest.TestCase):
    def test_turn_player_pool_is_exhausted_before_non_turn_player(self):
        context = ResolutionContext("P1", "P2", 0)
        context.add_effect(TriggeredEffect("P1-A", "P1"))
        context.add_effect(TriggeredEffect("P1-B", "P1"))
        context.add_effect(TriggeredEffect("P2-A", "P2"))

        order = []

        def choose_effect(player_id, pool):
            return pool[0]

        def resolve_effect(effect, ctx):
            order.append(effect.effect_id)
            if effect.effect_id == "P1-A":
                # A newly triggered turn-player effect must stay ahead of P2.
                ctx.add_effect(TriggeredEffect("P1-C", "P1"))

        resolve_pending_effects(
            context,
            choose_effect=choose_effect,
            resolve_effect=resolve_effect,
        )

        self.assertEqual(["P1-A", "P1-B", "P1-C", "P2-A"], order)
        self.assertEqual([], context.turn_player_pool)
        self.assertEqual([], context.non_turn_player_pool)

    def test_resolution_point_captures_only_new_events(self):
        session_events = [
            {"kind": "old"},
            {"kind": "older"},
        ]
        context = ResolutionContext("P1", "P2", len(session_events))

        session_events.append({"kind": "card_moved"})
        first = context.capture_new_events(session_events)

        session_events.append({"kind": "card_played"})
        second = context.capture_new_events(session_events)

        self.assertEqual([{"kind": "card_moved"}], first)
        self.assertEqual([{"kind": "card_played"}], second)
        self.assertEqual(
            [{"kind": "card_moved"}, {"kind": "card_played"}],
            context.events,
        )


if __name__ == "__main__":
    unittest.main()
