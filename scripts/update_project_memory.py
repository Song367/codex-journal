#!/usr/bin/env python3
"""Update generated PROJECT_MEMORY.md state."""

from __future__ import annotations

import argparse
from pathlib import Path

from codex_journal_common import (
    JournalConfig,
    analyze_project,
    parse_project_memory,
    write_project_memory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update Codex Journal project memory.")
    parser.add_argument("--project-root", default=".", help="Project root containing PROJECT_MEMORY.md.")
    parser.add_argument("--status", help="Current project status paragraph.")
    parser.add_argument("--latest-log", help="Latest log path relative to the Obsidian vault.")
    parser.add_argument("--decision", action="append", default=[], help="Confirmed decision. Repeatable.")
    parser.add_argument("--open-question", action="append", default=[], help="Open question. Repeatable.")
    parser.add_argument("--next-step", action="append", default=[], help="Next concrete step. Repeatable.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    fields = parse_project_memory(project_root)
    vault = fields.get("Vault")
    project_log_dir = fields.get("Project Log Dir", "")
    latest_log = args.latest_log or fields.get("Latest Log", "")
    if not vault:
        raise SystemExit("Cannot update PROJECT_MEMORY.md: Vault field is missing.")

    config = JournalConfig(
        obsidian_vault=Path(vault).expanduser().resolve(),
        projects_dir=project_log_dir.split("/", 1)[0] if "/" in project_log_dir else "Projects",
    )
    analysis = analyze_project(project_root)
    memory_path = write_project_memory(
        project_root,
        analysis,
        config,
        latest_log,
        status=args.status,
        decisions=args.decision or None,
        open_questions=args.open_question or None,
        next_steps=args.next_step or None,
    )
    print(str(memory_path))


if __name__ == "__main__":
    main()
