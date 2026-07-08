# Project Journal MVP Implementation Plan

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

Expected: validation succeeds. Actual: the official validator could not run because both available Python environments lacked `yaml`; frontmatter was checked with `awk` instead.

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

Create a README explaining what the MVP is, how to copy/install the Skill, how to configure a project, and how the confirmation-before-write workflow works.

- [x] **Step 2: Document current limitations**

State that the MVP does not auto-discover vaults, does not require Obsidian CLI, and does not silently write logs.

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
