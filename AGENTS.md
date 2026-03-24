# AGENTS.md — Repository Map for AI Agents

Quick-reference for navigating this codebase. Read this first, then drill into specific files.

## What is Frai?

Cross-IDE AI agent framework. Manages tasks, sessions, and project memory via SQLite + FTS5.

## Directory Structure

```
scripts/           → Core Python code (CLI, service, backend, gates)
references/        → Documentation (CLI reference, architecture, getting-started)
agents/            → IDE-specific skills, roles, stacks, MCP servers
  claude/skills/   → 8 core skill definitions (SKILL.md files)
  claude/roles/    → Role profiles (developer, architect, qa, tech-writer, ui-ux)
  claude/stacks/   → Stack guides (python, react, typescript, go, vue)
  claude/mcp/      → MCP servers (project, codebase-rag)
  cursor/          → Mirror of claude/ for Cursor IDE
bootstrap/         → Bootstrap script for submodule projects
tests/             → pytest tests
.frai/             → Runtime data (DB, config, venv) — gitignored
```

## Key Entry Points

| What you want | Where to look |
|---------------|---------------|
| Run a CLI command | `scripts/project.py` → dispatches to handlers |
| Add a CLI subcommand | `scripts/project_parser.py` (argparse tree) |
| Add a CLI handler | `scripts/project_cli.py` or `scripts/project_cli_extra.py` |
| Business logic | `scripts/project_service.py` + `scripts/service_knowledge.py` |
| Database schema | `scripts/backend_schema.py` |
| Migrations | `scripts/backend_migrations.py` |
| Quality gates config | `scripts/project_config.py` (DEFAULT_GATES) |
| Run quality gates | `scripts/gate_runner.py` |
| Type definitions | `scripts/project_types.py` |
| Add a new skill | `agents/claude/skills/<name>/SKILL.md` |
| Add a role profile | `agents/claude/roles/<name>.md` |
| Add a stack guide | `agents/claude/stacks/<name>.md` |
| MCP server (project) | `agents/claude/mcp/project/server.py` |
| MCP server (RAG) | `agents/claude/mcp/codebase-rag/server.py` |
| Bootstrap logic | `bootstrap/bootstrap.py` |

## How Things Connect

```
User → Skill (SKILL.md) → CLI (.frai/frai) → project.py → service → backend → SQLite
                        → MCP tools (frai-project server) → service → backend → SQLite
                        → gate_runner.py → runs checks → pass/fail
```

## Conventions

- **Layers:** CLI never touches DB directly. Service validates, backend executes.
- **Slugs:** `^[a-z0-9][a-z0-9-]*$`, max 64 chars.
- **Cascades:** All tasks done → story auto-closes → epic auto-closes.
- **Gates:** Configured in `.frai/config.json` under `"gates"` key. See `frai gates status`.
- **Roles:** Free-text (any string). Common: developer, architect, qa, tech-writer.

## Testing

```bash
pytest tests/ -v          # all tests
pytest tests/test_gates.py  # quality gates specifically
```

## Docs

- `CLAUDE.md` — constraints and project overview (keep concise)
- `references/project-cli.md` — full CLI reference
- `references/architecture.md` — detailed architecture, modules, testing
- `references/getting-started.md` — onboarding guide
