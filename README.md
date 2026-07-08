# codex-journal

Lightweight project memory for Codex using a reusable Skill, per-project memory files, and Obsidian daily logs.

## What This MVP Provides

- A `project-journal` Codex Skill.
- A project `AGENTS.md` template.
- A project `PROJECT_MEMORY.md` template.
- An Obsidian daily project log template.
- A confirmation-first workflow: Codex drafts logs, then waits for the user to confirm before writing.

This MVP does not auto-discover Obsidian vaults, does not require Obsidian CLI, and does not silently write to your notes.

## Repository Layout

```text
skills/
  project-journal/
    SKILL.md
    agents/openai.yaml
templates/
  AGENTS.md
  PROJECT_MEMORY.md
  obsidian-daily-log.md
docs/
  superpowers/
    specs/
    plans/
```

## Install The Skill

Copy the Skill folder into your Codex skills directory:

```bash
cp -R skills/project-journal ~/.codex/skills/project-journal
```

Restart Codex or start a new conversation so the skill metadata is loaded.

## Configure A Project

In each project that should use the journal workflow:

1. Copy `templates/AGENTS.md` to the project root as `AGENTS.md`.
2. Copy `templates/PROJECT_MEMORY.md` to the project root as `PROJECT_MEMORY.md`.
3. Edit `PROJECT_MEMORY.md` with the project name, current status, and Obsidian paths.
4. Create the Obsidian project log directory, for example `Projects/my-project/`.
5. Create today's log from `templates/obsidian-daily-log.md`.

Example project files:

```text
my-project/
  AGENTS.md
  PROJECT_MEMORY.md
```

Example Obsidian files:

```text
Obsidian Vault/
  Projects/
    my-project/
      2026-07-08.md
```

## Normal Workflow

At the start of a new Codex conversation in a configured project:

1. Codex reads `PROJECT_MEMORY.md`.
2. Codex reads the latest Obsidian log listed there.
3. Codex continues from the recovered project context.

At the end of a meaningful task:

1. Codex drafts an Obsidian log entry.
2. Codex shows the target path.
3. The user confirms whether to write it.
4. Codex appends or creates the daily log only after confirmation.

## Safety Rules

- Codex must not write to Obsidian without user confirmation.
- Codex must not claim it read or wrote files unless it actually did.
- Codex must separate confirmed decisions from open questions and inferences.
- If the Obsidian vault is outside the writable workspace, Codex should request permission or provide the draft for manual insertion.

## Current Limitations

- No automatic new-project initializer yet.
- No required Obsidian CLI integration.
- No MCP or plugin packaging yet.
- No automatic search across multiple projects.

The intended upgrade path is to add an initializer script first, then package the Skill and templates as a personal Codex plugin.
