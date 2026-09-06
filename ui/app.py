"""Run with python main.py; requires only Python and Tkinter."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from actions import StartGameAction, MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction, SaveReplayAction, LoadReplayAction
from application import Application
from phases import PHASES, PHASE_NAMES
from ui.zones import clock_slots


class App(tk.Tk):
    def __init__(self, application=None):
        super().__init__()
        self.title("WS 模拟器")
        self.geometry("1100x850")
        self.minsize(950, 800)
        self.selected = set()
        self.application = application if application is not None else Application()
        self.view = None
        toolbar = ttk.Frame(self, padding=12)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="随机种子").pack(side="left")
        self.seed = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.seed, width=23).pack(side="left", padx=8)
        ttk.Button(toolbar, text="按此种子开局", command=self.start).pack(side="left")
        ttk.Button(toolbar, text="随机新局", command=self.random_start).pack(side="left", padx=6)
        ttk.Button(toolbar, text="保存 Replay", command=self.save).pack(side="right")
        ttk.Button(toolbar, text="载入 Replay", command=self.load).pack(side="right", padx=6)
        self.status = ttk.Label(self, padding=12, font=("Microsoft YaHei", 12, "bold"))
        self.status.pack(fill="x")
        ttk.Label(self, text="统一编号：位置 #1 = 顶部；最后一位 = 底部。手牌、计时区从左到右显示底部 → 顶部。\n卡面 1–50 是实例序号，不是区域位置；P1/P2 区分双方实体卡。", padding=(12, 0)).pack(fill="x")
        viewport = ttk.Frame(self)
        viewport.pack(fill="both", expand=True)
        board_canvas = tk.Canvas(viewport, highlightthickness=0)
        board_scroll = ttk.Scrollbar(viewport, orient="vertical", command=board_canvas.yview)
        board_scroll.pack(side="right", fill="y")
        board_canvas.pack(fill="both", expand=True)
        board_canvas.configure(yscrollcommand=board_scroll.set)
        self.board = ttk.Frame(board_canvas, padding=12)
        board_window = board_canvas.create_window((0, 0), window=self.board, anchor="nw")
        self.board.bind("<Configure>", lambda event: board_canvas.configure(scrollregion=board_canvas.bbox("all")))
        board_canvas.bind("<Configure>", lambda event: board_canvas.itemconfigure(board_window, width=event.width))
        self.confirm = ttk.Button(self, command=self.submit)
        self.confirm.pack(pady=8)
        self.clock_confirm = ttk.Button(self, text="将所选手牌置于计时区顶部并抽 2 张", command=self.submit_clock)
        self.clock_confirm.pack(pady=4)
        self.log = ttk.Label(self, padding=12, wraplength=1000)
        self.log.pack(fill="x")
        self.random_start()

    def random_start(self):
        self.execute(StartGameAction(), clear_selection=True)

    def execute(self, action, clear_selection=False):
        try:
            view = self.application.dispatch(action)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            messagebox.showerror("操作失败", str(exc))
            return
        self.view = view
        self.seed.set(str(view.state.seed))
        if clear_selection:
            self.selected.clear()
        self.render()

    def start(self):
        try:
            seed = int(self.seed.get())
        except ValueError:
            messagebox.showerror("种子错误", "请输入整数种子")
            return
        self.execute(StartGameAction(seed), clear_selection=True)

    def render(self):
        for child in self.board.winfo_children():
            child.destroy()
        state = self.view.state
        actor = state.actor
        clock_available = state.phase == "clock" and not state.clock_used
        hand_actor = actor or (state.current_player if clock_available or state.phase == "main" else None)
        phase = (f"轮到 {actor} 选择换牌（可选 0–5 张）" if actor else
                 f"回合 {state.turn_number} · {state.current_player} · {PHASE_NAMES[state.phase]}")
        if state.phase == "main":
            phase += " · 选手牌后点击己方舞台位置出牌"
        self.status.config(text=f"先手：{state.first_player}　｜　{phase}")
        for pid in state.players:
            player = state.players[pid]
            frame = ttk.LabelFrame(self.board, text=f"{pid} · {'先手' if pid == state.first_player else '后手'}", padding=12)
            frame.pack(fill="x", pady=6)
            clock_frame = ttk.Frame(frame)
            clock_frame.pack(side="bottom", fill="x", pady=(8, 0))
            ttk.Label(clock_frame, text=f"计时区 {len(player.clock)}/50 · 仅显示底部 6 位，左端为底部，向右朝顶部").pack(anchor="w")
            clock_row = ttk.Frame(clock_frame)
            clock_row.pack(anchor="w")
            for slot in clock_slots(player.clock):
                text = "空位" if slot is None else f"位置 #{slot[0]} · 卡 {slot[1].number}\n{slot[1].instance_id}" + (" · 底部" if slot[0] == len(player.clock) else "")
                ttk.Label(clock_row, text=text, width=16, relief="solid", padding=4).pack(side="left", padx=2)
            for label, zone in (("卡组", "deck"), ("控制室", "control_room")):
                ttk.Button(frame, text=f"{label}\n{len(getattr(player, zone))} 张\n点击查看顺序",
                           command=lambda p=pid, z=zone, l=label: self.inspect(p, z, l), width=16).pack(side="left", padx=(0, 12), ipady=16)
            hand = ttk.Frame(frame)
            hand.pack(side="left", fill="x", expand=True)
            ttk.Label(hand, text="手牌　底部 → 顶部（新抽牌显示在左侧）").pack(anchor="w")
            canvas = tk.Canvas(hand, height=128, highlightthickness=0)
            canvas.pack(fill="x", expand=True, pady=(6, 0))
            scroll = ttk.Scrollbar(hand, orient="horizontal", command=canvas.xview)
            scroll.pack(fill="x")
            canvas.configure(xscrollcommand=scroll.set)
            row = ttk.Frame(canvas)
            canvas.create_window((0, 0), window=row, anchor="nw")
            row.bind("<Configure>", lambda event, c=canvas: c.configure(scrollregion=c.bbox("all")))
            for i, card in reversed(list(enumerate(player.hand))):
                selected = card.instance_id in self.selected
                tk.Button(row, text=f"位置 #{i+1}\n{self.card_text(card)}" + ("\n✓ 已选" if selected else "\n"),
                          width=22, bg="#fff4bb" if not selected else "#cce7ff",
                          state="normal" if pid == hand_actor else "disabled",
                          command=lambda cid=card.instance_id: self.toggle(cid)).pack(side="left", padx=3)
            if pid == "P1":
                self.render_stage()
        if actor:
            button_text = f"确认换 {len(self.selected)} 张"
        elif state.phase == "end":
            button_text = "完成结束阶段，切换玩家 → 重置阶段"
        elif state.phase == "clock":
            button_text = "进入主要阶段" if state.clock_used else "跳过计时操作 → 主要阶段"
        else:
            next_phase = PHASES[PHASES.index(state.phase) + 1]
            button_text = f"进入{PHASE_NAMES[next_phase]}" + ("（抽 1 张）" if next_phase == "draw" else "")
        self.confirm.config(text=button_text, state="normal")
        self.clock_confirm.config(state="normal" if clock_available and len(self.selected) == 1 else "disabled")
        lines = [f"种子：{state.seed}。双方已洗牌并各抽 5 张。"]
        for e in self.view.events[1:][-3:]:
            if e['kind'] == 'mulligan_completed':
                lines.append(f"{e['player']} 换牌：{', '.join(e['discarded']) or '不换牌'}；抽到：{', '.join(e['drawn']) or '无'}。")
            elif e['kind'] == 'card_drawn':
                lines.append(f"{e['player']} 从卡组顶部抽到 {e['card_id']}。")
            elif e['kind'] == 'card_clocked':
                lines.append(f"{e['player']} 将 {e['card_id']} 置于计时区顶部；抽到 {', '.join(e['drawn'])}。")
            elif e['kind'] == 'card_moved':
                lines.append(f"{e['player']}：{e['card_id']} 从 {e['source']} 移至 {e['destination']}。")
            elif e['kind'] == 'card_played':
                lines.append(f"{e['player']}：{e['card_id']} 登场于 {e['slot']}（规则结算已完成）。")
            else:
                lines.append(f"回合 {e['turn']} · {e['player']} · {PHASE_NAMES[e['phase']]}。")
        self.log.config(text="\n".join(lines))

    def render_stage(self):
        state = self.view.state
        arena = ttk.LabelFrame(self.board, text="双方舞台 · 对应位置上下对齐", padding=8)
        arena.pack(fill="x", pady=6)
        side = 176
        gap = round(side * 0.1)
        card_width = round(side * 63 / 88)
        pitch = side + gap
        layout = ttk.Frame(arena, width=3 * side + 2 * gap, height=4 * side + 3 * gap)
        layout.pack(anchor="center")
        layout.pack_propagate(False)
        front = (("front_left", "前列左", 0), ("front_center", "前列中", 1), ("front_right", "前列右", 2))
        back = (("back_left", "后列左", 0.5), ("back_right", "后列右", 1.5))
        self.stage_buttons = {}
        self.stage_cells = {}
        for row, (pid, slots) in enumerate((("P1", back), ("P1", front), ("P2", front), ("P2", back))):
            for slot_id, label, column in slots:
                cards = state.players[pid].stage[slot_id]
                content = self.stage_card_text(cards[0]) if cards else "\n空位"
                cell = ttk.Frame(layout, borderwidth=0)
                cell.place(x=round(column * pitch), y=row * pitch, width=side, height=side)
                button = tk.Button(cell, text=f"{pid} · {label}\n{content}",
                                    wraplength=card_width - 12, font=("Microsoft YaHei", 9),
                                    bg="#fff4bb" if cards else "#f8f8f8", relief="solid", borderwidth=1,
                                    highlightthickness=0, disabledforeground="#555555",
                                    state="normal" if state.phase == "main" and pid == state.current_player and len(self.selected) == 1 else "disabled",
                                    command=lambda p=pid, s=slot_id: self.play_card(s, p))
                button.place(x=(side-card_width)//2, y=0, width=card_width, height=side)
                self.stage_buttons[pid, slot_id] = button
                self.stage_cells[pid, slot_id] = cell

    @staticmethod
    def stage_card_text(card):
        d = card.definition
        kind = {"character": "角色", "event": "事件", "climax": "高潮"}.get(d.kind, d.kind)
        color = "黄色" if d.color == "yellow" else d.color
        return (f"{d.name} · {kind}\n{d.code} · {card.instance_id}\n"
                f"等级 {d.level} / 费用 {d.cost}\n力量 {d.power} / 灵魂 {d.soul}\n"
                f"{color} · 特征 {','.join(d.traits) or '无'}\n触发 {','.join(d.trigger_marks) or '无'}")

    def toggle(self, card_id):
        if card_id in self.selected:
            self.selected.remove(card_id)
        else:
            if self.view.state.phase in ("clock", "main"):
                self.selected.clear()
            self.selected.add(card_id)
        self.render()

    @staticmethod
    def card_text(card):
        d = card.definition
        kind_name = {"character": "角色", "event": "事件", "climax": "高潮"}.get(d.kind, d.kind)
        return (f"{d.name} · {d.code} · {card.instance_id} · {kind_name}\n"
                f"等级 {d.level} / 费用 {d.cost} · 力量 {d.power} / 灵魂 {d.soul}\n"
                f"{'黄色' if d.color == 'yellow' else d.color} · 特征 {','.join(d.traits) or '无'} · 触发 {','.join(d.trigger_marks) or '无'}")

    def play_card(self, slot_id, owner=None):
        if owner is not None and owner != self.view.state.current_player:
            return
        if len(self.selected) == 1:
            self.execute(PlayCardAction(self.view.state.current_player, next(iter(self.selected)), slot_id), clear_selection=True)

    def submit_clock(self):
        if len(self.selected) == 1:
            self.execute(ClockAction(self.view.state.current_player, next(iter(self.selected))), clear_selection=True)

    def submit(self):
        state = self.view.state
        action = (MulliganAction(state.actor, tuple(self.selected)) if state.actor else
                  AdvancePhaseAction(state.current_player))
        self.execute(action, clear_selection=True)

    def inspect(self, pid, zone, label):
        window = tk.Toplevel(self)
        window.title(f"{pid} {label} · 当前顺序快照")
        window.geometry("420x550")
        ttk.Label(window, text="位置 #1 = 顶部；最后一位 = 底部\n这是打开时的顺序快照。", padding=10).pack()
        box = ttk.Frame(window)
        box.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(box)
        scrollbar.pack(side="right", fill="y")
        listing = tk.Listbox(box, font=("Microsoft YaHei", 11), yscrollcommand=scrollbar.set)
        listing.pack(fill="both", expand=True)
        scrollbar.config(command=listing.yview)
        cards = getattr(self.view.state.players[pid], zone)
        for i, card in enumerate(cards):
            marker = (" 顶部" if i == 0 else "") + (" 底部" if i == len(cards)-1 else "")
            listing.insert("end", f"位置 #{i+1:02}　卡片 {card.number:02}　{card.instance_id}{marker}")
        if not cards:
            listing.insert("end", "（空区域）")

    def save(self):
        path = filedialog.asksaveasfilename(initialdir=Path(__file__).resolve().parent.parent, defaultextension=".json", filetypes=[("Replay", "*.json")])
        if path:
            self.execute(SaveReplayAction(path))

    def load(self):
        path = filedialog.askopenfilename(initialdir=Path(__file__).resolve().parent.parent, filetypes=[("Replay", "*.json")])
        if not path:
            return
        self.execute(LoadReplayAction(path), clear_selection=True)
