# CLAUDE.md

This file provides guidance to Claude Code when working with this project.

## Project: my-project

Stack: not detected
Framework: Frai (FRamework AI)

## Frai Commands

```bash
.frai/frai status                  # project overview
.frai/frai session start           # start session
.frai/frai task list               # list tasks
.frai/frai task start <slug>       # claim + activate task
.frai/frai task done <slug>        # complete task
```

Full CLI ref: `.claude/references/project-cli.md`

## Workflow
- NEVER start coding without a task. Use `task start` first.
- ALWAYS use `.frai/frai` to run CLI commands (ensures correct venv Python).
- Always respond in the user's language.

## External Skills
External skills are managed via `skills.json` and auto-synced during bootstrap.
See `.claude/references/skill-catalog.md` for the full catalog with trigger keywords.
**When a user's request matches a trigger keyword for a not-installed skill, proactively suggest installing it.**

<!-- DYNAMIC:START -->
<!-- DYNAMIC:END -->
