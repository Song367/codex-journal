#!/usr/bin/env python3
"""Shared helpers for Codex Journal scripts."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


DEFAULT_PROJECTS_DIR = "Projects"
DEFAULT_CONFIG_PATH = Path.home() / ".codex-journal" / "config.json"
BEGIN_MARKER = "<!-- BEGIN CODEX-JOURNAL -->"
END_MARKER = "<!-- END CODEX-JOURNAL -->"


@dataclass(frozen=True)
class JournalConfig:
    obsidian_vault: Path
    projects_dir: str = DEFAULT_PROJECTS_DIR
    require_confirmation_before_write: bool = True
    auto_update_project_memory: bool = True
    auto_log_tasks: bool = True


@dataclass(frozen=True)
class ProjectAnalysis:
    name: str
    slug: str
    root: Path
    git_remote: str
    summary: str
    stack: list[str]


def resolve_config_path(raw_path: str | None = None) -> Path:
    if raw_path:
        return Path(raw_path).expanduser().resolve()
    env_path = os.environ.get("CODEX_JOURNAL_CONFIG")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return DEFAULT_CONFIG_PATH


def read_config(config_path: Path) -> JournalConfig:
    if not config_path.is_file():
        raise SystemExit(
            f"Codex Journal config not found: {config_path}\n"
            "Run init_project_journal.py with --vault once, or pass --config."
        )
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    vault = payload.get("obsidian_vault")
    if not isinstance(vault, str) or not vault.strip():
        raise SystemExit(f"Missing obsidian_vault in config: {config_path}")
    return JournalConfig(
        obsidian_vault=Path(vault).expanduser().resolve(),
        projects_dir=str(payload.get("projects_dir") or DEFAULT_PROJECTS_DIR),
        require_confirmation_before_write=bool(
            payload.get("require_confirmation_before_write", True)
        ),
        auto_update_project_memory=bool(payload.get("auto_update_project_memory", True)),
        auto_log_tasks=bool(payload.get("auto_log_tasks", True)),
    )


def write_config(config_path: Path, vault: Path) -> JournalConfig:
    config = JournalConfig(obsidian_vault=vault.expanduser().resolve())
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "obsidian_vault": str(config.obsidian_vault),
        "projects_dir": config.projects_dir,
        "require_confirmation_before_write": config.require_confirmation_before_write,
        "auto_update_project_memory": config.auto_update_project_memory,
        "auto_log_tasks": config.auto_log_tasks,
    }
    config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return config


def load_or_create_config(config_path: Path, vault: str | None) -> JournalConfig:
    if vault:
        return write_config(config_path, Path(vault))
    return read_config(config_path)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def run_git(project_root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def detect_readme_summary(project_root: Path) -> str:
    for name in ("README.md", "readme.md", "README"):
        path = project_root / name
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip().lstrip("#").strip()
            if line:
                return line
    return "Project initialized for Codex Journal. Update through Codex task context."


def detect_stack(project_root: Path) -> list[str]:
    candidates = {
        "package.json": "Node.js",
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "Yarn",
        "go.mod": "Go",
        "pyproject.toml": "Python",
        "requirements.txt": "Python",
        "Cargo.toml": "Rust",
        "Gemfile": "Ruby",
        "composer.json": "PHP",
    }
    stack = [label for filename, label in candidates.items() if (project_root / filename).exists()]
    return sorted(set(stack))


def analyze_project(project_root: Path) -> ProjectAnalysis:
    root = project_root.expanduser().resolve()
    name = root.name
    git_remote = run_git(root, ["remote", "get-url", "origin"])
    return ProjectAnalysis(
        name=name,
        slug=slugify(name),
        root=root,
        git_remote=git_remote,
        summary=detect_readme_summary(root),
        stack=detect_stack(root),
    )


def latest_log_relative(config: JournalConfig, project_slug: str, day: str | None = None) -> str:
    log_day = day or date.today().isoformat()
    return f"{config.projects_dir}/{project_slug}/{log_day}.md"


def latest_log_path(config: JournalConfig, project_slug: str, day: str | None = None) -> Path:
    return config.obsidian_vault / latest_log_relative(config, project_slug, day)


def render_agents_section() -> str:
    return f"""{BEGIN_MARKER}
