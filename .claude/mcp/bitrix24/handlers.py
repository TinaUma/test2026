"""Bitrix24 Scrum MCP tool handlers."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from bitrix_client import (
    BitrixClient, get_client, STATUS_ID_TO_NAME, STATUS_NAME_TO_ID, COMPLEXITY_TO_SP,
)


def handle_tool(project_dir: str, name: str, args: dict) -> str:
    """Dispatch tool call to handler. Always returns text."""
    try:
        # Tools that don't need B24 connection
        if name == "b24_sync_status":
            return _handle_sync_status(project_dir)

        bx = get_client(project_dir)

        # Health
        if name == "b24_health":
            return _handle_health(bx)

        # Epics
        elif name == "b24_epic_list":
            return _handle_epic_list(bx)
        elif name == "b24_epic_add":
            return _handle_epic_add(bx, args)
        elif name == "b24_epic_update":
            return _handle_epic_update(bx, args)

        # Tasks
        elif name == "b24_task_list":
            return _handle_task_list(bx, args)
        elif name == "b24_task_add":
            return _handle_task_add(bx, args)
        elif name == "b24_task_get":
            return _handle_task_get(bx, args)
        elif name == "b24_task_update":
            return _handle_task_update(bx, args)
        elif name == "b24_task_complete":
            return _handle_task_complete(bx, args)

        # Sprints
        elif name == "b24_sprint_list":
            return _handle_sprint_list(bx)
        elif name == "b24_sprint_add":
            return _handle_sprint_add(bx, args)
        elif name == "b24_sprint_start":
            return _handle_sprint_start(bx, args)
        elif name == "b24_sprint_complete":
            return _handle_sprint_complete(bx, args)
        elif name == "b24_sprint_get":
            return _handle_sprint_get(bx, args)

        # Task move
        elif name == "b24_task_move_to_sprint":
            return _handle_task_move_to_sprint(bx, args)

        # Backlog
        elif name == "b24_backlog":
            return _handle_backlog(bx)

        # Sync
        elif name == "b24_sync_push":
            return _handle_sync_push(bx, project_dir)
        elif name == "b24_sync_push_task":
            return _handle_sync_push_task(bx, project_dir, args)
        elif name == "b24_sync_pull":
            return _handle_sync_pull(bx, project_dir)

        return f"Unknown tool: {name}"
    except Exception as e:
        return f"Error: {e}"


# --- Helpers ---

def _frai_db(project_dir: str) -> sqlite3.Connection:
    db_path = os.path.join(project_dir, ".frai", "frai.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_sync_table(db: sqlite3.Connection) -> None:
    db.execute("""
        CREATE TABLE IF NOT EXISTS bitrix_sync (
            entity_type TEXT NOT NULL,
            frai_slug TEXT NOT NULL,
            bitrix_id INTEGER NOT NULL,
            last_synced_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (entity_type, frai_slug)
        )
    """)
    db.commit()


def _get_b24_id(db: sqlite3.Connection, entity_type: str, slug: str) -> int | None:
    row = db.execute(
        "SELECT bitrix_id FROM bitrix_sync WHERE entity_type = ? AND frai_slug = ?",
        (entity_type, slug),
    ).fetchone()
    return row["bitrix_id"] if row else None


def _save_b24_id(db: sqlite3.Connection, entity_type: str, slug: str, b24_id: int) -> None:
    db.execute(
        "INSERT OR REPLACE INTO bitrix_sync (entity_type, frai_slug, bitrix_id, last_synced_at) "
        "VALUES (?, ?, ?, datetime('now'))",
        (entity_type, slug, b24_id),
    )
    db.commit()


# --- Health ---

def _handle_health(bx: BitrixClient) -> str:
    try:
        bx.health()
        epics = bx.epic_list()
        tasks = bx.task_list(limit=1)
        return f"Bitrix24 connected. Group: {bx.group_id}. Epics: {len(epics)}."
    except Exception as e:
        return f"Connection failed: {e}"


# --- Epics ---

def _handle_epic_list(bx: BitrixClient) -> str:
    epics = bx.epic_list()
    if not epics:
        return "No epics."
    lines = []
    for e in epics:
        lines.append(f"  #{e.get('id', '?')} {e.get('name', '?')}")
    return f"Epics ({len(epics)}):\n" + "\n".join(lines)


def _handle_epic_add(bx: BitrixClient, args: dict) -> str:
    epic_id = bx.epic_add(
        name=args["name"],
        description=args.get("description", ""),
        color=args.get("color", "#69dadb"),
    )
    return f"Epic #{epic_id} created: {args['name']}"


def _handle_epic_update(bx: BitrixClient, args: dict) -> str:
    fields = {}
    if "name" in args:
        fields["name"] = args["name"]
    if "description" in args:
        fields["description"] = args["description"]
    bx.epic_update(args["id"], **fields)
    return f"Epic #{args['id']} updated."


# --- Tasks ---

def _handle_task_list(bx: BitrixClient, args: dict) -> str:
    status = args.get("status", "all")
    limit = args.get("limit", 50)
    tasks = bx.task_list(status=status, limit=limit)
    if not tasks:
        return f"No tasks (filter: {status})."
    lines = []
    for t in tasks:
        st = STATUS_ID_TO_NAME.get(int(t.get("status", 0)), "?")
        tags = ", ".join(t.get("tags", {}).values()) if isinstance(t.get("tags"), dict) else ""
        line = f"  #{t['id']} [{st}] {t.get('title', '?')}"
        if tags:
            line += f" ({tags})"
        lines.append(line)
    return f"Tasks ({len(tasks)}, filter: {status}):\n" + "\n".join(lines)


def _handle_task_add(bx: BitrixClient, args: dict) -> str:
    task_id = bx.task_add(
        title=args["title"],
        description=args.get("description", ""),
        epic_id=args.get("epic_id", 0),
        story_points=args.get("story_points", 0),
        tags=args.get("tags"),
        responsible_id=args.get("responsible_id", 0),
    )
    return f"Task #{task_id} created: {args['title']}"


def _handle_task_get(bx: BitrixClient, args: dict) -> str:
    t = bx.task_get(args["task_id"])
    if not t:
        return f"Task #{args['task_id']} not found."
    st = STATUS_ID_TO_NAME.get(int(t.get("status", 0)), "?")
    lines = [
        f"Task #{t.get('id', '?')}",
        f"  Title: {t.get('title', '?')}",
        f"  Status: {st}",
        f"  Description: {(t.get('description') or '-')[:200]}",
    ]
    if t.get("tags"):
        lines.append(f"  Tags: {t['tags']}")
    return "\n".join(lines)


def _handle_task_update(bx: BitrixClient, args: dict) -> str:
    task_id = args.pop("task_id")
    bx.task_update(task_id, **args)
    return f"Task #{task_id} updated."


def _handle_task_complete(bx: BitrixClient, args: dict) -> str:
    bx.task_complete(args["task_id"])
    return f"Task #{args['task_id']} completed."


# --- Sprints ---

def _handle_sprint_list(bx: BitrixClient) -> str:
    sprints = bx.sprint_list()
    if not sprints:
        return "No sprints."
    lines = []
    for s in sprints:
        status = s.get("status", "?")
        lines.append(f"  #{s.get('id', '?')} [{status}] {s.get('name', '?')}")
    return f"Sprints ({len(sprints)}):\n" + "\n".join(lines)


def _handle_sprint_add(bx: BitrixClient, args: dict) -> str:
    sprint_id = bx.sprint_add(
        name=args["name"],
        date_start=args["date_start"],
        date_end=args["date_end"],
    )
    return f"Sprint #{sprint_id} created: {args['name']} ({args['date_start']} — {args['date_end']})"


def _handle_sprint_start(bx: BitrixClient, args: dict) -> str:
    bx.sprint_start(args["sprint_id"])
    return f"Sprint #{args['sprint_id']} started."


def _handle_sprint_complete(bx: BitrixClient, args: dict) -> str:
    bx.sprint_complete(args["sprint_id"])
    return f"Sprint #{args['sprint_id']} completed."


def _handle_task_move_to_sprint(bx: BitrixClient, args: dict) -> str:
    bx.task_move_to_sprint(args["task_id"], args["sprint_id"])
    return f"Task #{args['task_id']} moved to sprint #{args['sprint_id']}."


def _handle_sprint_get(bx: BitrixClient, args: dict) -> str:
    s = bx.sprint_get(args["sprint_id"])
    if not s:
        return f"Sprint #{args['sprint_id']} not found."
    return f"Sprint #{s.get('id')}: {s.get('name', '?')} [{s.get('status', '?')}]"


# --- Backlog ---

def _handle_backlog(bx: BitrixClient) -> str:
    bl = bx.backlog_get()
    if not bl:
        return "Backlog empty or not found."
    return f"Backlog ID: {bl.get('id', '?')}, Group: {bl.get('groupId', '?')}"


# --- Sync ---

def _handle_sync_push(bx: BitrixClient, project_dir: str) -> str:
    db = _frai_db(project_dir)
    _ensure_sync_table(db)
    lines = []

    # Epics
    epics = db.execute("SELECT * FROM epics").fetchall()
    for epic in epics:
        slug = epic["slug"]
        b24_id = _get_b24_id(db, "epic", slug)
        if b24_id:
            bx.epic_update(b24_id, name=epic["title"])
            lines.append(f"  Epic [{slug}] updated (B24 #{b24_id})")
        else:
            b24_id = bx.epic_add(epic["title"], epic.get("description", ""))
            if b24_id:
                _save_b24_id(db, "epic", slug, b24_id)
                lines.append(f"  Epic [{slug}] -> B24 #{b24_id}")

    # Tasks
    tasks = db.execute("SELECT * FROM tasks").fetchall()
    for task in tasks:
        slug = task["slug"]
        b24_id = _get_b24_id(db, "task", slug)
        epic_slug = task["epic_slug"] if "epic_slug" in task.keys() else ""
        b24_epic_id = _get_b24_id(db, "epic", epic_slug) if epic_slug else 0
        sp = COMPLEXITY_TO_SP.get(task.get("complexity", ""), 0)
        tags = [f"frai:{slug}"]

        if b24_id:
            status_name = {
                "planning": "new", "active": "in_progress",
                "blocked": "deferred", "done": "completed",
            }.get(task.get("status", ""), "new")
            bx.task_update(b24_id, status=status_name)
            lines.append(f"  Task [{slug}] status synced (B24 #{b24_id})")
        else:
            b24_id = bx.task_add(
                title=task["title"],
                description=task.get("goal", ""),
                epic_id=b24_epic_id or 0,
                story_points=sp,
                tags=tags,
            )
            if b24_id:
                _save_b24_id(db, "task", slug, b24_id)
                lines.append(f"  Task [{slug}] -> B24 #{b24_id}")

    if not lines:
        return "Nothing to sync (no epics or tasks in frai)."
    return f"Pushed {len(lines)} items:\n" + "\n".join(lines)


def _handle_sync_push_task(bx: BitrixClient, project_dir: str, args: dict) -> str:
    slug = args["slug"]
    db = _frai_db(project_dir)
    _ensure_sync_table(db)

    row = db.execute("SELECT * FROM tasks WHERE slug = ?", (slug,)).fetchone()
    if not row:
        return f"Task '{slug}' not found in frai."

    b24_id = _get_b24_id(db, "task", slug)
    if b24_id:
        status_name = {
            "planning": "new", "active": "in_progress",
            "blocked": "deferred", "done": "completed",
        }.get(row.get("status", ""), "new")
        bx.task_update(b24_id, status=status_name)
        return f"Task [{slug}] status synced (B24 #{b24_id})."

    epic_slug = row["epic_slug"] if "epic_slug" in row.keys() else ""
    b24_epic_id = _get_b24_id(db, "epic", epic_slug) if epic_slug else 0
    sp = COMPLEXITY_TO_SP.get(row.get("complexity", ""), 0)

    b24_id = bx.task_add(
        title=row["title"],
        description=row.get("goal", ""),
        epic_id=b24_epic_id or 0,
        story_points=sp,
        tags=[f"frai:{slug}"],
    )
    if b24_id:
        _save_b24_id(db, "task", slug, b24_id)
        return f"Task [{slug}] -> B24 #{b24_id}"
    return f"Failed to create task [{slug}] in B24."


def _handle_sync_pull(bx: BitrixClient, project_dir: str) -> str:
    db = _frai_db(project_dir)
    _ensure_sync_table(db)

    rows = db.execute("SELECT * FROM bitrix_sync WHERE entity_type = 'task'").fetchall()
    if not rows:
        return "No synced tasks."

    frai_status_map = {2: "planning", 3: "active", 5: "done", 6: "blocked"}
    changes = []

    for row in rows:
        slug = row["frai_slug"]
        try:
            b24_task = bx.task_get(row["bitrix_id"])
            b24_status = int(b24_task.get("status", 0))
            frai_status = frai_status_map.get(b24_status)

            frai_task = db.execute("SELECT status FROM tasks WHERE slug = ?", (slug,)).fetchone()
            if frai_task and frai_status and frai_task["status"] != frai_status:
                db.execute("UPDATE tasks SET status = ? WHERE slug = ?", (frai_status, slug))
                db.commit()
                changes.append(f"  [{slug}] {frai_task['status']} -> {frai_status}")
        except Exception as e:
            changes.append(f"  [{slug}] ERROR: {e}")

    if not changes:
        return f"Checked {len(rows)} tasks — no changes."
    return f"Pulled {len(changes)} updates:\n" + "\n".join(changes)


def _handle_sync_status(project_dir: str) -> str:
    db = _frai_db(project_dir)
    _ensure_sync_table(db)

    rows = db.execute(
        "SELECT * FROM bitrix_sync ORDER BY entity_type, frai_slug"
    ).fetchall()
    if not rows:
        return "No synced entities."

    lines = [f"{'Type':<8} {'Slug':<25} {'B24 ID':<10} {'Last Synced'}"]
    lines.append("-" * 65)
    for r in rows:
        lines.append(f"{r['entity_type']:<8} {r['frai_slug']:<25} {r['bitrix_id']:<10} {r['last_synced_at']}")
    return "\n".join(lines)
