---
name: diff
description: "Analyze git diff — summarize changes, highlight risks. Use when user says 'diff', 'show changes', 'what changed', 'what did I change'."
---

# /diff — Diff Analysis

Analyze code changes, summarize modifications, highlight risks. Always respond in the user's language.

## Algorithm

### 1. Gather Changes
```bash
# Unstaged changes
git diff --stat
git diff

# Staged changes
git diff --cached --stat
git diff --cached

# Recent commits (if no uncommitted changes)
git log --oneline -5
git diff HEAD~1
```

### 2. Determine Scope
- `$ARGUMENTS` = empty → show all uncommitted changes (staged + unstaged)
- `$ARGUMENTS` = "staged" → staged only
- `$ARGUMENTS` = "HEAD~N" or commit hash → diff against that ref
- `$ARGUMENTS` = branch name → diff against that branch
- `$ARGUMENTS` = file path → changes to that file only

### 3. Analyze Each Changed File
For every modified file, identify:
- What was added / removed / changed
- The intent behind the change (feature, fix, refactor)
- Potential risks or side effects

### 4. Highlight Risks
Flag any changes that:
- Touch security-sensitive code (auth, crypto, permissions)
- Modify public APIs or interfaces
- Remove error handling or validation
- Change database schemas or migrations
- Affect configuration or environment variables
- Could break existing tests

## Output Format

```
## Changes Summary

Files changed: {N} (+{additions} -{deletions})

### Modified Files
| File | Changes | Risk |
|------|---------|------|
| {path} | {summary} | {low/medium/high} |

### Key Changes
1. {description of logical change group}
2. ...

### Risks
- {risk description + affected file}

### Recommendation
{ready to commit / needs review / needs tests}
```

## Rules
- Show the BIG PICTURE first, then details
- Group related changes together (don't list file-by-file mechanically)
- Always flag security-sensitive changes regardless of scope
- If no changes found, say so clearly
- **Suggest next:** based on assessment — `/review` if risky, `/commit` if clean, `/test` if untested

## Gotchas

- **Binary files in diff** show as "Binary files differ" — don't try to analyze their content, just flag them.
- **Renamed files** may show as delete+add if similarity is below git's threshold. Use `git diff --find-renames` for accurate rename detection.
