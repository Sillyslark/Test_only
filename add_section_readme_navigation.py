#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

NAV_START = "<!-- SECTION_README_NAV_START -->"
NAV_END = "<!-- SECTION_README_NAV_END -->"
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+.+$")

# Chapter 2 section-level navigation.
# 2.1 is a standalone Markdown file, while 2.2-2.4 use subsection directories.
SECTIONS = [
    ("2.1", "01_card_properties_overview.md", False),
    ("2.2", "02_base_json_storage/README.md", True),
    ("2.3", "03_card_number/README.md", True),
    ("2.4", "04_card_text_ability/README.md", True),
]


def strip_existing_nav(text: str) -> str:
    pattern = re.compile(
        rf"\n?{re.escape(NAV_START)}.*?{re.escape(NAV_END)}\n?",
        re.DOTALL,
    )
    return pattern.sub("\n", text)


def rel_link(from_path: Path, to_path: Path) -> str:
    return Path(
        __import__("os").path.relpath(to_path, start=from_path.parent)
    ).as_posix()


def make_nav(
    current_path: Path,
    previous: tuple[str, Path] | None,
    next_: tuple[str, Path] | None,
    chapter_readme: Path,
) -> str:
    if previous:
        prev_label, prev_path = previous
        left = f"[← {prev_label}]({rel_link(current_path, prev_path)})"
    else:
        left = "← 上一节"

    middle = f"[返回第 2 章目录]({rel_link(current_path, chapter_readme)})"

    if next_:
        next_label, next_path = next_
        right = f"[{next_label} →]({rel_link(current_path, next_path)})"
    else:
        right = "下一节 →"

    return f"{NAV_START}\n{left} | {middle} | {right}\n{NAV_END}"


def add_nav(text: str, nav: str) -> str:
    text = strip_existing_nav(text).rstrip("\n") + "\n"

    heading = HEADING_RE.search(text)
    if not heading:
        raise ValueError("No Markdown heading found")

    insert_at = heading.end()

    return (
        text[:insert_at]
        + "\n\n"
        + nav
        + "\n"
        + text[insert_at:].lstrip("\n")
        + "\n"
        + nav
        + "\n"
    )


def remove_nav(text: str) -> str:
    return strip_existing_nav(text).strip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add chapter-level navigation to Chapter 2 section README files."
    )
    parser.add_argument(
        "chapter_dir",
        type=Path,
        help="Path to docs/02_cards",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove navigation blocks inserted by this script",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing files",
    )
    args = parser.parse_args()

    chapter_dir = args.chapter_dir.resolve()
    chapter_readme = chapter_dir / "README.md"

    if not chapter_dir.is_dir():
        raise SystemExit(f"Directory not found: {chapter_dir}")

    if not chapter_readme.exists():
        raise SystemExit(f"Chapter README.md not found: {chapter_readme}")

    resolved = [(label, chapter_dir / rel, is_readme) for label, rel, is_readme in SECTIONS]

    missing = [str(path) for _, path, _ in resolved if not path.exists()]
    if missing:
        raise SystemExit("Required section file(s) not found:\n" + "\n".join(missing))

    # Only the section README files (2.2-2.4) are modified.
    targets = [(i, label, path) for i, (label, path, is_readme) in enumerate(resolved) if is_readme]

    changed = 0

    for i, label, path in targets:
        original = path.read_text(encoding="utf-8")

        if args.remove:
            updated = remove_nav(original)
        else:
            prev_label, prev_path, _ = resolved[i - 1] if i > 0 else (None, None, None)
            next_label, next_path, _ = resolved[i + 1] if i + 1 < len(resolved) else (None, None, None)

            previous = (prev_label, prev_path) if prev_path else None
            next_ = (next_label, next_path) if next_path else None

            nav = make_nav(path, previous, next_, chapter_readme)
            updated = add_nav(original, nav)

        if updated == original:
            print(f"UNCHANGED  {label}  {path.relative_to(chapter_dir)}")
            continue

        changed += 1

        if args.dry_run:
            print(f"WOULD CHANGE  {label}  {path.relative_to(chapter_dir)}")
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"UPDATED  {label}  {path.relative_to(chapter_dir)}")

    print(f"\nREADME targets: {len(targets)}")
    print(f"Files changed: {changed}")

    if args.dry_run:
        print("Dry run only; no files were written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
