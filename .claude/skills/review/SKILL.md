---
name: review
description: "Code review — finds bugs, vulnerabilities, antipatterns. Use when user says 'review', 'code review', 'find bugs', 'check my code', 'PR review'. Args: [file|directory|diff]"
---

# /review — Code Review (SENAR-aligned)

Zero-tolerance review. Find every bug, vulnerability, antipattern, and performance issue. Always respond in the user's language.

## Mindset

You are a hostile reviewer. Assume the code is broken until proven otherwise.
- Every line is suspect
- "It works" is not a defense

## Phase 0 — Load Context

Before reviewing, load role and project context:

1. **Check active task** (if any):
   ```bash
   .frai/frai task list --status active
   ```
   If active → `.frai/frai task show {slug}` → extract role, stack, **acceptance criteria**.

2. **Load role profile**: Read `roles/{role}.md` — follow the role's /review modifiers.

3. **Load stack guide**: Read `stacks/{stack}.md` — use the stack's review checklist.

4. **Load project conventions and dead ends**:
   ```bash
   .frai/frai memory search "convention"
   .frai/frai memory search "gotcha"
   .frai/frai memory list --type dead_end
   ```

## Algorithm

### 1. Determine Scope
- `$ARGUMENTS` = file path — review that file
- `$ARGUMENTS` = directory — review all source files in it
- `$ARGUMENTS` = "diff" or empty — `git diff HEAD~1` (last commit)
- `$ARGUMENTS` = "staged" — `git diff --cached`

### 2. Read Code
Read every file in scope. Do NOT skim. Check `CLAUDE.md` for project rules.

### 3. Find Issues (by severity)

**CRITICAL — Will break in production:**
- Null/undefined access, race conditions, deadlocks
- SQL injection, XSS, command injection
- Unhandled exceptions, resource leaks
- Auth/authz bypasses, data loss scenarios

**HIGH — Will cause problems:**
- Missing input validation, error swallowing
- N+1 queries, hardcoded secrets
- Incorrect error propagation, type coercion bugs

**MEDIUM — Code smell / tech debt:**
- God functions (>50 lines), copy-paste duplication
- Magic numbers, mixed abstraction levels
- Mutable shared state

**LOW — Style / convention:**
- Misleading names, dead code, commented-out code
- Console.log/print in production, TODO without reference

**Apply stack-specific review checklist** from the stack guide (if loaded).

### 4. SENAR Compliance Checks

In addition to standard code review, verify:

- **Scope creep**: Does the change touch files/modules outside the task's stated goal and AC? Flag any unrequested modifications.
- **Dead end awareness**: Does the code repeat an approach documented as a dead end? Check `memory list --type dead_end`.
- **AC coverage**: If an active task has acceptance criteria, does the implementation actually satisfy ALL of them?
- **Knowledge gaps**: Any non-obvious decisions that should be documented as `decide` or `memory add`?

### 5. Verify Each Issue
- Show exact file:line and problematic code
- Explain WHY it's a problem (concrete failure scenario)
- Provide a concrete fix (code, not description)

### 6. Run Quality Gates
```bash
python scripts/gate_runner.py review --files {files_in_scope}
```
- Gate results are appended to the review output
- Log results if task is active: `.frai/frai task log {slug} "Gates: {summary}"`

## Output Format

```
## Review: {scope}

Role: {role} | Stack: {stack}
Verdict: {FAIL|PASS WITH ISSUES|PASS}
Issues: {N} (Critical: {C}, High: {H}, Medium: {M}, Low: {L})

### Critical

**[C1] {Title}** — `{file}:{line}`
{problematic code}
Problem: {why this breaks}
Fix: {fixed code}

### High / Medium / Low ...

### SENAR Checks
- Scope creep: {clean / flagged items}
- Dead end violations: {none / repeated dead ends}
- AC coverage: {all met / gaps found}

### Summary
{1-2 sentences: overall assessment}
{Top 3 things to fix before merge}
```

**Suggest next:** "Fix issues and run `/test` to verify, then `/commit`."

## Separate Context Review

**Key principle:** The implementer and reviewer should be different instances.

### When to use subagent review

- **Always** when reviewing code you just wrote in this session
- When `$ARGUMENTS` contains "separate" or "independent"
- When the diff touches >3 files

### How it works

Launch a review subagent via the Agent tool with ONLY the diff and project context.
The dispatcher merges subagent findings into the standard review output format.

## Adversarial Mode

When `$ARGUMENTS` contains "adversarial" or "deep", activate adversarial review:

1. **First pass** — standard review via Separate Context Review
2. **Launch critic subagent** — find what the first reviewer MISSED
3. **Merge findings** — deduplicate, re-prioritize
4. **Stop condition** — if the critic finds only LOW severity, stop.

### When to activate automatically

- When reviewing security-sensitive code (auth, payments, crypto)
- When the diff touches >5 files across multiple modules

## Rules

- NEVER say "looks good" or "nice work"
- NEVER skip a section because "it's probably fine"
- If 0 issues found: "No issues found — request a second review."
- Prioritize: security > correctness > performance > style
- Log review result if task is active: `.frai/frai task log {slug} "Review: {verdict}, {N} issues"`
- **Document dead ends**: if the review reveals a pattern that doesn't work, add it: `.frai/frai dead-end "approach" "reason"`
- **Defect tracking**: if bugs are found in completed tasks, create fix tasks with `--defect-of`: `.frai/frai task add "Fix: description" --defect-of parent-slug --role developer`

## Gotchas

- **`git diff HEAD~1` shows nothing if nothing is committed** — check `git status` first.
- **Large diffs (>500 lines)** degrade review quality. Split into focused reviews.
- **Review your own generated code** — don't skip review just because you wrote it.
