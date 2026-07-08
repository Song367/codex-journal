# Codex Journal Plugin Design

## Purpose

Build `codex-journal` as a Codex plugin, not a template-only MVP. The plugin should help Codex maintain project memory automatically across conversations by combining a global configuration file, project-local generated memory files, and Obsidian daily logs.

Users should not manually edit `PROJECT_MEMORY.md`, create Obsidian logs, or run Python commands as the normal workflow. Users express intent in natural language; Codex uses the Skill to call plugin scripts internally.

## Confirmed Decisions

- Default write policy: `require_confirmation_before_write: true`.
- Plugin implementation target: repository-local plugin only for now.
- Do not write a personal marketplace entry yet.
- Global config path: `~/.codex-journal/config.json`.
- Keep hook support experimental until the local plugin validator accepts hook manifest fields.

## Architecture

```text
codex-journal/
  .codex-plugin/
    plugin.json
  skills/
    project-journal/
      SKILL.md
      agents/openai.yaml
  scripts/
    codex_journal.py
    codex_journal_common.py
    init_project_journal.py
    resolve_project_context.py
    update_project_memory.py
    append_obsidian_log.py
  templates/
    AGENTS.md
    PROJECT_MEMORY.md
    obsidian-daily-log.md
  hooks/
    README.md
```

## Global Configuration

Default config path:

```text
~/.codex-journal/config.json
```

Schema:

```json
{
  "obsidian_vault": "/absolute/path/to/Obsidian",
  "projects_dir": "Projects",
  "require_confirmation_before_write": true,
  "auto_update_project_memory": true,
  "auto_log_tasks": true
}
```

Scripts also support `--config` and `CODEX_JOURNAL_CONFIG` so tests and advanced users can avoid writing to the default home path.

## User-Facing Interaction

Users interact with the plugin through natural language:

```text
启用 codex-journal
恢复项目上下文
记录本次任务
更新项目记忆
```

Codex maps these intents to the unified internal command surface. The user should not be asked to copy templates, run scripts, or create Markdown notes unless the environment blocks Codex from doing so.

## Project Initialization

When the user asks to enable Codex Journal, Codex internally runs `scripts/codex_journal.py enable`. It:

1. Reads or creates global config.
2. Analyzes the current project:
   - directory name
   - git remote
   - README heading or first useful line
   - common stack files such as `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`
3. Writes or updates generated `PROJECT_MEMORY.md`.
4. Writes or updates project `AGENTS.md`.
5. Creates the Obsidian project log directory.
6. Creates today's daily log.
7. Points `PROJECT_MEMORY.md` to the latest log.

The user provides the vault path once, either by config file or by passing `--vault`.

## Runtime Behavior

At the start of project work, `project-journal` instructs Codex to:

1. Read `PROJECT_MEMORY.md`.
2. Read the latest Obsidian log listed in it.
3. Summarize the recovered context only when it matters to the task.
4. Continue from verified project memory, not assumed chat history.

At task completion, Codex should:

1. Generate a task log entry automatically.
2. Update project memory when status, decisions, open questions, or next steps changed.
3. Respect `require_confirmation_before_write`.
4. Use scripts for deterministic writes when possible.

## Script Responsibilities

### `codex_journal.py`

Unified internal command surface for Codex. It exposes:

- `status`
- `enable`
- `restore`
- `record`
- `memory`

The Skill should call this script instead of asking users to run commands directly.

### `codex_journal_common.py`

Shared config loading, project analysis, path handling, markdown helpers, and safe file writes.

### `init_project_journal.py`

Primary setup command. It creates global config if `--vault` is provided, generates project memory, AGENTS instructions, and today's Obsidian note.

### `resolve_project_context.py`

Reads `PROJECT_MEMORY.md` and the latest log, then prints a compact JSON payload for Codex to use as startup context.

### `update_project_memory.py`

Updates generated fields in `PROJECT_MEMORY.md`, especially latest log, status, decisions, open questions, and next steps.

### `append_obsidian_log.py`

Appends a task entry to the correct daily note. With confirmation enabled, it writes only when called with `--confirmed`.

## Hooks And Commands

The repository includes a `hooks/` directory documenting intended lifecycle hooks, but `.codex-plugin/plugin.json` does not declare hooks yet because the current local plugin validator rejects unsupported manifest fields.

For now, `scripts/codex_journal.py` is the stable internal command surface. The Skill tells Codex when to call it.

## Safety

- Default to confirmation before writes.
- Never overwrite user content silently.
- Generated files include a generated section marker where needed.
- Existing `AGENTS.md` is preserved by appending/updating a Codex Journal section.
- Existing Obsidian daily notes are appended to, not replaced.
- If config is missing and no vault is supplied, initialization fails with a clear message.

## Verification

Use a temporary sample project and temporary fake Obsidian vault:

1. Run `codex_journal.py status` and verify the sample project is unconfigured.
2. Run `codex_journal.py enable --project-root <sample> --vault <vault> --config <tmp-config>`.
3. Verify sample project has `AGENTS.md` and `PROJECT_MEMORY.md`.
4. Verify fake vault has `Projects/<project>/YYYY-MM-DD.md`.
5. Run `codex_journal.py restore` and verify it returns project memory plus latest log text.
6. Run `codex_journal.py record` without confirmation and verify it returns a confirmation-required draft.
7. Run `codex_journal.py record --confirmed` and verify the log entry is appended.
8. Run `codex_journal.py memory` and verify generated project memory updates.
9. Run plugin validation and Skill validation.

## Acceptance Criteria

- The repository validates as a Codex plugin.
- The Skill validates as a Codex Skill.
- Project setup does not require hand-editing `PROJECT_MEMORY.md`.
- Obsidian project directory and daily log are created by script.
- New conversations can recover project context from generated files.
- Task logging can be performed by script and respects confirmation policy.
