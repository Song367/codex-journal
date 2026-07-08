# Project Journal MVP Implementation Plan

> Superseded: this plan has been replaced by `docs/superpowers/plans/2026-07-08-codex-journal-plugin-implementation.md`. The current product direction is a repository-local Codex plugin with scripts, generated project memory, and automatic Obsidian log creation.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the repository MVP for a reusable Codex project journal Skill with project and Obsidian templates.

**Architecture:** The repository ships an installable Skill folder plus plain Markdown templates. The Skill owns runtime behavior; templates give each project the minimum files needed to participate in the workflow.

**Tech Stack:** Codex Skills, Markdown, YAML frontmatter, shell-based validation.

---

### Task 1: Skill Package

**Files:**
- Create: `skills/project-journal/SKILL.md`
- Create: `skills/project-journal/agents/openai.yaml`

- [x] **Step 1: Create the Skill instructions**

Create `skills/project-journal/SKILL.md` with YAML frontmatter, startup context protocol, task-end logging protocol, confirmation-before-write rules, templates, and fallback behavior.

- [x] **Step 2: Create Skill UI metadata**

Create `skills/project-journal/agents/openai.yaml` with a concise display name, description, and default prompt for the Skill.

- [x] **Step 3: Verify Skill metadata**

Run: `python3 /Users/wadesong/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/project-journal`

Expected: validation succeeds. Actual: installed PyYAML into `/private/tmp/codex-journal-pydeps` and ran the official validator with `PYTHONPATH`; validation succeeded with `Skill is valid!`.

### Task 2: Templates

**Files:**
- Create: `templates/AGENTS.md`
- Create: `templates/PROJECT_MEMORY.md`
- Create: `templates/obsidian-daily-log.md`

- [x] **Step 1: Create project `AGENTS.md` template**

Create a minimal template that tells Codex to use the `project-journal` Skill and read `PROJECT_MEMORY.md`.

- [x] **Step 2: Create `PROJECT_MEMORY.md` template**

Create a project-state schema with current status, Obsidian paths, decisions, open questions, and next steps.

- [x] **Step 3: Create Obsidian daily log template**

Create a daily log with frontmatter, summary, decisions, changes, open items, inferences, and next context sections.

### Task 3: Repository Guide

**Files:**
- Create: `README.md`

- [x] **Step 1: Document MVP usage**

Create a README for the historical template-only MVP. This has been superseded by the plugin README and should not be used as the current setup path.

- [x] **Step 2: Document historical MVP limitations**

State the historical template-only MVP limitations. These limitations are superseded by the plugin implementation plan.

### Task 4: Verification

**Files:**
- Modify: none expected

- [x] **Step 1: Check repository structure**

Run: `find . -maxdepth 4 -type f | sort`

Expected: shows the design doc, implementation plan, README, Skill files, and templates.

- [x] **Step 2: Search for unfinished placeholder markers**

Run: `rg -n "T""BD|TO""DO|FIX""ME" README.md skills templates docs`

Expected: no unfinished marker output.

- [x] **Step 3: Review git diff**

Run: `git diff --stat`

Expected: only MVP implementation files are changed.
