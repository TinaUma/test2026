# Frai Architecture Reference

## Key Modules

| File | Lines | Purpose |
|------|-------|---------|
| `project_backend.py` | ~393 | SQLiteBackend: WAL, FTS5, metrics, roadmap, all CRUD |
| `backend_schema.py` | ~210 | DDL: 8 tables, 3 FTS virtual tables, triggers, indexes |
| `backend_migrations.py` | ~355 | Version-by-version SQL migrations (v1→v11) |
| `backend_queries.py` | ~310 | Complex aggregations: roadmap, metrics, search, graph traversal |
| `project_service.py` | ~384 | ProjectService + HierarchyMixin + TaskMixin + SessionMixin |
| `service_knowledge.py` | ~200 | KnowledgeMixin: memory, decisions, graph memory |
| `project_cli.py` | ~269 | Core CLI handlers (status, metrics, team, handoff) |
| `project_cli_extra.py` | ~275 | Memory, gates, update-claudemd handlers |
| `project_parser.py` | ~278 | argparse tree (incl. claim/unclaim/team/metrics/gates) |
| `project_config.py` | ~125 | Config loader, service factory, gates config |
| `project_types.py` | ~129 | TypedDict types, constants |
| `gate_runner.py` | ~120 | Quality gate execution engine |
| `frai_utils.py` | ~49 | Slug validation (max 64 chars), timestamps |
| `frai_version.py` | ~3 | Version constant |
| `project.py` | ~90 | Entry point, dispatch |

## Cross-IDE Support

Skills in `agents/{ide}/skills/` (24 per IDE). Role profiles in `agents/{ide}/roles/` (5). Stack guides in `agents/{ide}/stacks/` (5). MCP servers in `agents/{ide}/mcp/`. Bootstrap copies to target project's `.claude/` or `.cursor/`.

```
agents/
├── claude/skills/    # 24 SKILL.md (with Phase 0 context loading)
├── claude/roles/     # 5 role profiles (developer, architect, qa, tech-writer, ui-ux)
├── claude/stacks/    # 5 stack guides (python, react, typescript, go, vue)
├── claude/mcp/
│   └── codebase-rag/ # code search + knowledge MCP
├── cursor/skills/    # 24 SKILL.md (copy of claude)
├── cursor/roles/     # 5 role profiles (copy of claude)
├── cursor/stacks/    # 5 stack guides (copy of claude)
└── cursor/mcp/       # same MCP servers
```

## Role-Stack Context System

Execution skills (task, review, test, debug, optimize, security) follow **Phase 0 — Load Context**:
1. Get active task → extract role and stack
2. Read `roles/{role}.md` → follow role-specific skill modifiers
3. Read `stacks/{stack}.md` → use stack-specific patterns, checklists, pitfalls
4. Load project memories and decisions for context

## RAG (Codebase Search)

FTS5-based code search. Files: `rag_detect.py` (50+ lang extensions, .gitignore), `rag_store.py` (FTS5 SQLite), `rag_indexer.py` (12-language chunking), `server.py` (MCP: search_code, search_knowledge, reindex, rag_status, archive_done).

## Testing

```bash
pytest tests/ -v                    # all tests
pytest tests/test_frai_backend.py   # backend
pytest tests/test_frai_service.py   # service
pytest tests/test_frai_cli.py       # CLI smoke
pytest tests/test_gates.py          # quality gates
pytest tests/test_rag.py            # RAG core
pytest tests/test_cascade_delete.py # CASCADE DELETE
pytest tests/test_fts5_sync.py      # FTS5 sync
pytest tests/test_stress.py         # stress/perf
pytest tests/test_e2e_workflow.py   # E2E workflow
pytest tests/test_rag_edge.py       # RAG edge cases
```

## Knowledge Tools

| Tool | When | Example |
|------|------|---------|
| `decide` | Architecture decisions, tech choices | `decide "SQLite not Postgres" --rationale "zero-dep"` |
| `memory add` | Code patterns, gotchas, conventions | `memory add gotcha "FTS5 quotes" "Sanitize quotes"` |
| `session handoff` | Every /end and /checkpoint | `session handoff '{"done":[...], "next":[...]}'` |
