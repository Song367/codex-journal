# Codex Journal Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `codex-journal` from a template MVP into a repository-local Codex plugin with automatic project initialization and script-driven journal updates.

**Architecture:** The plugin manifest exposes the existing Skill. Scripts provide deterministic setup, context resolution, project memory updates, and Obsidian log appends. Templates become internal generation assets, not instructions for users to manually edit.

**Tech Stack:** Codex plugin manifest, Codex Skill, Python 3 standard library, Markdown, JSON.

---

### Task 1: Plugin Skeleton

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `hooks/README.md`

- [x] **Step 1: Add plugin manifest**

Create a validation-ready `.codex-plugin/plugin.json` with `skills: "./skills/"`, interface metadata, author metadata, and no unsupported `hooks` field.

- [x] **Step 2: Add hooks documentation**

Create `hooks/README.md` explaining that hooks are intentionally experimental and not declared in the manifest until validator/runtime support is confirmed.

### Task 2: Python Command Surface

**Files:**
- Create: `scripts/codex_journal_common.py`
- Create: `scripts/init_project_journal.py`
- Create: `scripts/resolve_project_context.py`
- Create: `scripts/update_project_memory.py`
- Create: `scripts/append_obsidian_log.py`

- [x] **Step 1: Implement shared helpers**

Create config loading, project analysis, generated markdown rendering, safe section replacement, and path helpers.

- [x] **Step 2: Implement initialization**

Create project `AGENTS.md`, generated `PROJECT_MEMORY.md`, global config when `--vault` is passed, and the Obsidian daily note.

- [x] **Step 3: Implement context resolution**

Print JSON containing project memory text, latest log path, and latest log text.

- [x] **Step 4: Implement memory updates**

Update generated `PROJECT_MEMORY.md` fields from CLI arguments.

- [x] **Step 5: Implement log appending**

Append a task entry to today's Obsidian note only when confirmation policy allows it or `--confirmed` is passed.

### Task 3: Skill And Docs Rewrite

**Files:**
- Modify: `skills/project-journal/SKILL.md`
- Modify: `README.md`
- Modify: `templates/AGENTS.md`
- Modify: `templates/PROJECT_MEMORY.md`
- Modify: `templates/obsidian-daily-log.md`

- [x] **Step 1: Rewrite Skill around plugin scripts**

Make automatic startup context recovery and task-end logging the default behavior. Point Codex to scripts instead of user-triggered manual templates.

- [x] **Step 2: Rewrite README**

Document plugin-local installation, global config, initialization command, and script-based workflows.

- [x] **Step 3: Rewrite templates as generated assets**

Clarify that templates are script inputs, not user-edit instructions.

### Task 4: End-To-End Verification

**Files:**
- Test artifacts only under `/private/tmp`

- [x] **Step 1: Run initialization against temp project**

Run `scripts/init_project_journal.py` with temp project, temp vault, and temp config.

- [x] **Step 2: Resolve generated context**

Run `scripts/resolve_project_context.py` against the temp project and verify JSON output includes memory and log text.

- [x] **Step 3: Append confirmed log**

Run `scripts/append_obsidian_log.py --confirmed` and verify the temp Obsidian note changed.

- [x] **Step 4: Validate plugin and Skill**

Run official plugin validator and Skill validator.
