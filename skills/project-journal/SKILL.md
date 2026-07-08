---
name: project-journal
description: Maintain project memory across Codex conversations using PROJECT_MEMORY.md and Obsidian daily project logs. Use when starting or resuming work in a project, when the user asks to record progress, when a task completes and should be logged, or when setting up lightweight project continuity with AGENTS.md, PROJECT_MEMORY.md, and Obsidian Markdown.
---

# Project Journal

Use this skill to preserve project continuity without relying on prior chat history. Keep project state in `PROJECT_MEMORY.md`, keep human-readable daily logs in Obsidian, and never write logs without user confirmation.

## Startup Context Protocol

When starting or resuming project work:

1. Look for `PROJECT_MEMORY.md` in the project root.
2. If it exists, read it before making project-specific claims.
3. Extract the Obsidian vault path, project log directory, and latest log path.
4. Read the latest Obsidian project log if the path is present and readable.
5. Summarize the recovered context briefly before proceeding when it affects the task.
6. If the memory file or log is missing, state exactly what is missing and continue from available evidence.

Do not invent prior requirements, decisions, files, or test results. If a detail is inferred from context rather than directly read, label it as an inference.

## Task Completion Logging

At the end of a meaningful task, draft an Obsidian log entry before finalizing. Include only information supported by the current conversation, inspected files, or tool output.

Use this structure:

```md
## HH:mm - Codex Task

### Summary
- ...

### Decisions
- ...

### Changes
- ...

### Open Items
- ...

### Inferences
- ...

### Next Context For Codex
- ...
```

Rules:

- Ask the user to confirm before writing to Obsidian.
- If nothing material changed, say no log entry is needed unless the user wants one.
- Keep entries concise enough to scan in Obsidian.
- Separate confirmed decisions from open questions and inferences.
- Mention verification only when it actually ran.

## Write Protocol

Before writing:

1. Show the exact draft entry.
2. State the target Obsidian path.
3. Ask for confirmation.

After confirmation:

1. Read the existing daily log first if it exists.
2. Append the entry under the current date.
3. Create the daily log if it does not exist and the directory is writable.
4. Update `PROJECT_MEMORY.md` only when project status, latest log, decisions, open questions, or next steps changed.

If the Obsidian vault is outside the writable workspace or access is denied, request the required filesystem approval or provide the draft for manual insertion. Never silently skip the write after the user confirmed.

## Project Memory Schema

Expect this structure in `PROJECT_MEMORY.md`:

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

Treat `Latest Log` as a pointer, not proof that it is current. If today's work is logged to a new date, update the pointer after confirmation.

## Obsidian Daily Log Schema

Use this daily log shape when creating new notes:

```md
---
date: YYYY-MM-DD
project: <project-name>
source: codex
---

# YYYY-MM-DD

## Summary

## Decisions

## Changes

## Open Items

## Inferences

## Next Context For Codex
```

Prefer normal Markdown headings and bullets. Obsidian wikilinks and tags are optional; do not introduce them unless the project already uses them or the user asks.

## Setup Protocol

When setting up a project:

1. Add or adapt `AGENTS.md` so it tells Codex to use this skill.
2. Add `PROJECT_MEMORY.md` with project status and Obsidian paths.
3. Create the Obsidian project log directory if writable.
4. Create or reference today's daily log.
5. Keep project-specific facts in `PROJECT_MEMORY.md`, not in the global skill.

## Fallbacks

- No `PROJECT_MEMORY.md`: ask whether to initialize one or continue without project memory.
- Missing Obsidian path: use `PROJECT_MEMORY.md` only and ask for the vault path before writing logs.
- Unreadable latest log: state the path and continue from project memory.
- Unwritable vault: draft the log and ask for approval or manual insertion.
- Conflicting memory and logs: report the conflict and ask which source should win before updating either file.
