# Claude Code Rules — Frai Framework

## Tool Constraints
- Always use dedicated tools (Read, Edit, Grep, Glob) over Bash equivalents
- Use AskUserQuestion for clarifications, not assumptions

## Frai Integration
- Skills are in `.claude/skills/` — invoked via `/skill-name`
- CLI: `.frai/frai <command>`
- Database: `.frai/frai.db` (SQLite, shared with Cursor if both installed)
## Workflow Discipline
- NEVER start coding without a task (`/task <slug>` or `task start <slug>`)
- Record architectural decisions with `decide` command
- Save useful patterns to project memory
