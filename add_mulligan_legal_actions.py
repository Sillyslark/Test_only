# One-time patch: add Mulligan legal-action query and hide unavailable UI actions.
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ACTIONS = ROOT / "actions.py"
ENGINE = ROOT / "engine.py"
APPLICATION = ROOT / "application.py"
UI_APP = ROOT / "ui" / "app.py"


def patch_actions():
    text = ACTIONS.read_text(encoding="utf-8")
    if "class MulliganOptions:" not in text:
        marker = "@dataclass(frozen=True)\nclass MulliganAction:\n"
        addition = (
            "@dataclass(frozen=True)\n"
            "class MulliganOptions:\n"
            "    player_id: str\n"
            "    selectable_card_ids: tuple[str, ...]\n"
            "    min_select: int\n"
            "    max_select: int\n\n\n"
        )
        if marker not in text:
            raise RuntimeError("Cannot find MulliganAction")
        text = text.replace(marker, addition + marker, 1)
    ACTIONS.write_text(text, encoding="utf-8")


def patch_engine():
    text = ENGINE.read_text(encoding="utf-8")
    old_import = "from actions import MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction\n"
    new_import = "from actions import MulliganOptions, MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction\n"
    if "MulliganOptions" not in text[:500]:
        if old_import not in text:
            raise RuntimeError("Cannot find actions import in engine.py")
        text = text.replace(old_import, new_import, 1)

    if "def legal_actions(self, player_id):" not in text:
        marker = "    def _get_zone(self, player_id, zone, slot=None):\n"
        method = (
            "    def legal_actions(self, player_id):\n"
            "        if player_id not in PLAYERS:\n"
            "            raise ValueError(\"玩家无效\")\n\n"
            "        if self.state.result != MatchResult.ONGOING:\n"
            "            return ()\n\n"
            "        if self.state.actor == player_id:\n"
            "            hand = self.state.players[player_id].hand\n"
            "            return (\n"
            "                MulliganOptions(\n"
            "                    player_id=player_id,\n"
            "                    selectable_card_ids=tuple(card.instance_id for card in hand),\n"
            "                    min_select=0,\n"
            "                    max_select=len(hand),\n"
            "                ),\n"
            "            )\n\n"
            "        return ()\n\n"
        )
        if marker not in text:
            raise RuntimeError("Cannot find _get_zone")
        text = text.replace(marker, method + marker, 1)

    ENGINE.write_text(text, encoding="utf-8")


def patch_application():
    text = APPLICATION.read_text(encoding="utf-8")
    if "legal_actions: tuple[object, ...]" not in text:
        old = (
            "@dataclass(frozen=True)\n"
            "class Snapshot:\n"
            "    state: GameState\n"
            "    events: tuple[dict, ...]\n"
        )
        new = old + "    legal_actions: tuple[object, ...]\n"
        if old not in text:
            raise RuntimeError("Cannot find Snapshot")
        text = text.replace(old, new, 1)

    if "active_player = state.actor or state.current_player" not in text:
        old = (
            "        return Snapshot(\n"
            "            deepcopy(self._session.state),\n"
            "            tuple(deepcopy(self._session.events)),\n"
            "        )\n"
        )
        new = (
            "        state = deepcopy(self._session.state)\n"
            "        active_player = state.actor or state.current_player\n"
            "        legal_actions = (\n"
            "            self._session.legal_actions(active_player)\n"
            "            if active_player is not None\n"
            "            else ()\n"
            "        )\n"
            "        return Snapshot(\n"
            "            state,\n"
            "            tuple(deepcopy(self._session.events)),\n"
            "            tuple(deepcopy(legal_actions)),\n"
            "        )\n"
        )
        if old not in text:
            raise RuntimeError("Cannot find snapshot return")
        text = text.replace(old, new, 1)

    APPLICATION.write_text(text, encoding="utf-8")


