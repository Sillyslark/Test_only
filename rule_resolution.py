"""Mandatory rule resolutions, run before character-entry events/effects.

Each stage zone uses top-first order: the newly placed character is index zero.
Temporary overlap is internal to an action; published state has at most one card.
"""
STAGE_SLOTS = ("front_left", "front_center", "front_right", "back_left", "back_right")


def resolve_stage_overlaps(player, player_id, move_displaced):
    """Resolve temporary Stage overlaps through the engine movement primitive.

    ``move_displaced`` is an engine-supplied callback with signature:
        move_displaced(source_slot, card_id, destination_index)

    The resolver decides *which* cards must move and in what order.
    The engine remains responsible for actually moving cards and emitting
    card_moved events.
    """
    if not callable(move_displaced):
        raise ValueError("move_displaced 必须是可调用对象")

    for slot in STAGE_SLOTS:
        cards = player.stage[slot]
        if len(cards) <= 1:
            continue

        # Snapshot IDs before mutation. The callback will mutate the Stage list.
        displaced_ids = [card.instance_id for card in cards[1:]]

        # Preserve the old behavior:
        # - cards displaced from the same slot keep their relative order;
        # - they are inserted at the top of Waiting Room.
        for destination_index, card_id in enumerate(displaced_ids):
            move_displaced(slot, card_id, destination_index)
