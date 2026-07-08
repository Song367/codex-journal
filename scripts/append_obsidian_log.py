#!/usr/bin/env python3
"""Append a Codex task entry to the current Obsidian project log."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from codex_journal_common import (
    append_to_file,
    ensure_daily_log,
    latest_log_path,
    latest_log_relative,
    parse_project_memory,
    read_config,
    resolve_config_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a Codex Journal Obsidian entry.")
    parser.add_argument("--project-root", default=".", help="Project root containing PROJECT_MEMORY.md.")
    parser.add_argument("--config", help="Config path. Defaults to ~/.codex-journal/config.json.")
    parser.add_argument("--date", dest="day", help="Log date in YYYY-MM-DD format.")
    parser.add_argument("--summary", action="append", default=[], help="Summary bullet. Repeatable.")
    parser.add_argument("--decision", action="append", default=[], help="Decision bullet. Repeatable.")
    parser.add_argument("--change", action="append", default=[], help="Change bullet. Repeatable.")
    parser.add_argument("--open-item", action="append", default=[], help="Open item bullet. Repeatable.")
    parser.add_argument("--inference", action="append", default=[], help="Inference bullet. Repeatable.")
    parser.add_argument("--next-context", action="append", default=[], help="Next context bullet. Repeatable.")
    parser.add_argument("--entry-file", help="Markdown entry file to append instead of generated fields.")
    parser.add_argument("--confirmed", action="store_true", help="Confirm write when confirmation is required.")
    parser.add_argument("--print-draft", action="store_true", help="Print draft and target path without writing.")
    return parser.parse_args()


def bullets(items: list[str], fallback: str) -> str:
    actual = items or [fallback]
    return "\n".join(f"- {item}" for item in actual)


def render_entry(args: argparse.Namespace) -> str:
    if args.entry_file:
        return Path(args.entry_file).expanduser().read_text(encoding="utf-8")
    stamp = datetime.now().strftime("%H:%M")
    return f"""## {stamp} - Codex Task

### Summary
{bullets(args.summary, "Task completed.")}

### Decisions
{bullets(args.decision, "None recorded.")}

### Changes
{bullets(args.change, "No file changes recorded.")}

### Open Items
{bullets(args.open_item, "None recorded.")}

### Inferences
{bullets(args.inference, "None.")}

### Next Context For Codex
{bullets(args.next_context, "Read PROJECT_MEMORY.md and the latest Obsidian log before continuing.")}
"""


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    fields = parse_project_memory(project_root)
    config = read_config(resolve_config_path(args.config))
    day = args.day or date.today().isoformat()
    project_slug = fields.get("Slug") or project_root.name
    project_name = fields.get("Name") or project_root.name
    log_path = latest_log_path(config, project_slug, day)
    relative_log = latest_log_relative(config, project_slug, day)
    entry = render_entry(args)

    if args.print_draft:
        print(f"Target: {log_path}\n")
        print(entry)
        return

    if config.require_confirmation_before_write and not args.confirmed:
        print(f"Confirmation required before writing: {log_path}", file=sys.stderr)
        print(entry)
        raise SystemExit(2)

    ensure_daily_log(log_path, project_name, day)
    append_to_file(log_path, entry)
    print(f"Appended log entry to {log_path}")
    print(f"Latest Log: {relative_log}")


if __name__ == "__main__":
    main()
