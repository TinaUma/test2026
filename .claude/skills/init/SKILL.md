---
name: init
description: "First-time project setup. Creates .frai/frai.db and initializes project structure. Use when user says 'init', 'initialize', 'setup project'."
---

# /init — Project Initialization

First-time setup for a new Frai project. Always respond in the user's language.

## Algorithm

### 1. Determine project name

Use the argument if provided (`/init my-project`), otherwise derive from the current directory name. Validate slug format: `^[a-z0-9][a-z0-9-]*$`.

### 2. Initialize project

```bash
.frai/frai init --name <slug>
```

### 3. Verify

Check that the database was created:
```bash
ls -la .frai/frai.db
```

If the file exists — initialization succeeded.
If not — report the error from the init command.

### 4. Show getting-started help

Display to the user:

```
Project "<name>" initialized.

Getting started:
  /start              — Begin a session
  /plan <description> — Plan your first task
  /task <slug>        — Work on a task
  /end                — End session and save context

Project data: .frai/frai.db
```

## Gotchas

- **Running `/init` twice is safe** — it won't overwrite an existing DB, but will report that the project is already initialized.
- **Slug validation** is strict: `^[a-z0-9][a-z0-9-]*$`. Directory names with dots or underscores need a manual slug override.
