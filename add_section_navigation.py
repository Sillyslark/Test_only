#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

NAV_START = "<!-- SECTION_NAV_START -->"
NAV_END = "<!-- SECTION_NAV_END -->"

SECTION_RE = re.compile(r"^(\d+)_.*\.md$", re.IGNORECASE)
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+.+$")


def discover_sections(chapter_dir: Path) -> list[Path]:
    """Return numbered section files in numeric order."""
    items: list[tuple[int, Path]] = []
    for path in chapter_dir.glob("*.md"):
        m = SECTION_RE.match(path.name)
        if m:
            items.append((int(m.group(1)), path))
    return [p for _, p in sorted(items, key=lambda item: item[0])]


def strip_nav_blocks(text: str) -> str:
    """Remove navigation blocks previously inserted by this script."""
    pattern = re.compile(
        rf"\n?{re.escape(NAV_START)}.*?{re.escape(NAV_END)}\n?",
        re.DOTALL,
    )
    return pattern.sub("\n", text)


def build_nav(prev_file: Path | None, next_file: Path | None) -> str:
    parts: list[str] = []

    if prev_file is not None:
        parts.append(f"[← 上一节]({prev_file.name})")
    else:
        parts.append("← 上一节")

    parts.append("[返回本章目录](README.md)")

    if next_file is not None:
        parts.append(f"[下一节 →]({next_file.name})")
    else:
        parts.append("下一节 →")

    return f"{NAV_START}\n" + " | ".join(parts) + f"\n{NAV_END}"


def insert_navigation(text: str, nav: str) -> str:
    """
    Put one navigation block immediately after the first Markdown heading,
    and another at the end of the file.
    """
    text = strip_nav_blocks(text).rstrip("\n") + "\n"

    heading = HEADING_RE.search(text)
    if not heading:
        raise ValueError("No Markdown heading found")

    insert_at = heading.end()
    top = text[:insert_at]
    rest = text[insert_at:]

    # Preserve original body text; only add clearly marked navigation blocks.
    return (
        top
        + "\n\n"
        + nav
        + "\n"
        + rest.lstrip("\n")
        + "\n"
        + nav
        + "\n"
    )


def remove_navigation(text: str) -> str:
    """Remove only navigation blocks created by this script."""
    cleaned = strip_nav_blocks(text)
    # Normalize only the extra blank lines created by insertion/removal.
    return cleaned.strip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Add chapter navigation to numbered Markdown section files. "
            "Files are discovered from names like 01_xxx.md, 02_xxx.md, ..."
        )
    )
    parser.add_argument(
        "chapter_dir",
        type=Path,
        help="Chapter directory containing README.md and numbered section files",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove navigation blocks previously inserted by this script",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would change without writing them",
    )
    args = parser.parse_args()

    chapter_dir = args.chapter_dir.resolve()
    if not chapter_dir.is_dir():
        raise SystemExit(f"Chapter directory not found: {chapter_dir}")

    readme = chapter_dir / "README.md"
    if not readme.exists():
        raise SystemExit(f"Chapter README not found: {readme}")

    sections = discover_sections(chapter_dir)
    if not sections:
        raise SystemExit("No numbered Markdown section files found.")

    changed = 0

    for i, path in enumerate(sections):
        original = path.read_text(encoding="utf-8")

        if args.remove:
            updated = remove_navigation(original)
        else:
            prev_file = sections[i - 1] if i > 0 else None
            next_file = sections[i + 1] if i + 1 < len(sections) else None
            nav = build_nav(prev_file, next_file)
            updated = insert_navigation(original, nav)

        if updated == original:
            print(f"UNCHANGED  {path.name}")
            continue

        changed += 1
        if args.dry_run:
            print(f"WOULD CHANGE  {path.name}")
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"UPDATED  {path.name}")

    print(f"\nSections found: {len(sections)}")
    print(f"Files changed: {changed}")
    if args.dry_run:
        print("Dry run only; no files were written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