## Codex Journal

This project uses the `codex-journal` plugin.

Before project-specific work:
1. Read `PROJECT_MEMORY.md`.
2. Read the latest Obsidian log referenced by `PROJECT_MEMORY.md`.
3. Continue only from verified project memory, logs, inspected files, and current conversation context.

At task completion:
1. Draft a journal entry automatically for meaningful work.
2. Respect the global `require_confirmation_before_write` setting.
3. Use Codex Journal scripts when updating project memory or Obsidian logs.
4. Do not ask the user to hand-edit generated memory files.
{END_MARKER}
"""


def replace_marked_section(existing: str, new_section: str) -> str:
    pattern = re.compile(
        rf"{re.escape(BEGIN_MARKER)}.*?{re.escape(END_MARKER)}\n?",
        re.DOTALL,
    )
    if pattern.search(existing):
        return pattern.sub(new_section, existing).rstrip() + "\n"
    prefix = existing.rstrip()
    return (prefix + "\n\n" if prefix else "") + new_section


def upsert_agents_file(project_root: Path) -> Path:
    path = project_root / "AGENTS.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Project Instructions\n"
    path.write_text(replace_marked_section(existing, render_agents_section()), encoding="utf-8")
    return path


def render_project_memory(
    analysis: ProjectAnalysis,
    config: JournalConfig,
    latest_relative: str,
    *,
    status: str | None = None,
    decisions: list[str] | None = None,
    open_questions: list[str] | None = None,
    next_steps: list[str] | None = None,
) -> str:
    stack = ", ".join(analysis.stack) if analysis.stack else "Not detected"
    remote = analysis.git_remote or "Not detected"
    current_status = status or analysis.summary
    decisions = decisions or ["Project journal initialized."]
    open_questions = open_questions or ["None recorded."]
    next_steps = next_steps or ["Continue project work with Codex Journal context recovery enabled."]

    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    return f"""# Project Memory

Generated by codex-journal. Do not hand-edit routine state; update it through Codex Journal scripts or Codex task completion.

## Project

Name: {analysis.name}
Slug: {analysis.slug}
Root: {analysis.root}
Git Remote: {remote}
Detected Stack: {stack}

## Current Status

{current_status}

## Obsidian

Vault: {config.obsidian_vault}
Project Log Dir: {config.projects_dir}/{analysis.slug}/
Latest Log: {latest_relative}

## Important Decisions

{bullets(decisions)}

## Open Questions

{bullets(open_questions)}

## Next Steps

{bullets(next_steps)}
"""


def write_project_memory(
    project_root: Path,
    analysis: ProjectAnalysis,
    config: JournalConfig,
    latest_relative: str,
    **kwargs: Any,
) -> Path:
    path = project_root / "PROJECT_MEMORY.md"
    path.write_text(
        render_project_memory(analysis, config, latest_relative, **kwargs),
        encoding="utf-8",
    )
    return path


def parse_project_memory(project_root: Path) -> dict[str, str]:
    path = project_root / "PROJECT_MEMORY.md"
    if not path.is_file():
        raise SystemExit(f"PROJECT_MEMORY.md not found in {project_root}")
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {"text": text}
    for key in ("Name", "Slug", "Vault", "Project Log Dir", "Latest Log"):
        match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
        if match:
            fields[key] = match.group(1).strip()
    return fields


def render_daily_log(project_name: str, day: str | None = None) -> str:
    log_day = day or date.today().isoformat()
    return f"""---
date: {log_day}
project: {project_name}
source: codex-journal
---

# {log_day}

## Summary

- Project journal initialized.

## Decisions

- Codex Journal is responsible for generated project memory and daily logs.

## Changes

- Created daily project log.

## Open Items

- Continue recording meaningful Codex work in this log.

## Inferences

- None.

## Next Context For Codex

- Read `PROJECT_MEMORY.md` and this latest log before project-specific work.
"""


def ensure_daily_log(path: Path, project_name: str, day: str | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(render_daily_log(project_name, day), encoding="utf-8")
    return path


def append_to_file(path: Path, entry: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if existing.strip() else ""
    path.write_text(existing.rstrip() + separator + entry.rstrip() + "\n", encoding="utf-8")
