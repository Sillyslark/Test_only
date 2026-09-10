from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_DIR = REPO_ROOT / "tools" / "cards" / "scanner"

if str(SCANNER_DIR) not in sys.path:
    sys.path.insert(0, str(SCANNER_DIR))

from scan_cards import scan_cards, to_relative_paths, write_scan_report  # noqa: E402


def test_case_05_multiple_titles_products() -> None:
    case_root = (
        REPO_ROOT
        / "tests"
        / "fixtures"
        / "scanner"
        / "case_05_multiple_titles_products"
    )
    cards_root = case_root / "cards"

    expected_path = (
        REPO_ROOT
        / "tests"
        / "expected"
        / "scanner"
        / "case_05_multiple_titles_products.json"
    )
    artifact_path = (
        REPO_ROOT
        / "tests"
        / "artifacts"
        / "scanner"
        / "case_05_multiple_titles_products.json"
    )

    candidates = scan_cards(cards_root)

    actual = sorted(to_relative_paths(candidates, case_root))
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    write_scan_report(
        candidates,
        artifact_path,
        report_base=case_root,
    )

    assert actual == expected
