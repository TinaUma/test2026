---
name: end
description: "End development session. Records summary, decisions, and handoff to DB. Updates CLAUDE.md. Use when user says 'end session', 'finish', 'wrap up', 'done for today'."
---

# /end — Session End (SENAR-aligned)

Archives session, updates CLAUDE.md for next session. Always respond in the user's language.

## Algorithm

### 1. SENAR Metrics Dashboard

Show session metrics before closing:
```bash
.frai/frai metrics
```

Display prominently:
- **Throughput**: tasks/session (is it improving?)
- **FPSR**: first-pass success rate (target: >85%)
- **DER**: defect escape rate (target: <5%)
- **Knowledge Capture Rate**: entries/task

### 2. Summarize session

Review what was accomplished. Check current session state:
```bash
.frai/frai session current
.frai/frai task list --status active
```

Auto-generate a 1-line summary from completed tasks, or ask the user.

### 3. Save handoff

**Critical for context preservation.** Build a handoff JSON with:
- `completed`: tasks finished this session
- `in_progress`: tasks still active (with current state)
- `key_files`: top 5-7 files modified this session
- `dead_ends`: approaches that failed (so next session doesn't repeat them)
- `next_steps`: what to do next
- `warnings`: anything the next session should know

```bash
.frai/frai session handoff '{"completed":["..."],"in_progress":["..."],"key_files":["..."],"dead_ends":["..."],"next_steps":["..."],"warnings":["..."]}'
```

**Note:** Handoff MUST be saved while session is still active.

### 4. Record decisions

If any architectural or design decisions were made during the session:
```bash
.frai/frai decide "decision description" --task SLUG
```

### 5. Save patterns and dead ends to memory

If any reusable patterns, gotchas, or dead ends were discovered:
```bash
.frai/frai memory add <type> "<title>" "<content>" [--tags tag1 tag2] [--task SLUG]
# type: pattern | gotcha | convention | context | dead_end
```

**SENAR Rule 9.4:** If any approach failed during this session and was NOT already documented, document it now:
```bash
.frai/frai dead-end "approach description" "reason it failed" --task SLUG
```

Only save project-specific patterns — not framework instructions.

### 6. End session

```bash
.frai/frai session end --summary "One-line summary of what was done"
```

### 7. Update CLAUDE.md

Run `.frai/frai update-claudemd` to refresh the dynamic section.

### 8. Git commit prompt

Ask the user: "Commit changes? (y/n)"
- If yes — stage relevant files, create commit with descriptive message
- If no — done
- Never force-push or commit without explicit approval

## Gotchas

- **Handoff MUST be saved before `session end`** — once the session is ended, you can't write a handoff to it.
- **Decisions should be recorded before ending** — they're linked to the session.
- **Dead ends must be documented** (SENAR Rule 9.4) — check if any failed approaches weren't recorded.
- **Don't save framework instructions to memory** — only project-specific patterns.
