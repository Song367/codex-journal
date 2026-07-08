# Project Journal MVP Design

## Purpose

Create a lightweight project-memory workflow for Codex so new conversations can recover the important context of a project without rereading long prior chats. The MVP uses a global Skill, small per-project configuration files, and Obsidian Markdown logs.

The goal is not to build a full plugin yet. The goal is to prove the workflow with minimal moving parts, human confirmation before writes, and files that remain readable outside Codex.

## Recommended Approach

Use a global `project-journal` Skill as the main workflow, with each project carrying two small files:

- `AGENTS.md`: tells Codex that the project uses the project journal protocol.
- `PROJECT_MEMORY.md`: stores the current project summary and Obsidian log location.

Use Obsidian as the personal knowledge base:

- `Projects/<project-name>/YYYY-MM-DD.md`: daily project logs.
- Optional future files: `decisions.md`, `backlog.md`, `index.md`.

This balances Codex usability with human reviewability. Codex gets a stable project entry point, while the user gets a calendar-style project history in Obsidian.

## Scope

In scope for MVP:

- Define a `project-journal` Skill.
- Define per-project `AGENTS.md` and `PROJECT_MEMORY.md` templates.
- Define an Obsidian daily project log template.
- Require Codex to draft logs before writing them.
- Require user confirmation before any Obsidian write.
- Read the latest project log at the start of a new conversation when configured.

Out of scope for MVP:

- Full plugin packaging.
- Automatic project detection across all repositories.
- Automatic Obsidian vault discovery.
- Obsidian CLI integration as a required dependency.
- MCP server integration.
- Silent automatic writes without user confirmation.
- Cross-project global memory merging.

## Architecture

The MVP has three layers.

### Global Skill

The `project-journal` Skill defines reusable behavior:

1. At conversation start or when asked to resume a project, check for `PROJECT_MEMORY.md`.
2. Read `PROJECT_MEMORY.md`.
3. Read the latest Obsidian project log referenced by `PROJECT_MEMORY.md`.
4. Use both files as the working context.
5. At task completion, generate an Obsidian log draft.
6. Ask the user to confirm before writing.
7. After confirmation, append or create the current daily log.

The Skill should be global because the workflow applies across projects.

### Project Files

Each project keeps only project-specific context.

`AGENTS.md` should be small and durable:

```md
# Codex Project Instructions

This project uses the global project-journal skill.

At the start of a new conversation:
1. Read PROJECT_MEMORY.md.
2. Read the latest Obsidian project log listed there.
3. Continue with that context.

At the end of a task:
1. Generate a project log draft.
2. Ask the user to confirm before writing it.
```

`PROJECT_MEMORY.md` should be the project entry point:

```md
# Project Memory

## Project
Name: <project-name>

## Current Status
<one-paragraph summary>

## Obsidian
Vault: <absolute-path-to-obsidian-vault>
Project Log Dir: Projects/<project-name>/
Latest Log: Projects/<project-name>/YYYY-MM-DD.md

## Important Decisions
- ...

## Open Questions
- ...

## Next Steps
- ...
```

### Obsidian Vault

Obsidian stores time-based, human-readable logs:

```text
Obsidian Vault/
  Projects/
    <project-name>/
      2026-07-08.md
      decisions.md        # optional future file
      backlog.md          # optional future file
      index.md            # optional future file
```

Daily log template:

```md
---
date: YYYY-MM-DD
project: <project-name>
source: codex
---

# YYYY-MM-DD

## Summary
What happened today.

## Decisions
- Confirmed decisions.

## Changes
- Files, behavior, docs, or artifacts changed.

## Open Items
- Follow-up work or unresolved questions.

## Next Context For Codex
What the next new conversation should know first.
```

## Workflow Details

### New Conversation Resume

When a conversation starts in a project:

1. Check whether `PROJECT_MEMORY.md` exists in the project root.
2. If present, read it before making project-specific claims.
3. Find `Obsidian.Vault`, `Project Log Dir`, and `Latest Log`.
4. Read the latest log if the path is readable.
5. If the Obsidian path is missing or unreadable, state that clearly and continue from `PROJECT_MEMORY.md`.
6. Do not infer unavailable prior conversation details.

### Task Completion Logging

At the end of a task:

