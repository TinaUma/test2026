---
name: commit
description: "Create a standardized git commit. Use when user says 'commit', 'save changes', 'git commit'."
---

# /commit — Git Commit

Create well-structured commits with conventional commit messages. Always respond in the user's language.

## Conventional Commit Format
```
<type>(<scope>): <description>

<body>

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Algorithm

### 1. Analyze Changes
```bash
git status
git diff --stat
git diff --cached --stat
git log --oneline -5
```

### 2. Determine What to Stage
- If changes already staged — use those
- If nothing staged — identify related unstaged changes
- **NEVER stage** `.env`, credentials, secrets, large binaries
- **Prefer specific files** over `git add -A`
- Ask user if ambiguous

### 3. Generate Commit Message
From the diff, determine:
- **type**: feat/fix/refactor/etc.
- **scope**: primary affected module
- **description**: concise imperative summary (max 72 chars)
- **body**: 1-3 sentences explaining WHY, not WHAT

### 4. Run Quality Gates
```bash
python scripts/gate_runner.py commit --files {staged_files}
```
- `{staged_files}` = files being committed (from `git diff --cached --name-only`)
- If a **blocking** gate fails (ruff, mypy) → show output, do NOT commit. Fix issues first.
- If only **warnings** (filesize) → show them, proceed to confirm.

### 5. Present and Confirm
Show proposed message + file list + gate results. Ask user to confirm.

### 6. Commit
```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 7. Verify
```bash
git log --oneline -1
git status
```

## SENAR Checks Before Commit

Before committing, verify:
1. **Active task exists** — no commits without a task (SENAR Rule 9.1). Check: `.frai/frai task list --status active`
2. **Scope check** — do the staged files match the active task's goal? Flag any files outside task scope.
3. **AC coverage** — if task has acceptance criteria, are they addressed by this commit?
4. **Dead ends documented** — if any approach was abandoned during this task, was it recorded? `.frai/frai memory list --type dead_end`

## Rules
- **ALWAYS ask before committing** — never auto-commit
- **NEVER push** unless explicitly asked
- **NEVER use --no-verify** or skip hooks
- **NEVER amend** unless user explicitly requests it
- If pre-commit hook fails: fix, re-stage, create NEW commit
- Keep description under 72 characters
- Use imperative mood: "add feature" not "added feature"
- **Suggest next:** "More tasks? `/task list` or `/end` to wrap up."

## Gotchas

- **Pre-commit hook failure does NOT create the commit** — after fixing, create a NEW commit, never `--amend` (amend would modify the previous, unrelated commit).
- **HEREDOC for commit messages** — always use `$(cat <<'EOF' ... EOF)` to avoid shell escaping issues with quotes and special characters in the body.
- **Never `git add -A`** in projects with `.env`, credentials, or large binaries — always stage specific files.
