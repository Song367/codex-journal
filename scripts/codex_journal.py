#!/usr/bin/env python3
"""Unified internal command surface for the codex-journal plugin."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from codex_journal_common import (
    JournalConfig,
    analyze_project,
    append_to_file,
    ensure_daily_log,
    latest_log_path,
    latest_log_relative,
    load_or_create_config,
    parse_project_memory,
    read_config,
    resolve_config_path,
    upsert_agents_file,
    write_project_memory,
)
from append_obsidian_log import render_entry


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", default=".", help="Project root.")
    parser.add_argument("--config", help="Config path. Defaults to ~/.codex-journal/config.json.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex Journal plugin command surface.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enable = subparsers.add_parser("enable", help="Initialize Codex Journal for a project.")
    add_common_args(enable)
    enable.add_argument("--vault", help="Absolute path to Obsidian vault. Writes config.")
    enable.add_argument("--date", dest="day", help="Log date in YYYY-MM-DD format.")

    restore = subparsers.add_parser("restore", help="Resolve project memory and latest log.")
    add_common_args(restore)

    record = subparsers.add_parser("record", help="Append or draft a task log entry.")
    add_common_args(record)
    record.add_argument("--date", dest="day", help="Log date in YYYY-MM-DD format.")
    record.add_argument("--summary", action="append", default=[], help="Summary bullet.")
    record.add_argument("--decision", action="append", default=[], help="Decision bullet.")
    record.add_argument("--change", action="append", default=[], help="Change bullet.")
    record.add_argument("--open-item", action="append", default=[], help="Open item bullet.")
    record.add_argument("--inference", action="append", default=[], help="Inference bullet.")
    record.add_argument("--next-context", action="append", default=[], help="Next context bullet.")
    record.add_argument("--entry-file", help="Markdown entry file.")
    record.add_argument("--confirmed", action="store_true", help="Confirm write.")
    record.add_argument("--print-draft", action="store_true", help="Print draft only.")

    memory = subparsers.add_parser("memory", help="Update generated PROJECT_MEMORY.md.")
    add_common_args(memory)
    memory.add_argument("--status", help="Current project status paragraph.")
    memory.add_argument("--latest-log", help="Latest log path relative to vault.")
    memory.add_argument("--decision", action="append", default=[], help="Confirmed decision.")
    memory.add_argument("--open-question", action="append", default=[], help="Open question.")
    memory.add_argument("--next-step", action="append", default=[], help="Next concrete step.")

    status = subparsers.add_parser("status", help="Report whether the project is configured.")
    add_common_args(status)

    return parser


def project_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.project_root).expanduser().resolve()


def command_enable(args: argparse.Namespace) -> None:
    project_root = project_root_from_args(args)
    config_path = resolve_config_path(args.config)
    config = load_or_create_config(config_path, args.vault)
    analysis = analyze_project(project_root)
    day = args.day or date.today().isoformat()
    latest_relative = latest_log_relative(config, analysis.slug, day)
    log_path = latest_log_path(config, analysis.slug, day)
    agents_path = upsert_agents_file(project_root)
    memory_path = write_project_memory(project_root, analysis, config, latest_relative)
    ensure_daily_log(log_path, analysis.name, day)
    print(
        json.dumps(
            {
                "configured": True,
                "project_root": str(project_root),
                "config": str(config_path),
                "agents": str(agents_path),
                "project_memory": str(memory_path),
                "latest_log": str(log_path),
            },
            indent=2,
        )
    )


def command_restore(args: argparse.Namespace) -> None:
    project_root = project_root_from_args(args)
    fields = parse_project_memory(project_root)
    latest_relative = fields.get("Latest Log", "")
    vault = fields.get("Vault", "")
    latest_path = Path(vault).expanduser() / latest_relative if vault and latest_relative else None
    latest_text = latest_path.read_text(encoding="utf-8") if latest_path and latest_path.is_file() else ""
    print(
        json.dumps(
            {
                "configured": True,
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


def command_record(args: argparse.Namespace) -> None:
    project_root = project_root_from_args(args)
    fields = parse_project_memory(project_root)
    config = read_config(resolve_config_path(args.config))
    day = args.day or date.today().isoformat()
    project_slug = fields.get("Slug") or project_root.name
    project_name = fields.get("Name") or project_root.name
    log_path = latest_log_path(config, project_slug, day)
    entry = render_entry(args)

    if args.print_draft:
        print(json.dumps({"target": str(log_path), "draft": entry}, indent=2))
        return
    if config.require_confirmation_before_write and not args.confirmed:
        print(json.dumps({"confirmation_required": True, "target": str(log_path), "draft": entry}, indent=2))
        raise SystemExit(2)
    ensure_daily_log(log_path, project_name, day)
    append_to_file(log_path, entry)
    print(json.dumps({"written": True, "target": str(log_path)}, indent=2))


def command_memory(args: argparse.Namespace) -> None:
    project_root = project_root_from_args(args)
    fields = parse_project_memory(project_root)
    vault = fields.get("Vault")
    if not vault:
        raise SystemExit("Cannot update PROJECT_MEMORY.md: Vault field is missing.")
    project_log_dir = fields.get("Project Log Dir", "")
    latest_log = args.latest_log or fields.get("Latest Log", "")
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
    print(json.dumps({"updated": True, "project_memory": str(memory_path)}, indent=2))


def command_status(args: argparse.Namespace) -> None:
    project_root = project_root_from_args(args)
    memory_path = project_root / "PROJECT_MEMORY.md"
    config_path = resolve_config_path(args.config)
    print(
        json.dumps(
            {
                "project_root": str(project_root),
                "project_memory_exists": memory_path.is_file(),
                "config_path": str(config_path),
                "config_exists": config_path.is_file(),
            },
            indent=2,
        )
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    commands = {
        "enable": command_enable,
        "restore": command_restore,
        "record": command_record,
        "memory": command_memory,
        "status": command_status,
    }
    try:
        commands[args.command](args)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"codex-journal error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
