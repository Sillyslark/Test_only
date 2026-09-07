# One-time migration: move root test_*.py files into tests/ and remove safe duplication.
#
# Run from the repository root:
#     python organize_tests.py
#
# Afterwards:
#     python -B -m unittest discover -s tests -v
#
# This script does not modify engine/game-rule code.

from __future__ import annotations

import ast
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
TESTS = ROOT / "tests"


def remove_defs(source: str, names: set[str]) -> str:
    tree = ast.parse(source)
    ranges: list[tuple[int, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            start = node.lineno
            end = node.end_lineno or node.lineno

            if node.decorator_list:
                start = min(start, *(d.lineno for d in node.decorator_list))

            ranges.append((start, end))

    if not ranges:
        return source

    lines = source.splitlines(keepends=True)
    remove_lines: set[int] = set()

    for start, end in ranges:
        remove_lines.update(range(start - 1, end))
        if end < len(lines) and not lines[end].strip():
            remove_lines.add(end)

    return "".join(
        line
        for index, line in enumerate(lines)
        if index not in remove_lines
    )


def patch_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    TESTS.mkdir(exist_ok=True)

    init = TESTS / "__init__.py"
    if not init.exists():
        init.write_text("# Test package.\n", encoding="utf-8")

    helpers = TESTS / "helpers.py"
    helpers.write_text(
        "from actions import AdvancePhaseAction, MulliganAction\n"
        "from engine import Session\n\n\n"
        "def opened(seed: int = 42) -> Session:\n"
        "    session = Session(seed)\n"
        "    for _ in range(2):\n"
        "        session.dispatch(MulliganAction(session.state.actor, ()))\n"
        "    return session\n\n\n"
        "def at_clock(seed: int = 42) -> Session:\n"
        "    session = opened(seed)\n"
        "    for _ in range(2):\n"
        "        session.dispatch(AdvancePhaseAction(session.state.current_player))\n"
        "    return session\n\n\n"
        "def at_main(seed: int = 42) -> Session:\n"
        "    session = opened(seed)\n"
        "    for _ in range(3):\n"
        "        session.dispatch(AdvancePhaseAction(session.state.current_player))\n"
        "    return session\n",
        encoding="utf-8",
    )

    root_tests = sorted(ROOT.glob("test_*.py"))
    for source in root_tests:
        destination = TESTS / source.name

        if destination.exists():
            raise FileExistsError(
                f"{destination} already exists; aborting to avoid overwriting."
            )

        shutil.move(str(source), str(destination))

    for path in TESTS.glob("test_*.py"):
        patch_file(
            path,
            [
                ("from test_turns import opened", "from tests.helpers import opened"),
                ("from test_clock import at_clock", "from tests.helpers import at_clock"),
                ("from test_play import at_main", "from tests.helpers import at_main"),
            ],
        )

    helper_owners = {
        "test_turns.py": {"opened"},
        "test_clock.py": {"at_clock"},
        "test_play.py": {"at_main"},
    }

    for filename, names in helper_owners.items():
        path = TESTS / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            text = remove_defs(text, names)
            path.write_text(text, encoding="utf-8")

    app_choice = TESTS / "test_application_deck_choice.py"
    if app_choice.exists():
        text = app_choice.read_text(encoding="utf-8")
        text = remove_defs(
            text,
            {
                "test_start_game_can_choose_copy_for_both_players",
                "test_same_seed_and_deck_selection_is_deterministic",
            },
        )
        app_choice.write_text(text, encoding="utf-8")

    replay_choice = TESTS / "test_replay_deck_choice.py"
    if replay_choice.exists():
        text = replay_choice.read_text(encoding="utf-8")
        text = remove_defs(
            text,
            {"test_v1_replay_still_migrates_to_current_version"},
        )
        text = text.replace("from unittest.mock import patch\n", "")
        replay_choice.write_text(text, encoding="utf-8")

    turns = TESTS / "test_turns.py"
    if turns.exists():
        text = turns.read_text(encoding="utf-8")
        text = text.replace(
            "from engine import Session, other, state_hash\n",
            "from engine import Session, VERSION, other, state_hash\n",
        )
        text = text.replace("\nfrom engine import Session, VERSION\n", "\n")
        turns.write_text(text, encoding="utf-8")

    print("Test migration complete.")
    print(f"Moved tests to: {TESTS}")
    print()
    print("Run:")
    print("  python -B -m unittest discover -s tests -v")
    print()
    print("Expected change: 3 intentionally redundant tests removed.")
    print("All game-rule behavior tests remain in place.")


if __name__ == "__main__":
    main()
