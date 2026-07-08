#!/usr/bin/env python3
"""Install codex-journal into the default personal Codex plugin marketplace."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLUGIN_NAME = "codex-journal"
DEFAULT_PLUGIN_PARENT = Path.home() / "plugins"
DEFAULT_MARKETPLACE_PATH = Path.home() / ".agents" / "plugins" / "marketplace.json"
DEFAULT_MARKETPLACE_NAME = "personal"
DEFAULT_CATEGORY = "Productivity"
MANAGED_ENTRIES = (
    ".codex-plugin",
    "skills",
    "scripts",
    "templates",
    "hooks",
    "README.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy this plugin to ~/plugins/codex-journal and register it in the "
            "default personal Codex marketplace."
        )
    )
    parser.add_argument(
        "--source",
        default=str(Path(__file__).resolve().parents[1]),
        help="Source plugin root. Defaults to the repository root containing this script.",
    )
    parser.add_argument(
        "--plugin-parent",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Parent directory for personal plugins. Defaults to ~/plugins.",
    )
    parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to personal marketplace.json. Defaults to ~/.agents/plugins/marketplace.json.",
    )
    parser.add_argument(
        "--marketplace-name",
        default=DEFAULT_MARKETPLACE_NAME,
        help="Marketplace name to seed when creating a new marketplace file.",
    )
    parser.add_argument(
        "--skip-codex-add",
        action="store_true",
        help="Only sync files and update marketplace.json; do not run `codex plugin add`.",
    )
    parser.add_argument(
        "--no-cachebuster",
        action="store_true",
        help="Do not add a local Codex cachebuster suffix to the installed manifest version.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned install operation without writing files.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return payload


def write_json(path: Path, payload: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_plugin_name(plugin_root: Path) -> str:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    name = manifest.get("name")
    if name != PLUGIN_NAME:
        raise ValueError(f"{manifest_path} must declare name '{PLUGIN_NAME}'.")
    return name


def copy_entry(source: Path, target: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sync_plugin(source_root: Path, target_root: Path, *, dry_run: bool) -> list[str]:
    copied: list[str] = []
    if source_root == target_root:
        raise ValueError("Source and target plugin roots are the same path.")
    for entry in MANAGED_ENTRIES:
        source = source_root / entry
        if not source.exists():
            continue
        copy_entry(source, target_root / entry, dry_run=dry_run)
        copied.append(entry)
    if ".codex-plugin" not in copied:
        raise ValueError(f"Missing required manifest directory in source: {source_root}")
    return copied


def marketplace_entry() -> dict[str, Any]:
    return {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": DEFAULT_CATEGORY,
    }


def load_or_create_marketplace(path: Path, marketplace_name: str) -> dict[str, Any]:
    if path.exists():
        payload = load_json(path)
    else:
        payload = {
            "name": marketplace_name,
            "interface": {
                "displayName": "Personal",
            },
            "plugins": [],
        }

    existing_name = payload.get("name")
    if not isinstance(existing_name, str) or not existing_name.strip():
        raise ValueError(f"{path} must contain a non-empty string field 'name'.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", existing_name):
        raise ValueError(f"{path} has invalid marketplace name '{existing_name}'.")

    interface = payload.setdefault("interface", {"displayName": "Personal"})
    if not isinstance(interface, dict):
        raise ValueError(f"{path} field 'interface' must be an object.")
    plugins = payload.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError(f"{path} field 'plugins' must be an array.")
    return payload


def upsert_marketplace(path: Path, marketplace_name: str, *, dry_run: bool) -> str:
    payload = load_or_create_marketplace(path, marketplace_name)
    plugins = payload["plugins"]
    entry = marketplace_entry()
    action = "added"
    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            action = "updated"
            break
    else:
        plugins.append(entry)
    write_json(path, payload, dry_run=dry_run)
    return action


def add_cachebuster(source_root: Path, target_root: Path, *, dry_run: bool) -> str:
    manifest_root = source_root if dry_run else target_root
    manifest_path = manifest_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"{manifest_path} must contain a non-empty string field 'version'.")
    base_version = version.split("+", 1)[0]
    token = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    next_version = f"{base_version}+codex.{token}"
    manifest["version"] = next_version
    write_json(manifest_path, manifest, dry_run=dry_run)
    return next_version


def run_codex_add(marketplace_name: str, *, dry_run: bool) -> dict[str, Any]:
    command = ["codex", "plugin", "add", f"{PLUGIN_NAME}@{marketplace_name}"]
    if dry_run:
        return {"command": command, "skipped": "dry_run"}
    if shutil.which("codex") is None:
        return {"command": command, "skipped": "codex_cli_not_found"}
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main() -> None:
    args = parse_args()
    source_root = Path(args.source).expanduser().resolve()
    target_root = Path(args.plugin_parent).expanduser().resolve() / PLUGIN_NAME
    marketplace_path = Path(args.marketplace_path).expanduser().resolve()

    plugin_name = read_plugin_name(source_root)
    copied = sync_plugin(source_root, target_root, dry_run=args.dry_run)
    installed_version = (
        None
        if args.no_cachebuster
        else add_cachebuster(source_root, target_root, dry_run=args.dry_run)
    )
    marketplace_action = upsert_marketplace(
        marketplace_path,
        args.marketplace_name,
        dry_run=args.dry_run,
    )
    codex_add = (
        {"skipped": "requested"}
        if args.skip_codex_add
        else run_codex_add(args.marketplace_name, dry_run=args.dry_run)
    )
    print(
        json.dumps(
            {
                "plugin": plugin_name,
                "source": str(source_root),
                "target": str(target_root),
                "copied": copied,
                "installed_version": installed_version,
                "marketplace": str(marketplace_path),
                "marketplace_action": marketplace_action,
                "codex_add": codex_add,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - CLI should surface one clear error.
        print(f"install_personal_plugin.py error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
