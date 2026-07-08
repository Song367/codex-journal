#!/usr/bin/env python3
"""Resolve generated project memory and latest Obsidian log."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from codex_journal_common import parse_project_memory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve Codex Journal project context.")
    parser.add_argument("--project-root", default=".", help="Project root containing PROJECT_MEMORY.md.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    fields = parse_project_memory(project_root)
    latest_relative = fields.get("Latest Log", "")
    vault = fields.get("Vault", "")
    latest_path = Path(vault).expanduser() / latest_relative if vault and latest_relative else None
    latest_text = ""
    if latest_path and latest_path.is_file():
        latest_text = latest_path.read_text(encoding="utf-8")

    print(
        json.dumps(
            {
                "project_root": str(project_root),
                "project_name": fields.get("Name", ""),
                "project_slug": fields.get("Slug", ""),
                "project_memory": fields["text"],
                "latest_log": str(latest_path) if latest_path else "",
                "latest_log_text": latest_text,
                "latest_log_read": bool(latest_text),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
