#!/usr/bin/env python3
"""
Summarize research notes for an OpenClaw agent build.

Usage:
    python3 scripts/merge_research.py <agent_dir>

Scans <agent_dir>/references/research/*.md and prints a compact checkpoint table.
The script is intentionally filename-agnostic so it works for persona agents, operator
agents, and converted perspective skills.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


TARGET_FILE_MARKERS = {
    "IDENTITY": re.compile(r"\bIDENTITY\b|身份|名称|agent id", re.IGNORECASE),
    "SOUL": re.compile(r"\bSOUL\b|人格|语气|voice|values|truth boundary", re.IGNORECASE),
    "AGENTS": re.compile(r"\bAGENTS\b|workflow|routing|operations|subagent|流程|路由", re.IGNORECASE),
    "USER": re.compile(r"\bUSER\b|用户|preference|profile", re.IGNORECASE),
    "TOOLS": re.compile(r"\bTOOLS\b|tool|cli|api|path|工具|命令", re.IGNORECASE),
    "MEMORY": re.compile(r"\bMEMORY\b|memory|记忆|长期", re.IGNORECASE),
    "HEARTBEAT": re.compile(r"\bHEARTBEAT\b|heartbeat|monitor|cron|监控", re.IGNORECASE),
}


def count_sources(content: str) -> dict[str, int]:
    urls = re.findall(r"https?://[^\s)>\]]+", content)
    primary = re.findall(r"一手|primary|official|本人|原文|原始|direct", content, re.IGNORECASE)
    secondary = re.findall(r"二手|secondary|commentary|analysis|评论|分析|转述", content, re.IGNORECASE)
    uncertainty = re.findall(r"不确定|uncertain|推测|inference|conflict|矛盾", content, re.IGNORECASE)

    return {
        "urls": len(set(urls)),
        "primary": len(primary),
        "secondary": len(secondary),
        "uncertainty": len(uncertainty),
    }


def extract_findings(content: str, max_items: int = 2) -> str:
    headings = [h.strip() for h in re.findall(r"^##\s+(.+)$", content, re.MULTILINE)]
    if headings:
        return "; ".join(headings[:max_items])

    bolds = [b.strip() for b in re.findall(r"\*\*(.+?)\*\*", content)]
    if bolds:
        return "; ".join(bolds[:max_items])

    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
    return "; ".join(lines[:max_items])


def infer_targets(content: str) -> str:
    targets = [name for name, pattern in TARGET_FILE_MARKERS.items() if pattern.search(content)]
    return ", ".join(targets[:4]) if targets else "unspecified"


def trim(value: str, width: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= width:
        return value
    return value[: width - 3] + "..."


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/merge_research.py <agent_dir>")
        return 2

    agent_dir = Path(sys.argv[1]).expanduser()
    research_dir = agent_dir / "references" / "research"

    if not research_dir.exists():
        print(f"Research directory does not exist: {research_dir}")
        return 1

    notes = sorted(research_dir.glob("*.md"))
    if not notes:
        print(f"No markdown research notes found in: {research_dir}")
        return 1

    totals = {"urls": 0, "primary": 0, "secondary": 0, "uncertainty": 0}

    print("| Note | Targets | Sources | Key findings |")
    print("| --- | --- | ---: | --- |")

    for note in notes:
        content = note.read_text(encoding="utf-8")
        stats = count_sources(content)
        for key, value in stats.items():
            totals[key] += value

        source_summary = f"{stats['urls']} urls, {stats['primary']} primary, {stats['secondary']} secondary"
        print(
            f"| `{note.name}` | {trim(infer_targets(content), 32)} | "
            f"{trim(source_summary, 32)} | {trim(extract_findings(content), 56)} |"
        )

    print()
    print("Summary:")
    print(f"- Notes: {len(notes)}")
    print(f"- Unique URL mentions: {totals['urls']}")
    print(f"- Primary markers: {totals['primary']}")
    print(f"- Secondary markers: {totals['secondary']}")
    print(f"- Uncertainty/conflict markers: {totals['uncertainty']}")

    if totals["urls"] < 5 and totals["primary"] == 0:
        print("- Warning: evidence is thin; mark the generated agent as limited v1.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
