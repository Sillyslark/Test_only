import sys

# Windows DPI awareness.
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import pygame


# ============================================================
# Basic geometry
# ============================================================

FPS = 60

# Geometric origin used for constructing the lower half.
# The final visible canvas is cropped dynamically around all geometry,
# so these values do NOT determine the final canvas size.
STAGE_CENTER = pygame.Vector2(600, 450)

CELL_SIZE = 150
CELL_GAP = round(CELL_SIZE * 0.10)     # 15
CELL_PITCH = CELL_SIZE + CELL_GAP      # 165

# 63:88 card region. Long side equals the square-grid side.
CARD_LONG = CELL_SIZE                  # 150
CARD_SHORT = round(CARD_LONG * 63 / 88)  # 107

BOARD_MARGIN = CELL_GAP

# Reserved side columns for future controls/debug information.
# Total canvas width is derived from the central gameplay-board height
# using a target 16:9 aspect ratio. The remaining width is split equally.
TARGET_ASPECT_W = 16
TARGET_ASPECT_H = 9
SIDE_PANEL_INNER_MARGIN = 18

# Hand display is a UI browsing area, so cards are intentionally smaller
# than rule-zone cards.
HAND_VISIBLE_COUNT = 7
HAND_CARD_SCALE = 0.75
HAND_CARD_W = round(CARD_SHORT * HAND_CARD_SCALE)
HAND_CARD_H = round(CARD_LONG * HAND_CARD_SCALE)
HAND_CARD_GAP = 10
HAND_ARROW_W = 42
HAND_SIDE_PADDING = 12
HAND_STATUS_H = 24
HAND_TOP_GAP = CELL_GAP
# Demo-only hand sizes for this UI mockup.
# Change these independently to test each side.
LOWER_HAND_TOTAL_COUNT = 12
UPPER_HAND_TOTAL_COUNT = 5


# ============================================================
# Helpers
# ============================================================

def move_rect(rect, dx, dy):
    moved = rect.copy()
    moved.move_ip(round(dx), round(dy))
    return moved


def mirror_rect_about_stage_center(rect):
    """Exact 180-degree central symmetry around STAGE_CENTER."""
    mirrored = rect.copy()
    mirrored.left = round(2 * STAGE_CENTER.x - rect.right)
    mirrored.top = round(2 * STAGE_CENTER.y - rect.bottom)
    return mirrored


def bounding_rect(rects, margin=0):
    left = min(r.left for r in rects) - margin
    top = min(r.top for r in rects) - margin
    right = max(r.right for r in rects) + margin
    bottom = max(r.bottom for r in rects) + margin
    return pygame.Rect(left, top, right - left, bottom - top)


# ============================================================
# Stage card slots
# ============================================================

class CardSlot:
    def __init__(self, name, center, orientation=0):
        self.name = name
        self.center = pygame.Vector2(center)
        self.orientation = orientation % 360

    def cell_rect(self):
        rect = pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE)
        rect.center = (round(self.center.x), round(self.center.y))
        return rect

    def card_rect(self):
        if self.orientation in (0, 180):
            w, h = CARD_SHORT, CARD_LONG
        else:
            w, h = CARD_LONG, CARD_SHORT

        rect = pygame.Rect(0, 0, w, h)
        rect.center = (round(self.center.x), round(self.center.y))
        return rect

    def draw(self, surface, font, small_font, offset):
        ox, oy = offset
        cell = move_rect(self.cell_rect(), ox, oy)
        card = move_rect(self.card_rect(), ox, oy)

        pygame.draw.rect(surface, (120, 125, 132), cell, 2)
        pygame.draw.rect(surface, (238, 238, 238), card)
        pygame.draw.rect(surface, (45, 45, 45), card, 2)

        pygame.draw.polygon(
            surface,
            (55, 105, 225),
            self._top_marker(card),
        )

        label = font.render(self.name, True, (20, 20, 20))
        surface.blit(
            label,
            label.get_rect(center=(card.centerx, card.centery - 9)),
        )

        angle = small_font.render(
            f"{self.orientation}°",
            True,
            (75, 75, 75),
        )
        surface.blit(
            angle,
            angle.get_rect(center=(card.centerx, card.centery + 15)),
        )

    def _top_marker(self, rect):
        cx, cy = rect.center
        margin = 7
        half = 8
        depth = 12

        if self.orientation == 0:
            y = rect.top + margin
            return [(cx, y), (cx-half, y+depth), (cx+half, y+depth)]

        if self.orientation == 90:
            x = rect.left + margin
            return [(x, cy), (x+depth, cy-half), (x+depth, cy+half)]

        if self.orientation == 180:
            y = rect.bottom - margin
            return [(cx, y), (cx-half, y-depth), (cx+half, y-depth)]

        x = rect.right - margin
        return [(x, cy), (x-depth, cy-half), (x-depth, cy+half)]


