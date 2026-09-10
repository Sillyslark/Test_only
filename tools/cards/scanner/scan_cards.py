#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def scan_cards(cards_root: Path) -> list[Path]:
    """
    Discover candidate Card JSON files under cards_root.

    Responsibilities:
    - Scan only inside cards_root.
    - Discover every *.json file recursively.
    - Return candidate file paths only.

    Non-responsibilities:
    - Do not validate JSON syntax or Card fields.
    - Do not validate directory structure or filename format.
    - Do not generate Base Card Number.
    - Do not build Card Index.
    """
    cards_root = Path(cards_root)

    if not cards_root.exists():
        raise FileNotFoundError(f"Cards root does not exist: {cards_root}")

    if not cards_root.is_dir():
        raise NotADirectoryError(f"Cards root is not a directory: {cards_root}")

    return [
        path
        for path in cards_root.rglob("*.json")
        if path.is_file()
    ]


def to_relative_paths(paths: list[Path], base: Path) -> list[str]:
    """
    Convert discovered paths to POSIX-style paths relative to base.

    This helper is intended for test artifacts / human-readable reports.
    It does not change Scanner semantics.
    """
    base = Path(base).resolve()

    result: list[str] = []

    for path in paths:
        resolved = path.resolve()

        try:
            relative = resolved.relative_to(base)
        except ValueError as exc:
            raise ValueError(
                f"Path is outside report base: {resolved}"
            ) from exc

        result.append(relative.as_posix())

    return result


def write_scan_report(
    paths: list[Path],
    output_path: Path,
    *,
    report_base: Path,
) -> None:
    """
    Write a diagnostic scan artifact.

    The report is optional and is not an input to Validator or Index Builder.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Sorting is only for deterministic report readability.
    relative_paths = sorted(to_relative_paths(paths, report_base))

    output_path.write_text(
        json.dumps(relative_paths, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover candidate Card JSON files inside a cards/ directory."
    )

    parser.add_argument(
        "cards_root",
        type=Path,
        help="Root directory of Card JSON data, for example: cards",
    )

    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help=(
            "Optional diagnostic JSON output path. "
            "Example: tests/artifacts/scanner/case_01_basic.json"
        ),
    )

    parser.add_argument(
        "--report-base",
        type=Path,
        default=None,
        help=(
            "Base directory used to make report paths relative. "
            "Defaults to cards_root.parent."
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    cards_root = args.cards_root.resolve()

    try:
        candidates = scan_cards(cards_root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        parser.error(str(exc))

    # Console output is diagnostic only.
    for path in sorted(candidates, key=lambda p: p.as_posix()):
        print(path)

    print(f"\nCandidate Card JSON files: {len(candidates)}")

    if args.report is not None:
        report_base = (
            args.report_base.resolve()
            if args.report_base is not None
            else cards_root.parent
        )

        write_scan_report(
            candidates,
            args.report,
            report_base=report_base,
        )

        print(f"Scan report written to: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
