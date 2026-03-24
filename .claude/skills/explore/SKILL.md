---
name: explore
description: "SENAR exploration — time-bounded investigation before committing to a task. Use when user says 'explore', 'investigate', 'research', 'spike', or when facing an unfamiliar domain."
---

# /explore — Time-Bounded Exploration (SENAR Section 5.1)

Investigation without full task formality. Always respond in the user's language.

**When to use:** Unfamiliar domain, multiple possible approaches, need to understand before planning.

**Key rule:** If exploration yields implementation work, a task SHALL be created before changes are committed.

## Argument Dispatch

### $ARGUMENTS = description of what to investigate

1. **Start exploration:**
   ```bash
   .frai/frai explore start "{description}" --time-limit 30
   ```
   Default time limit: 30 min. Use shorter for simple questions, longer for complex domains.

2. **Announce:**
   - What we're investigating
   - Time limit
   - What we hope to learn

3. **Investigate:**
   - Read code, documentation, external resources
   - Try small experiments (do NOT write production code)
   - Document findings as you go: `frai task log` is not available (no task), so keep notes in conversation

4. **Check time periodically:**
   ```bash
   .frai/frai explore current
   ```
   If over time limit — wrap up immediately.

5. **End exploration with findings:**
   ```bash
   .frai/frai explore end --summary "What we learned: ..."
   ```

   If the exploration revealed work to do:
   ```bash
   .frai/frai explore end --summary "Need to implement X" --create-task
   ```
   This auto-creates a task from the exploration.

6. **Document dead ends** from exploration:
   ```bash
   .frai/frai dead-end "Tried approach X" "Doesn't work because Y"
   ```
   Also check existing dead ends to avoid repeating: `.frai/frai memory list --type dead_end`

7. **Suggest next:** "Findings recorded. Create a task with `/plan` or continue exploring."

### $ARGUMENTS = "end"

End current exploration:
```bash
.frai/frai explore end --summary "Findings summary"
```

### $ARGUMENTS = "status" or empty

Check current exploration:
```bash
.frai/frai explore current
```

## Rules

- **Time-bounded.** Respect the time limit. When it's up, stop and summarize.
- **No production code.** Explorations are for learning, not implementing. Small experiments only.
- **If it yields work → create task.** Use `--create-task` or follow up with `/plan`.
- **Document everything.** Dead ends, findings, decisions — all captured.
- **Cheap to start, cheap to end.** Don't overthink the exploration scope.

## Gotchas

- **Only one active exploration** at a time. End the current one before starting another.
- **Explorations are not tasks** — no plan steps, no QG-0, no AC. Just investigate and report.
- **`--create-task` requires `--summary`** — you can't create a task without explaining what you found.