def build_stage_slots():
    cx = STAGE_CENTER.x
    cy = STAGE_CENTER.y

    p2_back_y = cy - CELL_PITCH * 1.5
    p2_front_y = cy - CELL_PITCH * 0.5
    p1_front_y = cy + CELL_PITCH * 0.5
    p1_back_y = cy + CELL_PITCH * 1.5

    return [
        CardSlot("P2 BACK L", (cx - CELL_PITCH / 2, p2_back_y), 180),
        CardSlot("P2 BACK R", (cx + CELL_PITCH / 2, p2_back_y), 180),

        CardSlot("P2 FRONT L", (cx - CELL_PITCH, p2_front_y), 180),
        CardSlot("P2 FRONT C", (cx, p2_front_y), 180),
        CardSlot("P2 FRONT R", (cx + CELL_PITCH, p2_front_y), 180),

        CardSlot("P1 FRONT L", (cx - CELL_PITCH, p1_front_y), 0),
        CardSlot("P1 FRONT C", (cx, p1_front_y), 0),
        CardSlot("P1 FRONT R", (cx + CELL_PITCH, p1_front_y), 0),

        CardSlot("P1 BACK L", (cx - CELL_PITCH / 2, p1_back_y), 0),
        CardSlot("P1 BACK R", (cx + CELL_PITCH / 2, p1_back_y), 0),
    ]


# ============================================================
# Auxiliary zones
# ============================================================

