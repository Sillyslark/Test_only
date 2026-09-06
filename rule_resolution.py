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


def level_up_candidates(player):
    """Return the seven cards eligible for one level-up, top-first within that group.

    Storage convention is top-first for every ordered zone. Therefore the
    eligible group is always the bottom seven cards of Clock.
    """
    if len(player.clock) < 7:
        return ()
    return tuple(player.clock[-7:])


def resolve_level_up(player, player_id, choose_level_card, move_to_level, move_to_waiting):
    """Resolve one level-up if Clock contains at least seven cards.

    The eligible cards are the bottom seven cards of Clock. ``choose_level_card``
    returns the instance_id of the card that becomes the new Level card.
    All six remaining eligible cards move individually to Waiting Room.

    This function resolves exactly one level-up. The engine's interrupt loop is
    responsible for calling it again while Clock still contains seven or more.
    """
    if not callable(choose_level_card):
        raise ValueError("choose_level_card 必须是可调用对象")
    if not callable(move_to_level) or not callable(move_to_waiting):
        raise ValueError("升级移动回调必须是可调用对象")

    candidates = level_up_candidates(player)
    if not candidates:
        return None

    candidate_ids = tuple(card.instance_id for card in candidates)
    chosen_id = choose_level_card(player_id, candidates)

    if chosen_id not in candidate_ids:
        raise ValueError("升级选择必须来自计时区底部七张牌")

    # Move the selected Level card first.
    move_to_level(chosen_id)

    # Preserve the remaining eligible cards' relative top-first order while
    # inserting this whole batch at the top of Waiting Room.
    discarded_ids = tuple(card_id for card_id in candidate_ids if card_id != chosen_id)
    for destination_index, card_id in enumerate(discarded_ids):
        move_to_waiting(card_id, destination_index)

    return {
        "player": player_id,
        "candidates": candidate_ids,
        "chosen": chosen_id,
        "discarded": discarded_ids,
    }


def resolve_refresh(player, player_id, move_to_deck, shuffle_deck, move_refresh_point):
    """Resolve one deck refresh.

    All cards in Waiting Room are moved to Deck one-by-one, then Deck is
    shuffled, then the new top card is moved to Clock as the refresh point.

    This function resolves exactly one refresh. Any further interrupt checks
    (for example Level Up caused by the refresh point) are owned by the engine.
    """
    if player.deck:
        return None
    if not player.waiting_room:
        return None
    if not callable(move_to_deck) or not callable(shuffle_deck) or not callable(move_refresh_point):
        raise ValueError("刷新回调必须是可调用对象")

    waiting_ids = tuple(card.instance_id for card in player.waiting_room)

    for card_id in waiting_ids:
        move_to_deck(card_id)

    shuffle_deck()

    if not player.deck:
        raise RuntimeError("刷新后牌库为空")

    refresh_point = move_refresh_point()

    return {
        "player": player_id,
        "recycled": waiting_ids,
        "refresh_point": refresh_point.instance_id,
    }
