#!/usr/bin/env python3
"""
Validate an OpenClaw agent workspace.

Usage:
    python3 scripts/quality_check.py <agent_dir>

The checker is intentionally conservative. It fails on missing core files, hard size
overruns, obvious placeholders, and likely secret leakage. It warns on weaker design
signals that still need human judgment.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileSpec:
    name: str
    target_chars: int
    hard_chars: int = 20_000


CORE_FILES = [
    FileSpec("IDENTITY.md", 500),
    FileSpec("SOUL.md", 10_000),
    FileSpec("AGENTS.md", 18_000),
    FileSpec("USER.md", 5_000),
    FileSpec("TOOLS.md", 15_000),
    FileSpec("MEMORY.md", 20_000),
    FileSpec("HEARTBEAT.md", 2_000),
]

PLACEHOLDER_RE = re.compile(
    r"\b(TODO|TBD|FIXME|CHANGEME|REPLACE_ME)\b|"
    r"\[(?:agent-id|agent-name|agent-root|display name|mission|role|trait|value|anti-pattern|"
    r"path|condition|workflow|signals?|step|limit|date|optional|one sentence|"
    r"tool or command convention|fallback path)[^\]]*\]",
    re.IGNORECASE,
)

SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{20,}|"
    r"ghp_[A-Za-z0-9_]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"xox[baprs]-[A-Za-z0-9-]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----|"
    r"(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"])",
    re.IGNORECASE,
)


class Reporter:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def pass_(self, message: str) -> None:
        print(f"PASS  {message}")

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"WARN  {message}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"FAIL  {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_core_files(agent_dir: Path, reporter: Reporter) -> dict[str, str]:
    contents: dict[str, str] = {}

    for spec in CORE_FILES:
        path = agent_dir / spec.name
        if not path.exists():
            reporter.fail(f"missing required file: {spec.name}")
            continue

        content = read_text(path)
        contents[spec.name] = content
        size = len(content)

        if size > spec.hard_chars:
            reporter.fail(f"{spec.name} is {size} chars, over hard OpenClaw limit {spec.hard_chars}")
        elif size > spec.target_chars:
            reporter.warn(f"{spec.name} is {size} chars, over target {spec.target_chars}")
        else:
            reporter.pass_(f"{spec.name} exists and size is within target ({size}/{spec.target_chars})")

    return contents


def check_identity(contents: dict[str, str], reporter: Reporter) -> None:
    text = contents.get("IDENTITY.md", "")
    for marker in ("Name", "Agent ID", "Role"):
        if marker.lower() not in text.lower():
            reporter.warn(f"IDENTITY.md does not mention {marker}")

    if "One-Line Signal" in text or "one-line" in text.lower():
        reporter.pass_("IDENTITY.md includes a one-line signal")
    else:
        reporter.warn("IDENTITY.md should include a one-line signal")


def check_operational_boundaries(contents: dict[str, str], reporter: Reporter) -> None:
    agents = contents.get("AGENTS.md", "")
    tools = contents.get("TOOLS.md", "")
    soul = contents.get("SOUL.md", "")
    heartbeat = contents.get("HEARTBEAT.md", "")

    required_agents_markers = {
        "startup": r"\bStartup\b|启动",
        "request routing": r"Request Routing|Answer Protocol|请求|路由|classify",
        "memory": r"\bMemory\b|记忆|memory/YYYY",
        "safety": r"\bSafety\b|安全|approval|确认",
    }

    for label, pattern in required_agents_markers.items():
        if re.search(pattern, agents, re.IGNORECASE):
            reporter.pass_(f"AGENTS.md contains {label} guidance")
        else:
            reporter.fail(f"AGENTS.md missing {label} guidance")

    if re.search(r"subagents?|子[ -]?agent|delegation|spawn", agents, re.IGNORECASE):
        reporter.pass_("AGENTS.md mentions subagent/delegation visibility")
    else:
        reporter.warn("AGENTS.md should mention that subagents only see AGENTS.md and TOOLS.md")

    if re.search(r"Local Paths|Tool Use|工具|命令|CLI|API|env", tools, re.IGNORECASE):
        reporter.pass_("TOOLS.md contains concrete tool/path guidance")
    else:
        reporter.warn("TOOLS.md looks too thin for subagents")

    operational_terms_in_soul = len(
        re.findall(r"spawn|subagent|memory/YYYY|rm -rf|deploy|API|CLI|TOOL|workflow", soul, re.IGNORECASE)
    )
    if operational_terms_in_soul > 12:
        reporter.warn("SOUL.md appears to contain operational detail; move workflow rules to AGENTS.md")
    else:
        reporter.pass_("SOUL.md is not overloaded with operational detail")

    if len(heartbeat) > 2_000:
        reporter.fail("HEARTBEAT.md is too large for heartbeat context")
    elif "No proactive heartbeat work is configured" in heartbeat or "HEARTBEAT_OK" in heartbeat:
        reporter.pass_("HEARTBEAT.md uses safe no-proactive default")
    else:
        reporter.warn("HEARTBEAT.md configures proactive work; confirm this was user-requested")


def check_placeholders_and_secrets(agent_dir: Path, reporter: Reporter) -> None:
    text_files = [
        path
        for path in agent_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
        and "sessions" not in path.parts
    ]

    placeholder_files = [
        agent_dir / spec.name for spec in CORE_FILES if (agent_dir / spec.name).exists()
    ]
    research_dir = agent_dir / "references" / "research"
    if research_dir.exists():
        placeholder_files.extend(sorted(research_dir.glob("*.md")))

    placeholder_hits: list[str] = []
    secret_hits: list[str] = []
    stale_path_hits: list[str] = []

    for path in placeholder_files:
        text = read_text(path)
        rel = path.relative_to(agent_dir)
        if PLACEHOLDER_RE.search(text):
            placeholder_hits.append(str(rel))

    for path in text_files:
        text = read_text(path)
        rel = path.relative_to(agent_dir)
        if SECRET_RE.search(text):
            secret_hits.append(str(rel))
        if re.search(r"/Users/(?:alchain|macmini|[^/\s]+/Documents/写作)", text):
            stale_path_hits.append(str(rel))

    if placeholder_hits:
        reporter.fail("placeholder text remains in: " + ", ".join(sorted(set(placeholder_hits))[:8]))
    else:
        reporter.pass_("no obvious placeholders found")

    if secret_hits:
        reporter.fail("possible secret material found in: " + ", ".join(sorted(set(secret_hits))[:8]))
    else:
        reporter.pass_("no obvious secrets found")

    if stale_path_hits:
        reporter.warn("stale author-local paths found in: " + ", ".join(sorted(set(stale_path_hits))[:8]))
    else:
        reporter.pass_("no stale author-local paths found")


def check_runtime_state(agent_dir: Path, reporter: Reporter) -> None:
    forbidden_names = {
        "auth-state.json",
        "auth.json",
        "credentials.json",
        "sessions.json",
        "openclaw.json",
    }
    hits = [path.relative_to(agent_dir) for path in agent_dir.rglob("*") if path.is_file() and path.name in forbidden_names]

    if hits:
        reporter.fail("runtime/auth state should not be bundled: " + ", ".join(map(str, hits[:8])))
    else:
        reporter.pass_("no bundled auth/session state files found")


def check_references(agent_dir: Path, reporter: Reporter) -> None:
    research_dir = agent_dir / "references" / "research"
    if not research_dir.exists():
        reporter.warn("references/research/ is missing; acceptable only for simple hand-authored agents")
        return

    notes = sorted(research_dir.glob("*.md"))
    if not notes:
        reporter.warn("references/research/ exists but has no markdown notes")
        return

    reporter.pass_(f"references/research contains {len(notes)} markdown note(s)")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/quality_check.py <agent_dir>")
        return 2

    agent_dir = Path(sys.argv[1]).expanduser().resolve()
    reporter = Reporter()

    print(f"OpenClaw agent quality check: {agent_dir}")
    print("=" * 72)

    if not agent_dir.exists() or not agent_dir.is_dir():
        reporter.fail(f"agent directory does not exist: {agent_dir}")
    else:
        contents = check_core_files(agent_dir, reporter)
        check_identity(contents, reporter)
        check_operational_boundaries(contents, reporter)
        check_placeholders_and_secrets(agent_dir, reporter)
        check_runtime_state(agent_dir, reporter)
        check_references(agent_dir, reporter)

    print("=" * 72)
    print(f"Failures: {len(reporter.failures)}  Warnings: {len(reporter.warnings)}")

    if reporter.failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