def build_lower_aux_zones():
    """
    Define ONLY the lower half.

    Level zone:
      4 landscape rectangles, vertical stack, 2/3 overlap.

    Clock zone:
      6 portrait rectangles, horizontal stack, 2/3 overlap.
      First rectangle's left edge aligns with P1 BACK L square.
      The rightmost rectangle is drawn last and is fully visible.

    After both groups are generated, their BOTTOM edges are aligned
    to whichever group originally extends farther downward.
    """
    cx = STAGE_CENTER.x
    cy = STAGE_CENTER.y

    # --------------------------------------------------------
    # Front row
    # --------------------------------------------------------
    p1_front_y = cy + CELL_PITCH * 0.5
    front_left_center_x = cx - CELL_PITCH
    front_right_center_x = cx + CELL_PITCH

    front_left_edge = front_left_center_x - CELL_SIZE / 2
    front_right_edge = front_right_center_x + CELL_SIZE / 2
    front_top = p1_front_y - CELL_SIZE / 2

    inventory = pygame.Rect(
        round(front_left_edge - CELL_GAP - CARD_LONG),
        round(front_top),
        CARD_LONG,
        CARD_SHORT,
    )

    memory = pygame.Rect(
        round(front_right_edge + CELL_GAP),
        round(front_top),
        CARD_LONG,
        CARD_SHORT,
    )

    # --------------------------------------------------------
    # Back row
    # --------------------------------------------------------
    p1_back_y = cy + CELL_PITCH * 1.5
    back_left_center_x = cx - CELL_PITCH / 2
    back_left_edge = back_left_center_x - CELL_SIZE / 2
    back_top = p1_back_y - CELL_SIZE / 2
    back_bottom = back_top + CELL_SIZE

    climax = pygame.Rect(
        round(back_left_edge - CELL_GAP - CARD_LONG),
        round(back_top),
        CARD_LONG,
        CARD_SHORT,
    )

    # --------------------------------------------------------
    # Right column: 思出区 -> 卡组 -> 控制室
    # --------------------------------------------------------
    right_edge = memory.right

    deck = pygame.Rect(
        round(right_edge - CARD_SHORT),
        round(memory.bottom + CELL_GAP),
        CARD_SHORT,
        CARD_LONG,
    )

    control = pygame.Rect(
        round(right_edge - CARD_SHORT),
        round(deck.bottom + CELL_GAP),
        CARD_SHORT,
        CARD_LONG,
    )

    # --------------------------------------------------------
    # Level zone below climax:
    # 4 landscape rectangles.
    # 2/3 overlap => step = 1/3 of rectangle height.
    # --------------------------------------------------------
    level_step = CARD_SHORT / 3
    level_y0 = climax.bottom + CELL_GAP

    level_rects = [
        pygame.Rect(
            round(climax.left),
            round(level_y0 + i * level_step),
            CARD_LONG,
            CARD_SHORT,
        )
        for i in range(4)
    ]

    # --------------------------------------------------------
    # Clock zone below P1 BACK L:
    # 6 portrait rectangles, horizontally overlapping.
    # 2/3 overlap => step = 1/3 of rectangle width.
    # Left edge aligns with the BACK L square.
    # --------------------------------------------------------
    clock_step = CARD_SHORT / 3
    clock_x0 = round(back_left_edge)
    clock_y0 = round(back_bottom + CELL_GAP)

    clock_rects = [
        pygame.Rect(
            round(clock_x0 + i * clock_step),
            clock_y0,
            CARD_SHORT,
            CARD_LONG,
        )
        for i in range(6)
    ]

    # --------------------------------------------------------
    # Bottom alignment:
    # whichever group is higher is moved down to match the lower group.
    # --------------------------------------------------------
    level_bottom = max(r.bottom for r in level_rects)
    clock_bottom = max(r.bottom for r in clock_rects)
    target_bottom = max(level_bottom, clock_bottom)

    if level_bottom < target_bottom:
        dy = target_bottom - level_bottom
        level_rects = [move_rect(r, 0, dy) for r in level_rects]

    if clock_bottom < target_bottom:
        dy = target_bottom - clock_bottom
        clock_rects = [move_rect(r, 0, dy) for r in clock_rects]

    single_zones = [
        ("库存区", inventory),
        ("思出区", memory),
        ("高潮区", climax),
        ("卡组", deck),
        ("控制室", control),
    ]

    level_zones = [("等级区", r) for r in level_rects]
    clock_zones = [("计时区", r) for r in clock_rects]

    return single_zones, level_zones, clock_zones


def build_all_aux_zones():
    lower_single, lower_level, lower_clock = build_lower_aux_zones()

    upper_single = [
        (label, mirror_rect_about_stage_center(rect))
        for label, rect in lower_single
    ]
    upper_level = [
        (label, mirror_rect_about_stage_center(rect))
        for label, rect in lower_level
    ]
    upper_clock = [
        (label, mirror_rect_about_stage_center(rect))
        for label, rect in lower_clock
    ]

    return {
        "lower_single": lower_single,
        "lower_level": lower_level,
        "lower_clock": lower_clock,
        "upper_single": upper_single,
        "upper_level": upper_level,
        "upper_clock": upper_clock,
    }



# ============================================================
# Hand area
# ============================================================

def gameplay_bottom(zones):
    """
    Bottom edge of lower-half gameplay zones, excluding the hand UI.
    """
    lower_groups = (
        zones["lower_single"]
        + zones["lower_level"]
        + zones["lower_clock"]
    )
    return max(rect.bottom for _, rect in lower_groups)


def gameplay_horizontal_bounds(slots, zones):
    """
    Horizontal extent of the lower-half gameplay geometry.
    The hand strip uses this as its preferred available width.
    """
    rects = [slot.cell_rect() for slot in slots if slot.center.y >= STAGE_CENTER.y]
    rects.extend(rect for _, rect in zones["lower_single"])
    rects.extend(rect for _, rect in zones["lower_level"])
    rects.extend(rect for _, rect in zones["lower_clock"])

    left = min(r.left for r in rects)
    right = max(r.right for r in rects)
    return left, right


