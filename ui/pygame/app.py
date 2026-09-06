"""Live state/Action adapter using the user's v15 geometry."""
from pathlib import Path
from . import pygame_stage_grid_mock_v15 as layout
from application import Application
from actions import (StartGameAction, MulliganAction, AdvancePhaseAction, ClockAction,
                     PlayCardAction, SaveReplayAction, LoadReplayAction)
from phases import PHASES, PHASE_NAMES

pg = layout.pygame
SLOTS = {'FRONT L': 'front_left', 'FRONT C': 'front_center', 'FRONT R': 'front_right',
         'BACK L': 'back_left', 'BACK R': 'back_right'}
NAMES = dict(zip(SLOTS.values(), ('前列左', '前列中', '前列右', '后列左', '后列右')))
ZONES = {'deck': '卡组', 'control_room': '控制室', 'clock': '计时区'}


class PygameApp:
    def __init__(self, application=None):
        self.application = application or Application()
        self.view = self.application.dispatch(StartGameAction())
        self.selected = set()
        self.target = None
        self.scroll = {'P1': 0, 'P2': 0}
        self.seed_text = str(self.view.state.seed)
        self.seed_focused = False
        self.message = '开局完成，请先手选择换牌。'
        self.inspection = None
        self.page = 0
        self.hits = []
        self.dirty = True
        self.slots = layout.build_stage_slots()
        self.zones = layout.build_all_aux_zones()
        lower = layout.build_lower_hand_area(self.slots, self.zones)
        self.hands = {'P1': lower, 'P2': layout.mirror_hand_area(lower)}
        self.world = layout.compute_canvas_world_rect(self.slots, self.zones, self.hands)
        self.side = max(0, round((round(self.world.height * 16/9) - self.world.width)/2))
        self.offset = (self.side-self.world.left, -self.world.top)
        self.size = (self.world.width + 2*self.side, self.world.height)

    def dispatch(self, action):
        try:
            view = self.application.dispatch(action)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            self.message = str(exc)
        else:
            self.view = view
            if not isinstance(action, SaveReplayAction):
                self.selected.clear()
                self.target = None
                self.scroll = {'P1': 0, 'P2': 0}
            self.seed_text = str(view.state.seed)
            self.message = 'Replay 已保存。' if isinstance(action, SaveReplayAction) else '操作完成。'
            if isinstance(action, (StartGameAction, LoadReplayAction)):
                self.inspection = None
                self.page = 0
        self.dirty = True

    def select_card(self, pid, cid):
        s = self.view.state
        actor = s.actor or (s.current_player if s.phase == 'main' or (s.phase == 'clock' and not s.clock_used) else None)
        if pid != actor:
            return
        if cid in self.selected:
            self.selected.remove(cid)
        else:
            if not s.actor:
                self.selected.clear()
            self.selected.add(cid)
        self.dirty = True

    def select_slot(self, pid, slot):
        s = self.view.state
        if s.phase == 'main' and pid == s.current_player:
            self.target = slot
            self.message = f'目标：{pid} {NAMES[slot]}，请在右侧确认出牌。'
            self.dirty = True

    def browse(self, pid, zone):
        self.inspection, self.page = (pid, zone), 0
        self.dirty = True

    def scroll_hand(self, pid, delta):
        limit = max(0, len(self.view.state.players[pid].hand)-7)
        self.scroll[pid] = max(0, min(limit, self.scroll[pid]+delta))
        self.dirty = True

    def text(self, surface, value, rect, color=(30, 34, 40), font=None):
        font = font or self.font
        previous = surface.get_clip()
        surface.set_clip(rect.clip(previous))
        y = rect.y
        for paragraph in str(value).split('\n'):
            line = ''
            for char in paragraph:
                if line and font.size(line+char)[0] > rect.width:
                    surface.blit(font.render(line, True, color), (rect.x, y))
                    y += font.get_linesize()
                    line = ''
                line += char
            surface.blit(font.render(line, True, color), (rect.x, y))
            y += font.get_linesize()
        surface.set_clip(previous)

    def button(self, surface, rect, label, callback, enabled=True):
        pg.draw.rect(surface, (226, 234, 247) if enabled else (100, 107, 118), rect, border_radius=5)
        self.text(surface, label, rect.inflate(-14, -10), (25, 35, 50) if enabled else (190, 194, 202), self.panel_font)
        if enabled:
            self.hits.append((rect, callback))

    def shown(self, rect):
        return layout.move_rect(rect, *self.offset)

    def card(self, surface, rect, card, label='', selected=False, compact=False):
        pg.draw.rect(surface, (185, 221, 255) if selected else ((255, 245, 197) if card else (233, 235, 238)), rect)
        pg.draw.rect(surface, (35, 112, 216) if selected else (65, 70, 78), rect, 3 if selected else 1)
        content = label + '\n空位'
        if card:
            d = card.definition
            kind = {'character': '角色', 'event': '事件', 'climax': '高潮'}.get(d.kind, d.kind)
            content = f'{label}\n{card.instance_id}\n{d.name} · {kind}\n{d.code}'
            if not compact:
                color = '黄' if d.color == 'yellow' else d.color
                content += f'\n等级{d.level} 费用{d.cost}\n力量{d.power} 灵魂{d.soul}\n{color} · 特征{",".join(d.traits) or "无"}\n触发{",".join(d.trigger_marks) or "无"}'
        self.text(surface, content, rect.inflate(-8, -8))

    def draw_hand(self, surface, pid):
        hand = self.hands[pid]
        container = self.shown(hand['container'])
        pg.draw.rect(surface, (220, 224, 230), container)
        rects = sorted((self.shown(r) for r in hand['card_rects']), key=lambda r: r.x)
        entries = list(reversed(list(enumerate(self.view.state.players[pid].hand, 1))))
        limit = max(0, len(entries)-7)
        self.scroll[pid] = min(self.scroll[pid], limit)
        start = self.scroll[pid]
        visible = entries[start:start+7]
        w, h, gap = layout.HAND_CARD_W, layout.HAND_CARD_H, layout.HAND_CARD_GAP
        left = (rects[0].left+rects[-1].right-len(visible)*w-max(0, len(visible)-1)*gap)//2
        for i, (position, card) in enumerate(visible):
            rect = pg.Rect(left+i*(w+gap), rects[0].y, w, h)
            self.card(surface, rect, card, f'位置#{position}', card.instance_id in self.selected, True)
            self.hits.append((rect, lambda p=pid, c=card.instance_id: self.select_card(p, c)))
        arrows = sorted((self.shown(hand['left_arrow']), self.shown(hand['right_arrow'])), key=lambda r: r.x)
        self.button(surface, arrows[0], '<', lambda: self.scroll_hand(pid, -1), start > 0)
        self.button(surface, arrows[1], '>', lambda: self.scroll_hand(pid, 1), start < limit)
        y = container.top if pid == 'P2' else container.bottom-layout.HAND_STATUS_H
        self.text(surface, f'{pid} 手牌 {len(entries)} 张 · 左底部 → 右顶部 · 浏览 {start+1 if entries else 0}–{start+len(visible)}',
                  pg.Rect(container.x+10, y, container.width-20, layout.HAND_STATUS_H))

    def draw_clock(self, surface, pid, group):
        rects = sorted((self.shown(r) for _, r in group), key=lambda r: r.x)
        cards = self.view.state.players[pid].clock
        entries = list(reversed(list(enumerate(cards, 1))))[:6]
        for i, rect in enumerate(rects):
            pg.draw.rect(surface, (255, 245, 197) if i < len(entries) else (233, 235, 238), rect)
            pg.draw.rect(surface, (65, 70, 78), rect, 1)
        for i, (position, card) in enumerate(entries):
            rect = rects[i]
            width = rects[i+1].left-rect.left if i < 5 else rect.width
            self.text(surface, f'#{position}\n{card.number}', pg.Rect(rect.x+2, rect.y+5, width-2, 50))
        bounds = rects[0].union(rects[-1])
        self.text(surface, f'{pid} 计时 {len(cards)}/50 · 左底 → 右顶', pg.Rect(bounds.x, bounds.bottom+1, bounds.width, 18))
        self.hits.append((bounds, lambda: self.browse(pid, 'clock')))

    def render(self):
        surface = pg.Surface(self.size)
        surface.fill((45, 48, 54))
        central = pg.Rect(self.side, 0, self.world.width, self.world.height)
        pg.draw.rect(surface, (205, 209, 214), central)
        self.hits = []
        s = self.view.state
        for slot in self.slots:
            pid, suffix = slot.name.split(' ', 1)
            slot_id = SLOTS[suffix]
            cards = s.players[pid].stage[slot_id]
            rect = self.shown(slot.card_rect())
            self.card(surface, rect, cards[0] if cards else None, f'{pid} {NAMES[slot_id]}', pid == s.current_player and slot_id == self.target)
            self.hits.append((rect, lambda p=pid, z=slot_id: self.select_slot(p, z)))
        for pid, prefix in (('P1', 'lower'), ('P2', 'upper')):
            for label, rect in self.zones[prefix+'_single']:
                rect = self.shown(rect)
                zone = {'卡组': 'deck', '控制室': 'control_room'}.get(label)
                pg.draw.rect(surface, (233, 235, 238), rect)
                pg.draw.rect(surface, (65, 70, 78), rect, 1)
                content = f'{pid} {label}\n未实现'
                if zone:
                    content = f'{pid} {label}\n{len(getattr(s.players[pid], zone))} 张\n点击查看顺序'
                    self.hits.append((rect, lambda p=pid, z=zone: self.browse(p, z)))
                self.text(surface, content, rect.inflate(-8, -12))
            layout.draw_overlapping_group(surface, self.zones[prefix+'_level'], self.font, self.offset)
            self.draw_clock(surface, pid, self.zones[prefix+'_clock'])
            self.draw_hand(surface, pid)
        self.draw_panel(surface, central.right+24)
        return surface

    def draw_panel(self, surface, x):
        s, width = self.view.state, self.side-48
        light = (235, 238, 245)
        self.text(surface, 'WS 模拟器 · 操作', pg.Rect(x, 24, width, 45), light, self.panel_font)
        status = f'开局换牌：轮到 {s.actor}' if s.actor else f'回合{s.turn_number} · {s.current_player} · {PHASE_NAMES[s.phase]}'
        self.text(surface, f'先手 {s.first_player} | {status}\n本局种子：{s.seed}', pg.Rect(x, 75, width, 85), light, self.panel_font)
        self.seed_rect = pg.Rect(x, 165, width, 48)
        pg.draw.rect(surface, (248, 248, 250), self.seed_rect)
        pg.draw.rect(surface, (76, 154, 255) if self.seed_focused else (120, 130, 145), self.seed_rect, 2)
        self.text(surface, self.seed_text or '输入整数种子', self.seed_rect.inflate(-12, -10), font=self.panel_font)
        half = (width-12)//2
        self.button(surface, pg.Rect(x, 225, half, 48), '按种子开局', self.start_seed)
        self.button(surface, pg.Rect(x+half+12, 225, half, 48), '随机新局', lambda: self.dispatch(StartGameAction()))
        self.button(surface, pg.Rect(x, 285, half, 48), '保存 Replay', lambda: self.replay_dialog(True))
        self.button(surface, pg.Rect(x+half+12, 285, half, 48), '载入 Replay', lambda: self.replay_dialog(False))
        selection = ', '.join(sorted(self.selected)) or '无'
        self.text(surface, f'已选：{selection}\n目标：{NAMES.get(self.target, "未选择")}', pg.Rect(x, 350, width, 75), light, self.panel_font)
        self.button(surface, pg.Rect(x, 435, width, 48), f'确认换 {len(self.selected)} 张（可选 0 张）',
                    lambda: self.dispatch(MulliganAction(s.actor, tuple(self.selected))), bool(s.actor))
        if s.actor:
            advance = '完成换牌后可推进阶段'
        elif s.phase == 'end':
            advance = '结束回合 → 对方重置阶段'
        elif s.phase == 'clock' and not s.clock_used:
            advance = '跳过计时 → 主要阶段'
        else:
            advance = '进入'+PHASE_NAMES[PHASES[PHASES.index(s.phase)+1]]
        self.button(surface, pg.Rect(x, 495, width, 48), advance, lambda: self.dispatch(AdvancePhaseAction(s.current_player)), not s.actor)
        self.button(surface, pg.Rect(x, 555, width, 48), '所选手牌 → 计时区顶部，抽 2 张',
                    lambda: self.dispatch(ClockAction(s.current_player, next(iter(self.selected)))),
                    s.phase == 'clock' and not s.clock_used and len(self.selected) == 1)
        self.button(surface, pg.Rect(x, 615, width, 48), '确认出牌到所选己方位置',
                    lambda: self.dispatch(PlayCardAction(s.current_player, next(iter(self.selected)), self.target)),
                    s.phase == 'main' and len(self.selected) == 1 and self.target is not None)
        self.text(surface, self.message, pg.Rect(x, 680, width, 85), (255, 218, 139), self.panel_font)
        if self.inspection:
            self.draw_inspector(surface, x, 785, width)
        else:
            self.text(surface, '中央：选手牌、选己方舞台位置。\n右侧：确认操作。\n点击卡组、控制室、计时区查看完整顺序。\n手牌与计时：底部在左；位置 #1 始终是顶部。',
                      pg.Rect(x, 785, width, 190), light, self.panel_font)
        self.text(surface, '最近记录\n'+'\n'.join(self.event_text(e) for e in self.view.events[-4:]),
                  pg.Rect(x, self.size[1]-210, width, 200), light, self.panel_font)

    def draw_inspector(self, surface, x, y, width):
        pid, zone = self.inspection
        cards = getattr(self.view.state.players[pid], zone)
        count = max(1, min(12, (self.size[1]-y-330)//27))
        pages = max(1, (len(cards)+count-1)//count)
        self.page = min(self.page, pages-1)
        light = (235, 238, 245)
        self.text(surface, f'{pid} {ZONES[zone]} · {len(cards)} 张 · 顶部 → 底部', pg.Rect(x, y, width, 38), light, self.panel_font)
        self.button(surface, pg.Rect(x, y+42, 100, 45), '上一页', lambda: self.change_page(-1), self.page > 0)
        self.button(surface, pg.Rect(x+112, y+42, 100, 45), '下一页', lambda: self.change_page(1), self.page+1 < pages)
        self.text(surface, f'{self.page+1}/{pages}', pg.Rect(x+230, y+52, 100, 35), light, self.panel_font)
        start = self.page*count
        for i, card in enumerate(cards[start:start+count], start+1):
            marker = (' 顶部' if i == 1 else '') + (' 底部' if i == len(cards) else '')
            self.text(surface, f'位置 #{i:02}  {card.instance_id}  {card.definition.name}{marker}', pg.Rect(x, y+100+(i-start-1)*27, width, 27), light, self.panel_font)
        if not cards:
            self.text(surface, '（空区域）', pg.Rect(x, y+100, width, 40), light, self.panel_font)

    def change_page(self, delta):
        self.page = max(0, self.page+delta)
        self.dirty = True

    @staticmethod
    def event_text(e):
        kind, pid = e['kind'], e.get('player', '')
        if kind == 'game_started':
            return f'开局，先手 {e["first_player"]}'
        if kind in ('turn_started', 'phase_changed'):
            return f'{pid} 回合{e["turn"]} {PHASE_NAMES[e["phase"]]}'
        if kind == 'mulligan_completed':
            return f'{pid} 换{len(e["discarded"])}张，抽：{", ".join(e["drawn"]) or "无"}'
        if kind == 'card_drawn':
            return f'{pid} 抽牌 {e["card_id"]}'
        if kind == 'card_clocked':
            return f'{pid} 计时 {e["card_id"]}，抽：{", ".join(e["drawn"])}'
        if kind == 'card_played':
            return f'{pid} {e["card_id"]} 登场于{NAMES[e["slot"]]}'
        if kind == 'card_moved':
            destination = ZONES.get(e['destination'], NAMES.get(e['destination'], e['destination']))
            return f'{pid} {e["card_id"]} → {destination}'
        return kind

    def start_seed(self):
        try:
            seed = int(self.seed_text)
        except ValueError:
            self.message = '种子必须为整数。'
            self.dirty = True
            return
        self.dispatch(StartGameAction(seed))

    def replay_dialog(self, save):
        import tkinter as tk
        from tkinter import filedialog
        root = None
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            options = dict(parent=root, initialdir=str(Path(__file__).resolve().parents[2]), filetypes=[('Replay', '*.json')])
            path = filedialog.asksaveasfilename(defaultextension='.json', **options) if save else filedialog.askopenfilename(**options)
            if path:
                self.dispatch(SaveReplayAction(path) if save else LoadReplayAction(path))
        except tk.TclError as exc:
            self.message = f'无法打开文件选择窗口：{exc}'
        finally:
            if root:
                root.destroy()
            self.dirty = True

    def run(self):
        pg.init()
        try:
            self.font, _ = layout.make_fonts()
            self.panel_font = pg.font.SysFont('Microsoft YaHei', 22)
            desktop = pg.display.Info()
            scale = min(1600/self.size[0], 900/self.size[1], (desktop.current_w-60)/self.size[0], (desktop.current_h-100)/self.size[1])
            screen = pg.display.set_mode((max(640, round(self.size[0]*scale)), max(360, round(self.size[1]*scale))), pg.RESIZABLE)
            pg.display.set_caption('WS Simulator · Pygame v15')
            pg.key.start_text_input()
            timer = pg.time.Clock()
            board, scaled, previous_size = self.render(), None, None
            running = True
            while running:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
                    elif event.type == pg.TEXTINPUT and self.seed_focused:
                        self.seed_text = (self.seed_text+''.join(c for c in event.text if c in '-0123456789'))[:40]
                        self.dirty = True
                    elif event.type == pg.KEYDOWN:
                        if self.seed_focused:
                            if event.key == pg.K_BACKSPACE:
                                self.seed_text = self.seed_text[:-1]
                            elif event.key == pg.K_a and event.mod & pg.KMOD_CTRL:
                                self.seed_text = ''
                            elif event.key == pg.K_RETURN:
                                self.start_seed()
                            elif event.key == pg.K_ESCAPE:
                                self.seed_focused = False
                            self.dirty = True
                        elif event.key == pg.K_ESCAPE:
                            self.selected.clear()
                            self.target = None
                            self.dirty = True
                    elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        pos = layout.window_to_board_pos(event.pos, screen.get_size(), self.size)
                        self.seed_focused = pos is not None and self.seed_rect.collidepoint(pos)
                        if pos is not None and not self.seed_focused:
                            for rect, callback in reversed(self.hits):
                                if rect.collidepoint(pos):
                                    callback()
                                    break
                        self.dirty = True
                if self.dirty:
                    board, scaled = self.render(), None
                    self.dirty = False
                if scaled is None or previous_size != screen.get_size():
                    previous_size = screen.get_size()
                    ratio = min(previous_size[0]/self.size[0], previous_size[1]/self.size[1])
                    scaled = pg.transform.smoothscale(board, (max(1, round(self.size[0]*ratio)), max(1, round(self.size[1]*ratio))))
                screen.fill((15, 15, 18))
                screen.blit(scaled, ((screen.get_width()-scaled.get_width())//2, (screen.get_height()-scaled.get_height())//2))
                pg.display.flip()
                timer.tick(30)
        finally:
            pg.quit()


def main():
    PygameApp().run()
