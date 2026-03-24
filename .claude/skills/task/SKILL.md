---
name: task
description: "Work on task from project DB. Tracks progress via plan steps. Args: [task-slug|done|list|step N]. Use when user says 'task', 'work on', 'take task', 'task done'."
---

# /task — Task Execution (SENAR-aligned)

Work on tasks from project DB. Always respond in the user's language.

**STRICT: Never start coding without running `task start` first.**

## Argument Dispatch

### $ARGUMENTS = task slug

1. **Activate task (QG-0 enforced — NO --force):**
   ```bash
   .frai/frai task start {slug}
   ```
   If QG-0 fails (missing goal or acceptance criteria):
   - Set them: `.frai/frai task update {slug} --goal "..." --acceptance-criteria "..."`
   - Then retry `.frai/frai task start {slug}`

2. **Load task context:**
   ```bash
   .frai/frai task show {slug}
   ```
   Extract: goal, acceptance criteria, plan steps, role, complexity, stack.

3. **Load role & stack context:**
   - Read `roles/{role}.md` to understand focus and priorities for this role
   - Read `stacks/{stack}.md` if stack is set — follow stack-specific conventions
   - Load relevant project knowledge:
     ```bash
     .frai/frai memory search "{task title keywords}"
     .frai/frai decisions --limit 5
     ```
   - **Check dead ends** — don't repeat failed approaches:
     ```bash
     .frai/frai memory list --type dead_end
     ```

4. **Adopt role** from task — follow the role profile's skill modifiers for /task.

5. **Announce:** Display to user:
   - Role and task title
   - Goal
   - Plan steps as checkboxes
   - Acceptance criteria (numbered)
   - Stack context + role focus

6. **Begin working** through the plan steps sequentially.
   - After each step: `.frai/frai task log {slug} "Step N done: description"` + `.frai/frai task step {slug} N`
   - **On failure/dead end:** Document it immediately:
     ```bash
     .frai/frai dead-end "What was tried" "Why it failed" --task {slug}
     ```
     Then try an alternative approach.

### $ARGUMENTS = "done"

1. **Find active task:**
   ```bash
   .frai/frai task list --status active
   ```

2. **Verify plan completion:** Check that all plan steps are marked done. If incomplete steps remain, warn the user and ask whether to skip or complete them.

3. **Walk acceptance criteria (QG-2 MANDATORY):**
   Get the task's acceptance criteria:
   ```bash
   .frai/frai task show {slug}
   ```
   For EACH acceptance criterion:
   - State the criterion
   - Verify it is met (run test, check code, demonstrate)
   - Mark as verified or explain why not

   **All criteria must be verified before proceeding.** If any criterion fails, do NOT mark done — fix first.

4. **Log AC verification evidence (REQUIRED by QG-2):**
   ```bash
   .frai/frai task log {slug} "AC verified: 1. POST /login returns 200 ✓ 2. Invalid creds return 401 ✓ 3. ..."
   ```
   **QG-2 will reject `task done` if no "AC verified" entry exists in task notes.** This is not optional.

5. **Run quality gates:**
   ```bash
   python scripts/gate_runner.py task-done --files {changed_files}
   ```
   - If a **blocking** gate fails → show output, do NOT mark task done. Tell user what to fix.
   - If only **warnings** → show them, proceed.
   - Log gate results: `.frai/frai task log {slug} "Gates: {summary}"`

6. **Mark done (with AC verified):**
   ```bash
   .frai/frai task done {slug} --ac-verified
   ```
   This will succeed only if AC verification evidence was logged in step 4. There is no other way to complete a task with AC.

6. **Announce:** Confirm task completion, show what was accomplished.

7. **Suggest next:** "Run `/review` to review changes, `/test` to verify, or `/commit` to save."

### $ARGUMENTS = "list"

Show all tasks:
```bash
.frai/frai task list
```

Display as a formatted table with slug, title, status, and complexity.

### $ARGUMENTS = "step N"

Mark plan step N as done on the current active task:
```bash
.frai/frai task step {slug} N
```

Find the active task slug first if not obvious from context:
```bash
.frai/frai task list --status active
```

Log progress: `.frai/frai task log {slug} "Step N completed: description"`

### $ARGUMENTS = empty (no args)

Show current active task status:
```bash
.frai/frai task list --status active
```

If one active task — show its details with `task show {slug}`.
If none — suggest picking one from planning tasks.

## Gotchas

- **QG-0: task start requires goal + AC** — if missing, set them with `task update`. No shortcuts.
- **QG-2: task done requires evidence + --ac-verified** — log AC verification, then close. No shortcuts.
- **Document dead ends** — when an approach fails, immediately call `.frai/frai dead-end`.
- **Only one active task at a time** per agent. `task start` on a second task will fail unless the first is done/blocked.
- **`task step` is 1-indexed**, not 0-indexed. Step numbers must match the plan.
- **`task done` is gated by plan steps** — all steps must be marked done.
- **Always `task log` before `task step`** — log provides context, step just marks completion.