def build_lower_hand_area(slots, zones):
    """
    Create a fixed-size horizontal hand viewport.

    - Up to 7 cards are visible at once.
    - Cards do not overlap.
    - The viewport width does not grow when hand size exceeds 7.
    - The hand strip sits below the lower gameplay geometry.
    """
    left_bound, right_bound = gameplay_horizontal_bounds(slots, zones)
    preferred_center_x = (left_bound + right_bound) / 2

    cards_width = (
        HAND_VISIBLE_COUNT * HAND_CARD_W
        + (HAND_VISIBLE_COUNT - 1) * HAND_CARD_GAP
    )

    viewport_w = (
        HAND_ARROW_W * 2
        + HAND_SIDE_PADDING * 4
        + cards_width
    )
    viewport_h = HAND_CARD_H + HAND_SIDE_PADDING * 2 + HAND_STATUS_H

    top = gameplay_bottom(zones) + HAND_TOP_GAP
    left = round(preferred_center_x - viewport_w / 2)

    container = pygame.Rect(
        left,
        round(top),
        viewport_w,
        viewport_h,
    )

    left_arrow = pygame.Rect(
        container.left + HAND_SIDE_PADDING,
        container.centery - 24,
        HAND_ARROW_W,
        48,
    )

    right_arrow = pygame.Rect(
        container.right - HAND_SIDE_PADDING - HAND_ARROW_W,
        container.centery - 24,
        HAND_ARROW_W,
        48,
    )

    cards_left = left_arrow.right + HAND_SIDE_PADDING
    cards_top = container.top + HAND_SIDE_PADDING

    card_rects = []
    for i in range(HAND_VISIBLE_COUNT):
        card_rects.append(
            pygame.Rect(
                cards_left + i * (HAND_CARD_W + HAND_CARD_GAP),
                cards_top,
                HAND_CARD_W,
                HAND_CARD_H,
            )
        )

    return {
        "container": container,
        "left_arrow": left_arrow,
        "right_arrow": right_arrow,
        "card_rects": card_rects,
    }


def mirror_hand_area(lower_hand):
    """
    Upper hand geometry is an exact central-symmetry copy of the lower one.
    Text/card labels themselves remain upright when drawn.
    """
    return {
        "container": mirror_rect_about_stage_center(lower_hand["container"]),
        "left_arrow": mirror_rect_about_stage_center(lower_hand["left_arrow"]),
        "right_arrow": mirror_rect_about_stage_center(lower_hand["right_arrow"]),
        "card_rects": [
            mirror_rect_about_stage_center(r)
            for r in lower_hand["card_rects"]
        ],
    }


def hand_geometry_rects(hand_areas):
    rects = []
    for hand in hand_areas.values():
        rects.append(hand["container"])
        rects.append(hand["left_arrow"])
        rects.append(hand["right_arrow"])
        rects.extend(hand["card_rects"])
    return rects


# ============================================================
# Dynamic canvas
# ============================================================

def all_geometry_rects(slots, zones, hand_areas):
    rects = [slot.cell_rect() for slot in slots]

    for group in zones.values():
        rects.extend(rect for _, rect in group)

    rects.extend(hand_geometry_rects(hand_areas))
    return rects


def compute_canvas_world_rect(slots, zones, hand_areas):
    """
    The actual logical canvas is the outer bounding box of ALL geometry,
    expanded by the same margin on every side.

    This fixes the previous clipping problem: the Surface itself now
    grows/shrinks with the geometry instead of remaining 1200x900.
    """
    return bounding_rect(
        all_geometry_rects(slots, zones, hand_areas),
        BOARD_MARGIN,
    )


# ============================================================
# Drawing
# ============================================================

def draw_labeled_rect(surface, rect, label_text, font, offset):
    shown = move_rect(rect, *offset)
    pygame.draw.rect(surface, (238, 238, 238), shown)
    pygame.draw.rect(surface, (45, 45, 45), shown, 2)

    label = font.render(label_text, True, (20, 20, 20))
    surface.blit(label, label.get_rect(center=shown.center))


def draw_overlapping_group(
    surface,
    group,
    font,
    offset,
    label_on_last=True,
):
    """
    Draw in list order so the last rectangle appears on top.
    This makes the rightmost clock rectangle fully visible.
    """
    for i, (label_text, rect) in enumerate(group):
        shown = move_rect(rect, *offset)

        pygame.draw.rect(surface, (238, 238, 238), shown)
        pygame.draw.rect(surface, (45, 45, 45), shown, 2)

        if label_on_last and i != len(group) - 1:
            continue

        label = font.render(label_text, True, (20, 20, 20))
        surface.blit(label, label.get_rect(center=shown.center))



