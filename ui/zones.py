"""Display positions retain the global top-based numbering convention."""
def clock_slots(cards):
    visible = list(reversed(list(enumerate(cards, start=1))))[:6]
    return visible + [None] * (6 - len(visible))
