# Agent workflow adoption - 2026-11-06

Added shared routing, native Codex/Claude worker definitions, scoped context, app registry,
scaffold/bootstrap commands and secret-free structural CI. Product code is unchanged.
Existing product/release constraints remain. Configuration validation is not an app build.

Files in this change:
- `.agent/CHANGELOG.md`
- `.agent/WORKFLOW.md`
- `.agent/apps.json`
- `.agent/context.md`
- `.agent/templates/AGENTS.md`
- `.agent/templates/context.md`
- `.agent/toolkit.json`
- `.claude/agents/flow-checker.md`
- `.claude/agents/workhorse.md`
- `.claude/settings.json`
- `.codex/agents/flow-checker.toml`
- `.codex/agents/workhorse.toml`
- `.codex/config.toml`
- `.github/workflows/agent-workflow.yml`
- `AGENTS.md`
- `CLAUDE.md`
- `tools/agent_workflow.py`
- `tools/test_agent_workflow.py`