def draw_hand(
    surface,
    hand,
    font,
    small_font,
    offset,
    scroll_index,
    total_count,
    upper_side=False,
):
    container = move_rect(hand["container"], *offset)
    left_arrow = move_rect(hand["left_arrow"], *offset)
    right_arrow = move_rect(hand["right_arrow"], *offset)
    slot_rects = [move_rect(r, *offset) for r in hand["card_rects"]]

    # Container
    pygame.draw.rect(surface, (222, 225, 229), container)
    pygame.draw.rect(surface, (75, 75, 78), container, 2)

    # Status strip:
    # lower player -> bottom
    # upper/opponent -> top
    if upper_side:
        status_rect = pygame.Rect(
            container.left,
            container.top,
            container.width,
            HAND_STATUS_H,
        )
        pygame.draw.line(
            surface,
            (150, 150, 150),
            (status_rect.left, status_rect.bottom),
            (status_rect.right, status_rect.bottom),
            1,
        )
    else:
        status_rect = pygame.Rect(
            container.left,
            container.bottom - HAND_STATUS_H,
            container.width,
            HAND_STATUS_H,
        )
        pygame.draw.line(
            surface,
            (150, 150, 150),
            (status_rect.left, status_rect.top),
            (status_rect.right, status_rect.top),
            1,
        )

    # Clamp scroll position.
    last_start = max(0, total_count - HAND_VISIBLE_COUNT)
    scroll_index = max(0, min(scroll_index, last_start))

    visible_count = min(HAND_VISIBLE_COUNT, total_count)

    if total_count <= HAND_VISIBLE_COUNT:
        visible_numbers = list(range(1, total_count + 1))
    else:
        visible_numbers = list(
            range(
                scroll_index + 1,
                scroll_index + visible_count + 1,
            )
        )

    # Arrow states.
    can_scroll_left = total_count > HAND_VISIBLE_COUNT and scroll_index > 0
    can_scroll_right = (
        total_count > HAND_VISIBLE_COUNT
        and scroll_index < last_start
    )

    def draw_arrow_button(rect, direction, enabled):
        fill = (235, 235, 235) if enabled else (205, 205, 205)
        border = (55, 55, 55) if enabled else (145, 145, 145)
        arrow_color = (25, 25, 25) if enabled else (135, 135, 135)

        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 2)

        cx, cy = rect.center
        half_h = 10
        half_w = 8

        if direction == "left":
            points = [
                (cx - half_w, cy),
                (cx + half_w, cy - half_h),
                (cx + half_w, cy + half_h),
            ]
        else:
            points = [
                (cx + half_w, cy),
                (cx - half_w, cy - half_h),
                (cx - half_w, cy + half_h),
            ]

        pygame.draw.polygon(surface, arrow_color, points)

    # Upper side visually swaps the arrow directions.
    if upper_side:
        draw_arrow_button(left_arrow, "right", can_scroll_right)
        draw_arrow_button(right_arrow, "left", can_scroll_left)
    else:
        draw_arrow_button(left_arrow, "left", can_scroll_left)
        draw_arrow_button(right_arrow, "right", can_scroll_right)

    # Only draw as many card rectangles as actually exist.
    # For <=7 cards, center them within the 7-card display span.
    if visible_count > 0:
        total_slots_width = (
            HAND_VISIBLE_COUNT * HAND_CARD_W
            + (HAND_VISIBLE_COUNT - 1) * HAND_CARD_GAP
        )
        actual_cards_width = (
            visible_count * HAND_CARD_W
            + max(0, visible_count - 1) * HAND_CARD_GAP
        )

        first_slot_left = min(rect.left for rect in slot_rects)
        centered_left = first_slot_left + (total_slots_width - actual_cards_width) // 2

        card_rects = [
            pygame.Rect(
                centered_left + i * (HAND_CARD_W + HAND_CARD_GAP),
                slot_rects[0].top,
                HAND_CARD_W,
                HAND_CARD_H,
            )
            for i in range(visible_count)
        ]
    else:
        card_rects = []

    for i, rect in enumerate(card_rects):
        pygame.draw.rect(surface, (247, 247, 247), rect)
        pygame.draw.rect(surface, (45, 45, 45), rect, 2)

        number = visible_numbers[i]
        title = font.render(f"手牌 {number}", True, (20, 20, 20))
        surface.blit(
            title,
            title.get_rect(center=(rect.centerx, rect.centery - 8)),
        )

        pos = small_font.render(
            f"{number}/{total_count}" if total_count > 0 else "0/0",
            True,
            (80, 80, 80),
        )
        surface.blit(
            pos,
            pos.get_rect(center=(rect.centerx, rect.centery + 14)),
        )

    # Status text
    if total_count == 0:
        status_text = "手牌 0 张"
    elif total_count <= HAND_VISIBLE_COUNT:
        status_text = f"手牌 {total_count} 张 · 全部显示"
    else:
        status_text = (
            f"手牌 {total_count} 张 · 显示 "
            f"{scroll_index + 1}-{scroll_index + visible_count}"
        )

    status = small_font.render(
        status_text,
        True,
        (60, 60, 60),
    )
    surface.blit(
        status,
        status.get_rect(center=status_rect.center),
    )


