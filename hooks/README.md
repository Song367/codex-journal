# Hooks

Codex Journal is designed to support future lifecycle hooks for:

- resolving project context at the start of project work
- appending task logs at the end of meaningful work
- updating generated project memory after task completion

This directory is intentionally not declared in `.codex-plugin/plugin.json` yet. The current local plugin validator rejects unsupported manifest fields such as `hooks`, so the plugin ships validated command scripts first and keeps hook integration as a future compatibility layer.
