from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------
# 路径
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TERMINOLOGY_PATH = PROJECT_ROOT / "docs" / "terminology.md"


# ---------------------------------------------------------
# 审计规则
#
# 第一版暂时显式维护。
# 不自动修改代码。
#
# status:
#   migration_pending
#       规范名已经确定，检查旧名是否仍存在。
#
#   review
#       尚未最终决定，只报告当前使用情况。
# ---------------------------------------------------------


@dataclass(frozen=True)
class TerminologyRule:
    concept: str
    canonical: str
    legacy: tuple[str, ...]
    status: str
    note: str = ""


RULES: tuple[TerminologyRule, ...] = (
    TerminologyRule(
        concept="前列左",
        canonical="center_left",
        legacy=("front_left",),
        status="migration_pending",
        note="官方使用 Center Stage。",
    ),
    TerminologyRule(
        concept="前列中",
        canonical="center_center",
        legacy=("front_center",),
        status="migration_pending",
        note="官方使用 Center Stage。",
    ),
    TerminologyRule(
        concept="前列右",
        canonical="center_right",
        legacy=("front_right",),
        status="migration_pending",
        note="官方使用 Center Stage。",
    ),
    TerminologyRule(
        concept="舞台格",
        canonical="stage_position",
        legacy=("stage_slot",),
        status="review",
        note="是否保留 stage_slot 作为项目 API 术语尚未决定。",
    ),
    TerminologyRule(
        concept="攻击子阶段",
        canonical="attack_subphase",
        legacy=("attack_sequence",),
        status="migration_pending",
        note="规范名采用 attack_subphase。",
    ),
    TerminologyRule(
        concept="后续流程",
        canonical="Continuation",
        legacy=("pending_continuation",),
        status="review",
        note="当前元组结构以后可能改为明确类型。",
    ),
)


# ---------------------------------------------------------
# 扫描设置
# ---------------------------------------------------------

SCAN_SUFFIXES = {
    ".py",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "legacy",
}

SKIP_FILES = {
    Path("tools/terminology_audit.py"),
    Path("add_damage_support.py"),
}


# ---------------------------------------------------------
# 扫描结果
# ---------------------------------------------------------


@dataclass(frozen=True)
class Match:
    path: Path
    line_number: int
    line: str


def iter_source_files():
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix not in SCAN_SUFFIXES:
            continue

        relative = path.relative_to(PROJECT_ROOT)

        if relative in SKIP_FILES:
            continue

        if any(part in SKIP_DIRS for part in relative.parts):
            continue

        yield path


def find_name(name: str) -> list[Match]:
    matches: list[Match] = []

    # 避免 front_left_extra 之类的部分误匹配。
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_])"
        rf"{re.escape(name)}"
        rf"(?![A-Za-z0-9_])"
    )

    for path in iter_source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if pattern.search(line):
                matches.append(
                    Match(
                        path=path.relative_to(PROJECT_ROOT),
                        line_number=line_number,
                        line=line.strip(),
                    )
                )

    return matches


# ---------------------------------------------------------
# 输出
# ---------------------------------------------------------


def print_matches(matches: list[Match]) -> None:
    if not matches:
        print("    未发现")
        return

    for match in matches:
        print(
            f"    {match.path}:{match.line_number}"
        )
        print(
            f"        {match.line}"
        )


def audit_rule(rule: TerminologyRule) -> bool:
    """
    返回 True 表示 strict 模式下应视为问题。
    """

    print()
    print("=" * 72)
    print(f"{rule.concept}")
    print(f"规范名：{rule.canonical}")
    print(f"状态：{rule.status}")

    if rule.note:
        print(f"备注：{rule.note}")

    strict_problem = False

    print()
    print("[规范名使用位置]")

    canonical_matches = find_name(
        rule.canonical
    )
    print_matches(canonical_matches)

    for legacy in rule.legacy:
        print()
        print(f"[旧名 / 待检查名称] {legacy}")

        legacy_matches = find_name(legacy)
        print_matches(legacy_matches)

        if (
            rule.status == "migration_pending"
            and legacy_matches
        ):
            strict_problem = True

    return strict_problem


def check_terminology_file() -> None:
    if not TERMINOLOGY_PATH.exists():
        raise RuntimeError(
            "未找到命名规范："
            f"{TERMINOLOGY_PATH}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "扫描仓库中的规则相关命名。"
            "默认只报告，不修改文件。"
        )
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "若仍存在明确标记为待迁移的旧名称，"
            "返回非 0。"
        ),
    )

    args = parser.parse_args()

    check_terminology_file()

    print("WS Simulator 命名审计")
    print(f"项目：{PROJECT_ROOT}")
    print(f"规范：{TERMINOLOGY_PATH}")
    print()
    print(
        "注意：本工具只扫描和报告，"
        "不会修改任何文件。"
    )

    strict_problem = False

    for rule in RULES:
        if audit_rule(rule):
            strict_problem = True

    print()
    print("=" * 72)
    print("审计结束")

    if args.strict and strict_problem:
        print(
            "STRICT：仍存在明确待迁移的旧名称。"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())