def render_board(slots, zones, hand_areas, font, small_font, lower_scroll_index, upper_scroll_index):
    world_rect = compute_canvas_world_rect(slots, zones, hand_areas)

    # The central gameplay board remains dynamically sized.
    board_w, board_h = world_rect.size

    # Derive the target total width from the central-board height
    # using the desired overall 16:9 canvas aspect ratio.
    target_total_width = round(
        board_h * TARGET_ASPECT_W / TARGET_ASPECT_H
    )

    # Remaining width is split equally between the two side columns.
    # If the central board is already wider than the target aspect,
    # side columns collapse to zero instead of becoming negative.
    side_panel_width = max(
        0,
        round((target_total_width - board_w) / 2),
    )

    canvas_w = board_w + side_panel_width * 2
    canvas_h = board_h

    canvas = pygame.Surface((canvas_w, canvas_h))

    # Side panels deliberately use a darker background so they are visually
    # distinct from the gameplay board.
    canvas.fill((45, 48, 54))

    central_board_rect = pygame.Rect(
        side_panel_width,
        0,
        board_w,
        board_h,
    )
    pygame.draw.rect(
        canvas,
        (205, 209, 214),
        central_board_rect,
    )

    # Translate world coordinates into the central-board portion of canvas.
    offset = (
        side_panel_width - world_rect.left,
        -world_rect.top,
    )

    # Strong separators between side panels and central gameplay board.
    pygame.draw.line(
        canvas,
        (235, 235, 235),
        (central_board_rect.left, 0),
        (central_board_rect.left, canvas_h),
        3,
    )
    pygame.draw.line(
        canvas,
        (235, 235, 235),
        (central_board_rect.right - 1, 0),
        (central_board_rect.right - 1, canvas_h),
        3,
    )

    # Subtle outer border around the central gameplay board.
    pygame.draw.rect(
        canvas,
        (245, 245, 245),
        central_board_rect,
        2,
    )

    # Center axes.
    center_x = round(STAGE_CENTER.x + offset[0])
    center_y = round(STAGE_CENTER.y + offset[1])

    pygame.draw.line(
        canvas,
        (145, 145, 145),
        (central_board_rect.left, center_y),
        (central_board_rect.right, center_y),
        1,
    )
    pygame.draw.line(
        canvas,
        (145, 145, 145),
        (center_x, central_board_rect.top),
        (center_x, central_board_rect.bottom),
        1,
    )

    pygame.draw.circle(
        canvas,
        (95, 95, 95),
        (center_x, center_y),
        4,
    )

    for slot in slots:
        slot.draw(canvas, font, small_font, offset)

    # Non-overlapping zones.
    for group_name in ("lower_single", "upper_single"):
        for label_text, rect in zones[group_name]:
            draw_labeled_rect(
                canvas,
                rect,
                label_text,
                font,
                offset,
            )

    # Level zones: vertical overlapping stack.
    draw_overlapping_group(
        canvas,
        zones["lower_level"],
        font,
        offset,
    )
    draw_overlapping_group(
        canvas,
        zones["upper_level"],
        font,
        offset,
    )

    # Clock zones: horizontal overlapping stack.
    # List order is left -> right for lower half, so rightmost is fully visible.
    draw_overlapping_group(
        canvas,
        zones["lower_clock"],
        font,
        offset,
    )
    draw_overlapping_group(
        canvas,
        zones["upper_clock"],
        font,
        offset,
    )

    # Hand areas are UI strips outside the gameplay geometry.
    draw_hand(
        canvas,
        hand_areas["lower"],
        font,
        small_font,
        offset,
        lower_scroll_index,
        total_count=LOWER_HAND_TOTAL_COUNT,
    )
    draw_hand(
        canvas,
        hand_areas["upper"],
        font,
        small_font,
        offset,
        upper_scroll_index,
        total_count=UPPER_HAND_TOTAL_COUNT,
        upper_side=True,
    )

    # Temporary labels: these columns are intentionally empty for now.
    left_panel_label = font.render(
        "LEFT DEBUG / CONTROL AREA",
        True,
        (205, 205, 205),
    )
    right_panel_label = font.render(
        "RIGHT INFO / DEBUG AREA",
        True,
        (205, 205, 205),
    )

    canvas.blit(
        left_panel_label,
        (
            SIDE_PANEL_INNER_MARGIN,
            SIDE_PANEL_INNER_MARGIN,
        ),
    )
    canvas.blit(
        right_panel_label,
        (
            central_board_rect.right + SIDE_PANEL_INNER_MARGIN,
            SIDE_PANEL_INNER_MARGIN,
        ),
    )

    return canvas, world_rect