1. Generate a concise log draft in Obsidian Markdown.
2. Include only facts supported by the current conversation, inspected files, or tool output.
3. Separate confirmed decisions from inferred context.
4. Ask the user to confirm before writing.
5. If confirmed, create or append to the current daily log.
6. Update `PROJECT_MEMORY.md` only when the project status, latest log path, decisions, open questions, or next steps changed.

### Write Policy

The MVP should default to safe writes:

- Never write to Obsidian without user confirmation.
- Never overwrite an existing daily log without reading it first.
- Prefer appending a dated section if a daily log already exists.
- If the Obsidian vault is outside the writable workspace, request approval or provide the draft for manual use.

## Obsidian Skill Usage

The MVP may optionally use Obsidian-oriented Skills such as `obsidian-markdown` from `kepano/obsidian-skills` for Markdown conventions.

Do not require `obsidian-cli` for MVP. Direct Markdown file reads and writes are enough if the vault path is accessible.

Recommended split:

- `project-journal`: owns the project memory workflow.
- `obsidian-markdown`: optional formatting guidance.
- `obsidian-cli`: optional future integration for CLI-based vault operations.

## Skill Design

The `project-journal` Skill should be concise and procedural.

Suggested trigger description:

```yaml
---
name: project-journal
description: Maintain project memory across Codex conversations using PROJECT_MEMORY.md and Obsidian daily project logs. Use when starting or resuming work in a project, when the user asks to record progress, when a task completes and should be logged, or when setting up lightweight project continuity with AGENTS.md, PROJECT_MEMORY.md, and Obsidian Markdown.
---
```

The Skill body should include:

- Startup context protocol.
- Task-end log drafting protocol.
- Confirmation-before-write rule.
- `PROJECT_MEMORY.md` schema.
- Obsidian daily log schema.
- Permission and fallback handling.

For MVP, scripts are optional. Add scripts later only if repeated manual setup becomes annoying or write operations need deterministic handling.

## Initialization Flow

Initial setup for a project:

1. Add `AGENTS.md`.
2. Add `PROJECT_MEMORY.md`.
3. Create the Obsidian project directory.
4. Create or point to today's daily log.
5. Start future Codex conversations from the project root.

Future automation may provide:

```bash
init-project-journal <project-name> <vault-path>
```

That script is not required for MVP.

## Verification

MVP verification should prove these behaviors:

1. A new conversation can identify and read `PROJECT_MEMORY.md`.
2. Codex can locate the latest Obsidian project log from that file.
3. Codex can summarize the recovered context without inventing missing details.
4. Codex can produce a task-end log draft.
5. Codex waits for user confirmation before writing.
6. Codex can append to or create a daily log when the path is writable.
7. Codex reports clearly when the Obsidian vault is not writable.

## Risks

### Stale Latest Log

`PROJECT_MEMORY.md` may point to an old `Latest Log`.

Mitigation: when logging a new task, update the `Latest Log` field after confirmation.

### Overgrown Logs

Daily logs may become too long.

Mitigation: keep task entries concise and use `Next Context For Codex` as the compressed handoff section.

### Permission Friction

The Obsidian vault may be outside Codex's writable workspace.

Mitigation: MVP generates a draft first. Writing requires confirmation and, when needed, filesystem approval.

### False Memory

Codex may summarize something as decided when it was only discussed.

Mitigation: the Skill must distinguish `Decisions`, `Open Items`, and `Inferences`.

## Future Upgrade Path

After MVP proves useful:

1. Add an initialization script to create project files and Obsidian folders.
2. Add a small validation script for `PROJECT_MEMORY.md`.
3. Integrate `obsidian-markdown` formatting rules more explicitly.
4. Add optional `obsidian-cli` support.
5. Package the Skill, templates, and scripts as a personal Plugin.
6. Add commands such as `project-journal:init`, `project-journal:log`, and `project-journal:resume`.

## Acceptance Criteria

The MVP is successful when:

- New projects require only a small `AGENTS.md` and `PROJECT_MEMORY.md`.
- New Codex conversations can restore the important project context from those files and the latest Obsidian log.
- The user receives a clear log draft at task completion.
- Nothing is written to Obsidian until the user confirms.
- The resulting Obsidian notes remain useful when read directly by a human.
