# Scripts

Frai framework modules. Python 3.11+ stdlib only.

## Architecture: CLI → Service → Backend

| Module | Purpose |
|--------|---------|
| `project.py` | Entry point: argparse dispatch |
| `project_parser.py` | Argparse command tree |
| `project_cli.py` | CLI handlers: task, session, epic, story, search, etc. |
| `project_cli_extra.py` | CLI handlers: memory, gates, skill, fts |
| `project_service.py` | Business logic: task lifecycle, cascades, validation |
| `service_knowledge.py` | KnowledgeMixin: memory, decisions, events |
| `project_backend.py` | SQLiteBackend: CRUD operations |
| `backend_schema.py` | Schema: 7 tables, 3 FTS5, triggers, indexes |
| `backend_queries.py` | Complex queries: search, metrics, roadmap |
| `backend_migrations.py` | Schema migrations v1 → v9 |
| `project_config.py` | Config loader, gates config, service factory |
| `project_types.py` | Constants: valid statuses, stacks, complexities |
| `gate_runner.py` | Quality gates execution engine |
| `frai_version.py` | Version: 2.0.0 |
| `frai_utils.py` | Utilities: utcnow_iso, ServiceError, validators |

## MCP Servers

Located in `agents/{ide}/mcp/`:

| Server | Purpose |
|--------|---------|
| `project/` | Full project management (tasks, sessions, memory, decisions) |
| `codebase-rag/` | Code search via FTS5 |

## Usage

```bash
# Always via .frai/frai wrapper
.frai/frai status
.frai/frai task quick "Fix bug"
.frai/frai search "auth"
```

Full CLI reference: `references/project-cli.md`
