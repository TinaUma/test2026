---
name: plan
description: "Plan a new task with complexity scoring and stack detection. Args: [task-description]. Use when user says 'plan', 'create task', 'break down', 'estimate'."
---

# /plan — Task Planning (SENAR-aligned)

Plans a new feature with complexity scoring. Always respond in the user's language.

## Algorithm

### 1. Analyze scope

1. Which domains are affected? (frontend, backend, database, devops)
2. How many files/components?
3. Risk level?
4. **Is the domain well-known?** If unfamiliar — suggest `frai explore start "..."` first (SENAR Section 5.1).

**Complexity scoring:**
- 1-2 signals: **simple** (1 task)
- 3-5 signals: **medium** (2-3 tasks)
- 6+ signals: **complex** (decompose)

### 2. Check existing knowledge

```bash
.frai/frai memory search "relevant keywords"
```

Check for dead ends too — don't repeat failed approaches:
```bash
.frai/frai memory list --type dead_end
```

### 3. Detect stack

Determine from project structure (package.json, requirements.txt, go.mod). Check `stacks/` for valid names.

### 4. Create task

Epic/story are **optional**. For standalone tasks, use `task quick` or `task add` without `--group`:

```bash
# Quick (auto-slug):
.frai/frai task quick "Task title" --role developer --stack python --goal "What success looks like"

# Full (with explicit slug):
.frai/frai task add "Task title" --slug my-task --complexity medium --role developer --stack python --goal "What success looks like"

# With epic/story grouping (optional):
.frai/frai task add "Task title" --group my-story --slug my-task --complexity medium --role developer --stack python
```

If the work is part of a larger initiative, create or reuse an epic/story:
```bash
.frai/frai epic add <slug> "Epic title"
.frai/frai story add <epic-slug> <story-slug> "Story title"
```

### 5. Set acceptance criteria (SENAR QG-0 MANDATORY)

**CRITICAL: Without acceptance criteria, `task start` will be blocked by QG-0 Context Gate.**

Write clear, verifiable acceptance criteria. Each criterion must be independently testable.

```bash
.frai/frai task update <slug> --acceptance-criteria "1. POST /login returns JWT on valid creds. 2. Returns 401 on invalid password. 3. Returns 422 on missing email."
```

**AC quality rules (SENAR):**
- Each criterion independently testable
- At least one negative scenario (error case, boundary)
- No vague criteria ("works correctly", "handles edge cases")

### 6. Set plan steps

```bash
.frai/frai task plan <slug> "Step 1" "Step 2" "Step 3"
```

### 7. Present plan

Show: task slug, title, complexity, role, **goal**, plan steps, **acceptance criteria**.
Verify: "Goal and AC are set — QG-0 will pass."
Ask: "Proceed with `/task <slug>`?"

## Gotchas

- **Roles are free-text** — use any role name, not limited to a fixed set.
- **Slug format** must be `^[a-z0-9][a-z0-9-]*$`, max 64 chars.
- **Epic/story are optional** — tasks can exist without grouping.
- **QG-0 blocks without goal + AC** — always set both during planning.
- **Defect tasks** — use `--defect-of <parent-slug>` when creating a fix for a bug found in an existing task.
