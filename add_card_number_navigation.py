#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

NAV_START = "<!-- CARD_NUMBER_NAV_START -->"
NAV_END = "<!-- CARD_NUMBER_NAV_END -->"

FILE_RE = re.compile(r"^(\d+)_.*\.md$", re.IGNORECASE)
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+.+$")


def discover_files(section_dir: Path) -> list[Path]:
    items: list[tuple[int, Path]] = []
    for path in section_dir.glob("*.md"):
        match = FILE_RE.match(path.name)
        if match:
            items.append((int(match.group(1)), path))
    return [path for _, path in sorted(items, key=lambda item: item[0])]


def strip_existing_nav(text: str) -> str:
    pattern = re.compile(
        rf"\n?{re.escape(NAV_START)}.*?{re.escape(NAV_END)}\n?",
        re.DOTALL,
    )
    return pattern.sub("\n", text)


def make_nav(prev_file: Path | None, next_file: Path | None) -> str:
    left = f"[← 上一小节]({prev_file.name})" if prev_file else "← 上一小节"
    middle = "[返回 2.3 目录](README.md)"
    right = f"[下一小节 →]({next_file.name})" if next_file else "下一小节 →"
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
        description="Add navigation to Card Number subsection Markdown files."
    )
    parser.add_argument(
        "section_dir",
        type=Path,
        help="Directory containing README.md and numbered Card Number subsection files",
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

    section_dir = args.section_dir.resolve()

    if not section_dir.is_dir():
        raise SystemExit(f"Directory not found: {section_dir}")

    if not (section_dir / "README.md").exists():
        raise SystemExit(f"README.md not found in: {section_dir}")

    files = discover_files(section_dir)
    if not files:
        raise SystemExit("No numbered Markdown files found.")

    changed = 0

    for i, path in enumerate(files):
        original = path.read_text(encoding="utf-8")

        if args.remove:
            updated = remove_nav(original)
        else:
            prev_file = files[i - 1] if i > 0 else None
            next_file = files[i + 1] if i + 1 < len(files) else None
            updated = add_nav(original, make_nav(prev_file, next_file))

        if updated == original:
            print(f"UNCHANGED  {path.name}")
            continue

        changed += 1

        if args.dry_run:
            print(f"WOULD CHANGE  {path.name}")
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"UPDATED  {path.name}")

    print(f"\nSubsections found: {len(files)}")
    print(f"Files changed: {changed}")

    if args.dry_run:
        print("Dry run only; no files were written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