# ============================================================
# Fonts
# ============================================================

def make_fonts():
    chinese_fonts = [
        "Microsoft YaHei",
        "Microsoft YaHei UI",
        "SimHei",
        "SimSun",
    ]

    available_fonts = set(pygame.font.get_fonts())
    selected_font = None

    for candidate in chinese_fonts:
        normalized = candidate.lower().replace(" ", "")
        if normalized in available_fonts:
            selected_font = candidate
            break

    if selected_font is None:
        selected_font = "Microsoft YaHei"

    return (
        pygame.font.SysFont(selected_font, 14),
        pygame.font.SysFont(selected_font, 13),
    )



def window_to_board_pos(mouse_pos, screen_size, board_size):
    """
    Convert mouse position in the resizable OS window into coordinates
    on the dynamically rendered board surface.
    Returns None when the pointer is in letterbox/pillarbox space.
    """
    window_w, window_h = screen_size
    board_w, board_h = board_size

    scale = min(window_w / board_w, window_h / board_h)

    scaled_w = round(board_w * scale)
    scaled_h = round(board_h * scale)

    offset_x = (window_w - scaled_w) // 2
    offset_y = (window_h - scaled_h) // 2

    mx, my = mouse_pos

    if not (
        offset_x <= mx < offset_x + scaled_w
        and offset_y <= my < offset_y + scaled_h
    ):
        return None

    bx = (mx - offset_x) / scale
    by = (my - offset_y) / scale
    return pygame.Vector2(bx, by)


# ============================================================
# Main
# ============================================================

