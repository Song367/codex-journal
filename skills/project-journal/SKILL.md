---
name: project-journal
description: Use the codex-journal plugin to automatically maintain project memory across Codex conversations with generated PROJECT_MEMORY.md files and Obsidian daily logs. Use when starting project work, initializing project journal state, resolving project context, completing a meaningful task, updating project memory, or recording task progress through the plugin scripts.
---

# Project Journal

Use this skill with the `codex-journal` plugin. Project memory and Obsidian logs are generated artifacts maintained by scripts; do not ask the user to hand-edit `PROJECT_MEMORY.md` as the normal workflow.

## Startup Protocol

Before project-specific work in a configured project:

1. Read `PROJECT_MEMORY.md`.
2. Read the latest Obsidian log referenced by `PROJECT_MEMORY.md`.
3. If deterministic parsing is useful, run:

```bash
python3 scripts/resolve_project_context.py --project-root <project-root>
```

4. Continue only from verified project memory, logs, inspected files, tool output, and the current conversation.
5. If memory and logs conflict, report the conflict and ask which source should win before updating either file.

Do not invent prior requirements, decisions, files, or test results. Label inferences explicitly.

## Initialization Protocol

When a project is not configured, initialize it with:

```bash
python3 scripts/init_project_journal.py --project-root <project-root> --vault <obsidian-vault>
```

If the global config already exists, omit `--vault`:

```bash
python3 scripts/init_project_journal.py --project-root <project-root>
```

The script generates or updates:

- `AGENTS.md`
- `PROJECT_MEMORY.md`
- the Obsidian project directory
- today's Obsidian daily log
- `~/.codex-journal/config.json` when `--vault` is provided

## Task Completion Protocol

At the end of meaningful work, automatically prepare a journal update. Do not wait for the user to ask for logging.

1. Draft the entry from facts in the current conversation, inspected files, and tool output.
2. Include only verification that actually ran.
3. Separate confirmed decisions, changes, open items, inferences, and next context.
4. Check the global `require_confirmation_before_write` setting.
5. If confirmation is required, show the draft and target path before writing.
6. If confirmed, append with:

```bash
python3 scripts/append_obsidian_log.py --project-root <project-root> --confirmed \
  --summary "..." \
  --change "..." \
  --next-context "..."
```

7. Update project memory when status, latest log, decisions, open questions, or next steps changed:

```bash
python3 scripts/update_project_memory.py --project-root <project-root> \
  --status "..." \
  --latest-log "Projects/<project-slug>/YYYY-MM-DD.md" \
  --decision "..." \
  --next-step "..."
```

If `require_confirmation_before_write` is `false`, the append script may write without `--confirmed`.

## Write Policy

- Default config sets `require_confirmation_before_write` to `true`.
- Never silently overwrite user content.
- Existing `AGENTS.md` is preserved outside the generated Codex Journal section.
- Existing Obsidian daily logs are appended to, not replaced.
- If the Obsidian vault is outside the writable workspace, request filesystem approval or provide the exact command/draft for the user to run.

## Generated File Expectations

`PROJECT_MEMORY.md` is generated and maintained by plugin scripts. It should contain:

- project name, slug, root, git remote, and detected stack
- current status
- Obsidian vault, project log directory, and latest log
- important decisions
- open questions
- next steps

`AGENTS.md` contains a generated Codex Journal section that tells future Codex conversations to read project memory and latest logs before project-specific work.

## Fallbacks

- Missing global config: initialize with `--vault`.
- Missing `PROJECT_MEMORY.md`: run `init_project_journal.py`.
- Missing latest log: run initialization again or create the daily log through `append_obsidian_log.py --confirmed`.
- Unwritable vault: request permission or stop with the draft and target path.
- Unsupported hooks: use scripts directly; hooks are experimental until plugin manifest validation accepts them.