def patch_ui():
    text = UI_APP.read_text(encoding="utf-8")

    if "MulliganOptions" not in text[:600]:
        old = "from actions import StartGameAction, MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction, SaveReplayAction, LoadReplayAction\n"
        new = "from actions import MulliganOptions, StartGameAction, MulliganAction, AdvancePhaseAction, ClockAction, PlayCardAction, SaveReplayAction, LoadReplayAction\n"
        if old not in text:
            raise RuntimeError("Cannot find UI actions import")
        text = text.replace(old, new, 1)

    old = (
        "        self.confirm = ttk.Button(self, command=self.submit)\n"
        "        self.confirm.pack(pady=8)\n"
        "        self.clock_confirm = ttk.Button(self, text=\"将所选手牌置于计时区顶部并抽 2 张\", command=self.submit_clock)\n"
        "        self.clock_confirm.pack(pady=4)\n"
    )
    new = (
        "        self.confirm = ttk.Button(self, command=self.submit)\n"
        "        self.clock_confirm = ttk.Button(self, text=\"将所选手牌置于计时区顶部并抽 2 张\", command=self.submit_clock)\n"
    )
    if "self.confirm.pack(pady=8)" in text:
        if old not in text:
            raise RuntimeError("Cannot find operation button init block")
        text = text.replace(old, new, 1)

    if "mulligan_options = next(" not in text:
        old = (
            "        state = self.view.state\n"
            "        actor = state.actor\n"
            "        clock_available = state.phase == \"clock\" and not state.clock_used\n"
        )
        new = (
            "        state = self.view.state\n"
            "        actor = state.actor\n"
            "        mulligan_options = next(\n"
            "            (option for option in self.view.legal_actions if isinstance(option, MulliganOptions)),\n"
            "            None,\n"
            "        )\n"
            "        clock_available = state.phase == \"clock\" and not state.clock_used\n"
        )
        if old not in text:
            raise RuntimeError("Cannot find render state block")
        text = text.replace(old, new, 1)

    if "可选 0–5 张" in text:
        old = (
            "        phase = (f\"轮到 {actor} 选择换牌（可选 0–5 张）\" if actor else\n"
            "                 f\"回合 {state.turn_number} · {state.current_player} · {PHASE_NAMES[state.phase]}\")\n"
        )
        new = (
            "        phase = (\n"
            "            f\"轮到 {actor} 选择换牌（可选 {mulligan_options.min_select}–{mulligan_options.max_select} 张）\"\n"
            "            if mulligan_options is not None\n"
            "            else f\"回合 {state.turn_number} · {state.current_player} · {PHASE_NAMES[state.phase]}\"\n"
            "        )\n"
        )
        if old not in text:
            raise RuntimeError("Cannot find phase status block")
        text = text.replace(old, new, 1)

    old = (
        "        self.confirm.config(text=button_text, state=\"normal\")\n"
        "        self.clock_confirm.config(state=\"normal\" if clock_available and len(self.selected) == 1 else \"disabled\")\n"
    )
    new = (
        "        self.confirm.pack_forget()\n"
        "        self.clock_confirm.pack_forget()\n\n"
        "        if mulligan_options is not None:\n"
        "            self.confirm.config(text=f\"确认换 {len(self.selected)} 张\", state=\"normal\")\n"
        "            self.confirm.pack(pady=8)\n"
        "        elif actor is None:\n"
        "            self.confirm.config(text=button_text, state=\"normal\")\n"
        "            self.confirm.pack(pady=8)\n"
        "            if clock_available and len(self.selected) == 1:\n"
        "                self.clock_confirm.config(state=\"normal\")\n"
        "                self.clock_confirm.pack(pady=4)\n"
    )
    if "self.confirm.pack_forget()" not in text:
        if old not in text:
            raise RuntimeError("Cannot find button render block")
        text = text.replace(old, new, 1)

    old = (
        "    def toggle(self, card_id):\n"
        "        if card_id in self.selected:\n"
        "            self.selected.remove(card_id)\n"
        "        else:\n"
        "            if self.view.state.phase in (\"clock\", \"main\"):\n"
        "                self.selected.clear()\n"
        "            self.selected.add(card_id)\n"
        "        self.render()\n"
    )
    new = (
        "    def toggle(self, card_id):\n"
        "        mulligan_options = next(\n"
        "            (option for option in self.view.legal_actions if isinstance(option, MulliganOptions)),\n"
        "            None,\n"
        "        )\n\n"
        "        if mulligan_options is not None:\n"
        "            if card_id not in mulligan_options.selectable_card_ids:\n"
        "                return\n"
        "            if card_id in self.selected:\n"
        "                self.selected.remove(card_id)\n"
        "            elif len(self.selected) < mulligan_options.max_select:\n"
        "                self.selected.add(card_id)\n"
        "        else:\n"
        "            if card_id in self.selected:\n"
        "                self.selected.remove(card_id)\n"
        "            else:\n"
        "                if self.view.state.phase in (\"clock\", \"main\"):\n"
        "                    self.selected.clear()\n"
        "                self.selected.add(card_id)\n"
        "        self.render()\n"
    )
    if "if card_id not in mulligan_options.selectable_card_ids:" not in text:
        if old not in text:
            raise RuntimeError("Cannot find toggle method")
        text = text.replace(old, new, 1)

    UI_APP.write_text(text, encoding="utf-8")


def main():
    patch_actions()
    patch_engine()
    patch_application()
    patch_ui()
    print("Mulligan legal-actions patch applied.")
    print("Add tests/test_legal_actions.py and run full tests.")


if __name__ == "__main__":
    main()