def main():
    pygame.init()

    font, small_font = make_fonts()

    slots = build_stage_slots()
    zones = build_all_aux_zones()

    lower_hand = build_lower_hand_area(slots, zones)
    hand_areas = {
        "lower": lower_hand,
        "upper": mirror_hand_area(lower_hand),
    }

    lower_scroll_index = 0
    upper_scroll_index = 0

    # Render once to determine the true geometry-based aspect ratio.
    board, world_rect = render_board(
        slots,
        zones,
        hand_areas,
        font,
        small_font,
        lower_scroll_index,
        upper_scroll_index,
    )

    # Initial window follows the dynamically computed board size.
    # Limit only for practical desktop use; resize still preserves aspect ratio.
    initial_scale = min(
        1920 / board.get_width(),
        1080 / board.get_height()
    )
    initial_w = max(1, round(board.get_width() * initial_scale))
    initial_h = max(1, round(board.get_height() * initial_scale))

    screen = pygame.display.set_mode(
        (initial_w, initial_h),
        pygame.RESIZABLE,
    )
    pygame.display.set_caption(
        "WS Simulator - Dynamic Stage Geometry Mockup"
    )

    clock = pygame.time.Clock()

    demo_slot = next(
        slot for slot in slots
        if slot.name == "P1 FRONT C"
    )

    running = True

    while running:
        geometry_changed = False
        hand_changed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    demo_slot.orientation = 0
                    geometry_changed = True
                elif event.key == pygame.K_2:
                    demo_slot.orientation = 90
                    geometry_changed = True
                elif event.key == pygame.K_3:
                    demo_slot.orientation = 180
                    geometry_changed = True
                elif event.key == pygame.K_4:
                    demo_slot.orientation = 270
                    geometry_changed = True
                elif event.key == pygame.K_LEFT:
                    if lower_scroll_index > 0:
                        lower_scroll_index -= 1
                        hand_changed = True
                elif event.key == pygame.K_RIGHT:
                    lower_last_start = max(
                        0,
                        LOWER_HAND_TOTAL_COUNT - HAND_VISIBLE_COUNT,
                    )
                    if lower_scroll_index < lower_last_start:
                        lower_scroll_index += 1
                        hand_changed = True

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board_pos = window_to_board_pos(
                    event.pos,
                    screen.get_size(),
                    board.get_size(),
                )

                if board_pos is not None:
                    # Convert board-local coordinates back into world coordinates.
                    # Side columns are outside the gameplay world's coordinates.
                    # Ignore clicks there for gameplay hit testing.
                    board_w = world_rect.width
                    board_h = world_rect.height

                    target_total_width = round(
                        board_h * TARGET_ASPECT_W / TARGET_ASPECT_H
                    )
                    side_panel_width = max(
                        0,
                        round((target_total_width - board_w) / 2),
                    )

                    central_left = side_panel_width
                    central_right = side_panel_width + board_w

                    if not (central_left <= board_pos.x < central_right):
                        continue

                    world_x = (
                        board_pos.x
                        - side_panel_width
                        + world_rect.left
                    )
                    world_y = board_pos.y + world_rect.top
                    world_pos = (world_x, world_y)

                    # Both upper and lower hand strips use the same demo scroll state.
                    lower_left = hand_areas["lower"]["left_arrow"].collidepoint(world_pos)
                    lower_right = hand_areas["lower"]["right_arrow"].collidepoint(world_pos)

                    upper_left_hit = hand_areas["upper"]["left_arrow"].collidepoint(world_pos)
                    upper_right_hit = hand_areas["upper"]["right_arrow"].collidepoint(world_pos)

                    lower_last_start = max(
                        0,
                        LOWER_HAND_TOTAL_COUNT - HAND_VISIBLE_COUNT,
                    )
                    upper_last_start = max(
                        0,
                        UPPER_HAND_TOTAL_COUNT - HAND_VISIBLE_COUNT,
                    )

                    # Lower hand controls only lower hand.
                    if lower_left and lower_scroll_index > 0:
                        lower_scroll_index -= 1
                        hand_changed = True

                    elif lower_right and lower_scroll_index < lower_last_start:
                        lower_scroll_index += 1
                        hand_changed = True

                    # Upper hand is visually mirrored:
                    # visual right = previous, visual left = next.
                    elif upper_right_hit and upper_scroll_index > 0:
                        upper_scroll_index -= 1
                        hand_changed = True

                    elif upper_left_hit and upper_scroll_index < upper_last_start:
                        upper_scroll_index += 1
                        hand_changed = True

        if geometry_changed or hand_changed:
            board, world_rect = render_board(
                slots,
                zones,
                hand_areas,
                font,
                small_font,
                lower_scroll_index,
                upper_scroll_index,
            )

        window_w, window_h = screen.get_size()

        scale = min(
            window_w / board.get_width(),
            window_h / board.get_height(),
        )

        scaled_w = max(1, round(board.get_width() * scale))
        scaled_h = max(1, round(board.get_height() * scale))

        scaled_board = pygame.transform.smoothscale(
            board,
            (scaled_w, scaled_h),
        )

        screen.fill((15, 15, 18))

        x = (window_w - scaled_w) // 2
        y = (window_h - scaled_h) // 2
        screen.blit(scaled_board, (x, y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
