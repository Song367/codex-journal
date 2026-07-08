# codex-journal

Codex Journal is a local Codex plugin for automatic project memory.

After the plugin is installed, users interact with it through natural language. The Python scripts are plugin internals that Codex calls on the user's behalf.

## User Experience

In a project, say:

```text
启用 codex-journal
```

Codex should then:

1. Check whether the project already has journal memory.
2. Ask for the Obsidian vault path if global config is missing.
3. Analyze the project.
4. Generate or update `AGENTS.md`.
5. Generate or update `PROJECT_MEMORY.md`.
6. Create the Obsidian project folder and today's daily log.

For future conversations in the same project, Codex should automatically read:

- `PROJECT_MEMORY.md`
- the latest Obsidian log referenced inside it

At the end of meaningful work, Codex should automatically prepare a task log. With the default config, Codex asks before writing:

```json
{
  "require_confirmation_before_write": true
}
```

## Natural Language Intents

Users should say things like:

```text
启用 codex-journal
恢复项目上下文
记录本次任务
更新项目记忆
```

Users should not need to run Python commands, copy Markdown templates, or manually create Obsidian notes.

## What The Plugin Maintains

Global:

```text
~/.codex-journal/config.json
```

Per project:

```text
AGENTS.md
PROJECT_MEMORY.md
```

In Obsidian:

```text
Projects/<project-slug>/YYYY-MM-DD.md
```

## Plugin Layout

```text
.codex-plugin/
  plugin.json
skills/
  project-journal/
scripts/
  codex_journal.py
  codex_journal_common.py
  init_project_journal.py
  resolve_project_context.py
  update_project_memory.py
  append_obsidian_log.py
templates/
hooks/
```

## Developer Debugging

The unified internal command surface is:

```bash
python3 scripts/codex_journal.py <command>
```

Supported internal commands:

```text
status   check config and project memory
enable   initialize project memory and Obsidian logs
restore  print project memory and latest log JSON
record   draft or append task logs
memory   update generated PROJECT_MEMORY.md
```

These commands are for Codex/plugin implementation and debugging. They are not the normal user interface.

## Hooks Status

The repository includes `hooks/` documentation for the intended lifecycle integration, but `.codex-plugin/plugin.json` does not declare hooks yet. The current local plugin validator rejects unsupported manifest fields such as `hooks`, so scripts are the stable command surface for now.

## Validate

Validate the plugin:

```bash
python3 /Users/wadesong/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Validate the Skill:

```bash
PYTHONPATH=/private/tmp/codex-journal-pydeps \
python3 /Users/wadesong/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/project-journal
```
