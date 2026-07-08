---
name: project-journal
description: Use the codex-journal plugin to automatically maintain project memory across Codex conversations with generated PROJECT_MEMORY.md files and Obsidian daily logs. Use when starting project work, initializing project journal state, resolving project context, completing a meaningful task, updating project memory, or recording task progress through the plugin scripts.
---

# Project Journal

Use this skill with the `codex-journal` plugin. Project memory and Obsidian logs are generated artifacts maintained by plugin scripts; do not ask the user to run Python commands or hand-edit `PROJECT_MEMORY.md` as the normal workflow.

## User-Facing Contract

The user interacts with this skill in natural language. Treat phrases like these as commands:

- "启用 codex-journal"
- "为这个项目启用项目日志"
- "恢复项目上下文"
- "记录本次任务"
- "更新项目记忆"
- "安装 codex-journal"
- "注册到个人插件区"
- "让 codex-journal 显示在个人插件"

When these intents appear, run the plugin scripts yourself. Do not instruct the user to copy templates, create Markdown files, or execute terminal commands unless filesystem permissions prevent you from doing it.

## Plugin Installation Protocol

When the user asks to install the plugin, register it, or make it appear in the Codex app under Plugins -> Personal, run the installer from the plugin root:

```bash
python3 scripts/install_personal_plugin.py
```

This installer syncs the plugin to `~/plugins/codex-journal`, creates or updates `~/.agents/plugins/marketplace.json`, and runs `codex plugin add codex-journal@personal` when the Codex CLI is available.

If filesystem permissions prevent writing to the user's home directory, request approval for that write. Do not ask the user to hand-edit `marketplace.json`.

## Internal Command Surface

Use the unified script entry point from the plugin root:

```bash
python3 scripts/codex_journal.py <command> ...
```

Supported commands:

- `status`: check whether global config and project memory exist.
- `enable`: initialize global config, project memory, AGENTS instructions, and Obsidian daily log.
- `restore`: print project memory and latest Obsidian log as JSON.
- `record`: draft or append a task log entry.
- `memory`: update generated `PROJECT_MEMORY.md`.

## Startup Protocol

Before project-specific work in a configured project:

1. Check status:

```bash
python3 scripts/codex_journal.py status --project-root <project-root>
```

2. If configured, restore context:

```bash
python3 scripts/codex_journal.py restore --project-root <project-root>
```

3. Continue only from verified project memory, logs, inspected files, tool output, and the current conversation.
4. If memory and logs conflict, report the conflict and ask which source should win before updating either file.

Do not invent prior requirements, decisions, files, or test results. Label inferences explicitly.

## Initialization Protocol

When a project is not configured, initialize it internally.

If global config is missing, ask the user for the Obsidian vault path in natural language. After the user provides it, run:

```bash
python3 scripts/codex_journal.py enable --project-root <project-root> --vault <obsidian-vault>
```

If the global config already exists, omit `--vault`:

```bash
python3 scripts/codex_journal.py enable --project-root <project-root>
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
6. If confirmed, append internally with:

```bash
python3 scripts/codex_journal.py record --project-root <project-root> --confirmed \
  --summary "..." \
  --change "..." \
  --next-context "..."
```

7. Update project memory when status, latest log, decisions, open questions, or next steps changed:

```bash
python3 scripts/codex_journal.py memory --project-root <project-root> \
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
