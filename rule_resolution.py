"""Mandatory rule resolutions, run before character-entry events/effects.

Each stage zone uses top-first order: the newly placed character is index zero.
Temporary overlap is internal to an action; published state has at most one card.
"""
STAGE_SLOTS = ("front_left", "front_center", "front_right", "back_left", "back_right")


def resolve_stage_overlaps(player, player_id):
    events = []
    for slot in STAGE_SLOTS:
        cards = player.stage[slot]
        if len(cards) > 1:
            displaced = cards[1:]
            del cards[1:]
            player.control_room[0:0] = displaced
            for card in displaced:
                events.append({"kind": "card_moved", "player": player_id,
                               "card_id": card.instance_id, "source": slot,
                               "destination": "control_room", "reason": "stage_overlap"})
    return events
