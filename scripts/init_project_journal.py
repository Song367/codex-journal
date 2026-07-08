#!/usr/bin/env python3
"""Initialize Codex Journal for a project."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from codex_journal_common import (
    analyze_project,
    ensure_daily_log,
    latest_log_path,
    latest_log_relative,
    load_or_create_config,
    resolve_config_path,
    upsert_agents_file,
    write_project_memory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize Codex Journal in a project.")
    parser.add_argument("--project-root", default=".", help="Project root to initialize.")
    parser.add_argument("--vault", help="Absolute path to Obsidian vault. Writes global config.")
    parser.add_argument("--config", help="Config path. Defaults to ~/.codex-journal/config.json.")
    parser.add_argument("--date", dest="day", help="Log date in YYYY-MM-DD format.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
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
                "project_root": str(project_root),
                "config": str(config_path),
                "agents": str(agents_path),
                "project_memory": str(memory_path),
                "latest_log": str(log_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
