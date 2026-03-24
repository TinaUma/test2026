"""Jira MCP tool handlers."""

from __future__ import annotations

import json
import os
import sqlite3

from jira_client import JiraClient, get_client


def handle_tool(project_dir: str, name: str, args: dict) -> str:
    """Dispatch tool call to handler. Always returns text."""
    try:
        # Tools that don't need Jira connection
        if name == "jira_sync_status":
            return _handle_sync_status(project_dir)

        jira = get_client(project_dir)

        # Health
        if name == "jira_health":
            return _handle_health(jira)

        # Issues
        elif name == "jira_search":
            return _handle_search(jira, args)
        elif name == "jira_get_issue":
            return _handle_get_issue(jira, args)
        elif name == "jira_create_issue":
            return _handle_create_issue(jira, args)
        elif name == "jira_update_issue":
            return _handle_update_issue(jira, args)
        elif name == "jira_transition_issue":
            return _handle_transition_issue(jira, args)
        elif name == "jira_get_transitions":
            return _handle_get_transitions(jira, args)
        elif name == "jira_add_comment":
            return _handle_add_comment(jira, args)
        elif name == "jira_add_worklog":
            return _handle_add_worklog(jira, args)

        # Sync
        elif name == "jira_sync_push":
            return _handle_sync_push(jira, project_dir, args)
        elif name == "jira_sync_push_task":
            return _handle_sync_push_task(jira, project_dir, args)
        elif name == "jira_sync_pull":
            return _handle_sync_pull(jira, project_dir)

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
        CREATE TABLE IF NOT EXISTS jira_sync (
            frai_slug TEXT PRIMARY KEY,
            jira_key TEXT NOT NULL,
            last_synced_at TEXT DEFAULT (datetime('now'))
        )
    """)
    db.commit()


def _get_jira_key(db: sqlite3.Connection, slug: str) -> str | None:
    row = db.execute(
        "SELECT jira_key FROM jira_sync WHERE frai_slug = ?", (slug,)
    ).fetchone()
    return row["jira_key"] if row else None


def _save_jira_key(db: sqlite3.Connection, slug: str, jira_key: str) -> None:
    db.execute(
        "INSERT OR REPLACE INTO jira_sync (frai_slug, jira_key, last_synced_at) "
        "VALUES (?, ?, datetime('now'))",
        (slug, jira_key),
    )
    db.commit()


def _format_issue(issue: dict, brief: bool = False) -> str:
    fields = issue.get("fields", {})
    key = issue.get("key", "?")
    summary = fields.get("summary", "?")
    status = fields.get("status", {}).get("name", "?")
    priority = fields.get("priority", {}).get("name", "?") if fields.get("priority") else "-"
    assignee = fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned"

    if brief:
        return f"{key} [{status}] {summary} | {assignee} | {priority}"

    lines = [
        f"Issue: {key}",
        f"  Summary: {summary}",
        f"  Status: {status}",
        f"  Priority: {priority}",
        f"  Assignee: {assignee}",
    ]

    # Type
    issue_type = fields.get("issuetype", {}).get("name", "?")
    lines.append(f"  Type: {issue_type}")

    # Components
    components = [c.get("name", "") for c in fields.get("components", [])]
    if components:
        lines.append(f"  Components: {', '.join(components)}")

    # Time tracking
    tt = fields.get("timetracking", {})
    if tt:
        orig = tt.get("originalEstimate", "-")
        spent = tt.get("timeSpent", "-")
        remaining = tt.get("remainingEstimate", "-")
        lines.append(f"  Time: estimate={orig}, spent={spent}, remaining={remaining}")

    # Description (truncated)
    desc = fields.get("description", "")
    if desc:
        lines.append(f"  Description: {desc[:300]}{'...' if len(desc) > 300 else ''}")

    return "\n".join(lines)


# --- Health ---

def _handle_health(jira: JiraClient) -> str:
    return jira.health()


# --- Issues ---

def _handle_search(jira: JiraClient, args: dict) -> str:
    result = jira.search(
        jql=args["jql"],
        max_results=args.get("max_results", 50),
    )
    issues = result.get("issues", [])
    total = result.get("total", 0)
    if not issues:
        return f"No issues found. (JQL: {args['jql']})"
    lines = [_format_issue(i, brief=True) for i in issues]
    header = f"Found {total} issues (showing {len(issues)}):\n"
    return header + "\n".join(lines)


def _handle_get_issue(jira: JiraClient, args: dict) -> str:
    issue = jira.get_issue(args["issue_key"])
    return _format_issue(issue)


def _handle_create_issue(jira: JiraClient, args: dict) -> str:
    fields: dict = {
        "project": {"key": args["project_key"]},
        "summary": args["summary"],
        "issuetype": {"name": args["issue_type"]},
    }
    if args.get("description"):
        fields["description"] = args["description"]
    if args.get("priority"):
        fields["priority"] = {"name": args["priority"]}
    if args.get("components"):
        fields["components"] = [{"name": c} for c in args["components"]]
    if args.get("labels"):
        fields["labels"] = args["labels"]
    if args.get("estimate"):
        fields["timetracking"] = {"originalEstimate": args["estimate"]}
    if args.get("epic_link"):
        fields["customfield_10107"] = args["epic_link"]
    if args.get("epic_name"):
        fields["customfield_10104"] = args["epic_name"]
    if args.get("fix_version"):
        fields["fixVersions"] = [{"name": args["fix_version"]}]
    if args.get("additional_fields"):
        extra = args["additional_fields"]
        if isinstance(extra, str):
            extra = json.loads(extra)
        fields.update(extra)

    result = jira.create_issue(fields)
    key = result.get("key", "?")
    return f"Issue {key} created: {args['summary']}"


def _handle_update_issue(jira: JiraClient, args: dict) -> str:
    issue_key = args["issue_key"]
    fields: dict = {}
    if args.get("summary"):
        fields["summary"] = args["summary"]
    if args.get("description"):
        fields["description"] = args["description"]
    if args.get("priority"):
        fields["priority"] = {"name": args["priority"]}
    if args.get("labels"):
        fields["labels"] = args["labels"]
    if args.get("additional_fields"):
        extra = args["additional_fields"]
        if isinstance(extra, str):
            extra = json.loads(extra)
        fields.update(extra)
    if not fields:
        return "No fields to update."
    jira.update_issue(issue_key, fields)
    return f"Issue {issue_key} updated."


def _handle_transition_issue(jira: JiraClient, args: dict) -> str:
    jira.transition_issue(args["issue_key"], args["transition_id"])
    return f"Issue {args['issue_key']} transitioned (id={args['transition_id']})."


def _handle_get_transitions(jira: JiraClient, args: dict) -> str:
    transitions = jira.get_transitions(args["issue_key"])
    if not transitions:
        return f"No transitions available for {args['issue_key']}."
    lines = [f"  {t['id']}: {t['name']}" for t in transitions]
    return f"Available transitions for {args['issue_key']}:\n" + "\n".join(lines)


def _handle_add_comment(jira: JiraClient, args: dict) -> str:
    jira.add_comment(args["issue_key"], args["body"])
    return f"Comment added to {args['issue_key']}."


def _handle_add_worklog(jira: JiraClient, args: dict) -> str:
    jira.add_worklog(args["issue_key"], args["time_spent"], args.get("comment", ""))
    return f"Worklog added to {args['issue_key']}: {args['time_spent']}"


# --- Sync ---

FRAI_TO_JIRA_STATUS = {
    "planning": "To Do",
    "active": "In Progress",
    "blocked": "In Progress",
    "review": "In Progress",
    "done": "Done",
}


def _handle_sync_push(jira: JiraClient, project_dir: str, args: dict) -> str:
    project_key = args["project_key"]
    issue_type = args.get("issue_type", "Задача")
    db = _frai_db(project_dir)
    _ensure_sync_table(db)
    lines = []

    tasks = db.execute("SELECT * FROM tasks").fetchall()
    for task in tasks:
        slug = task["slug"]
        jira_key = _get_jira_key(db, slug)

        if jira_key:
            lines.append(f"  [{slug}] already synced -> {jira_key}")
        else:
            result = jira.create_issue({
                "project": {"key": project_key},
                "summary": task["title"],
                "issuetype": {"name": issue_type},
                "description": task.get("goal", "") or "",
            })
            new_key = result.get("key", "?")
            _save_jira_key(db, slug, new_key)
            lines.append(f"  [{slug}] -> {new_key}")

    if not lines:
        return "No tasks to sync."
    return f"Pushed {len(lines)} tasks:\n" + "\n".join(lines)


def _handle_sync_push_task(jira: JiraClient, project_dir: str, args: dict) -> str:
    slug = args["slug"]
    project_key = args["project_key"]
    issue_type = args.get("issue_type", "Задача")

    db = _frai_db(project_dir)
    _ensure_sync_table(db)

    row = db.execute("SELECT * FROM tasks WHERE slug = ?", (slug,)).fetchone()
    if not row:
        return f"Task '{slug}' not found in frai."

    jira_key = _get_jira_key(db, slug)
    if jira_key:
        return f"Task [{slug}] already synced -> {jira_key}"

    result = jira.create_issue({
        "project": {"key": project_key},
        "summary": row["title"],
        "issuetype": {"name": issue_type},
        "description": row.get("goal", "") or "",
    })
    new_key = result.get("key", "?")
    _save_jira_key(db, slug, new_key)
    return f"Task [{slug}] -> {new_key}"


def _handle_sync_pull(jira: JiraClient, project_dir: str) -> str:
    db = _frai_db(project_dir)
    _ensure_sync_table(db)

    rows = db.execute("SELECT * FROM jira_sync").fetchall()
    if not rows:
        return "No synced tasks."

    # Map Jira status categories to frai statuses
    jira_cat_to_frai = {
        "new": "planning",
        "indeterminate": "active",
        "done": "done",
    }

    changes = []
    for row in rows:
        slug = row["frai_slug"]
        try:
            issue = jira.get_issue(row["jira_key"])
            jira_status_cat = issue.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key", "")
            frai_status = jira_cat_to_frai.get(jira_status_cat)

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
        "SELECT * FROM jira_sync ORDER BY frai_slug"
    ).fetchall()
    if not rows:
        return "No synced entities."

    lines = [f"{'Slug':<25} {'Jira Key':<15} {'Last Synced'}"]
    lines.append("-" * 55)
    for r in rows:
        lines.append(f"{r['frai_slug']:<25} {r['jira_key']:<15} {r['last_synced_at']}")
    return "\n".join(lines)
