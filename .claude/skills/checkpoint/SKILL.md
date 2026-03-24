---
name: checkpoint
description: "Save context snapshot without ending session. Updates CLAUDE.md and records handoff. Use when user says 'checkpoint', 'save progress', 'save context', or proactively after significant work."
---

# /checkpoint — Context Snapshot (SENAR-aligned)

Quick context save without ending the session. Always respond in the user's language.

**When to use:** After completing a task or step, before large operations, every 30-50 tool calls.

**vs /end:** No session end, no commit prompt. ~4 tool calls vs ~8.

## Algorithm

### 1. Gather state + check session duration

Run in parallel:
```bash
git branch --show-current
.frai/frai session current
.frai/frai task list --status active
.frai/frai status
```

**SENAR Rule 9.2:** If `status` shows a session duration warning — tell the user prominently:
> "Session has been running for X min (limit: Y min). Consider wrapping up with /end."

### 2. Save handoff

Build handoff JSON from current conversation context:
```bash
.frai/frai session handoff '{"completed":["..."],"in_progress":["..."],"key_files":["..."],"dead_ends":["..."],"next_steps":["..."],"warnings":["..."]}'
```

### 3. Update CLAUDE.md

Run `.frai/frai update-claudemd` to refresh the dynamic section.

### 4. Confirm

Tell the user: "Checkpoint saved. Context preserved for session continuity."
If session duration warning was shown, reiterate it.

**That's it.** No session close, no commit prompt, no memory saves. Keep it fast.

## Gotchas

- **Handoff JSON must be valid JSON** — unescaped quotes in values will break the command.
- **Checkpoint does NOT commit** — code changes are only in working tree.
- **Session duration** — if over limit, warn at every checkpoint. This is the agent's obligation (SENAR Rule 9.2).
