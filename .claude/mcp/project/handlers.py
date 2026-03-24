"""Frai MCP handlers — dispatch tool calls to ProjectService."""

from __future__ import annotations

import json
from typing import Any


def handle_tool(svc: Any, name: str, args: dict) -> str:
    """Dispatch tool call to service method. Returns text result."""
    # === Health ===
    if name == "frai_health":
        return _handle_health(svc)

    # === Core ===
    elif name == "frai_status":
        return _handle_status(svc)
    elif name == "frai_task_list":
        return _handle_task_list(svc, args)
    elif name == "frai_task_show":
        return _handle_task_show(svc, args)
    elif name == "frai_task_add":
        return svc.task_add(
            args.get("story_slug"), args["slug"], args["title"],
            stack=args.get("stack"), complexity=args.get("complexity"),
            goal=args.get("goal"), role=args.get("role"),
        )
    elif name == "frai_task_quick":
        return svc.task_quick(args["title"], args.get("goal"), args.get("role"), args.get("stack"))
    elif name == "frai_task_next":
        task = svc.task_next(args.get("agent_id"))
        if task:
            action = "claimed and started" if args.get("agent_id") else "suggested"
            return f"Next task ({action}): {task['slug']} — {task['title']}"
        return "No available tasks."
    elif name == "frai_task_start":
        return svc.task_start(args["slug"])
    elif name == "frai_task_done":
        return svc.task_done(args["slug"], args.get("force", False), args.get("relevant_files"),
                             ac_verified=args.get("ac_verified", False))
    elif name == "frai_task_block":
        return svc.task_block(args["slug"], args.get("reason"))
    elif name == "frai_task_unblock":
        return svc.task_unblock(args["slug"])
    elif name == "frai_task_update":
        fields = {k: v for k, v in args.items() if k != "slug"}
        return svc.task_update(args["slug"], **fields) if fields else "No fields to update."
    elif name == "frai_task_plan":
        return svc.task_plan(args["slug"], args["steps"])
    elif name == "frai_task_step":
        return svc.task_step(args["slug"], args["step_num"])
    elif name == "frai_task_delete":
        return svc.task_delete(args["slug"])
    elif name == "frai_task_review":
        return svc.task_review(args["slug"])
    elif name == "frai_task_move":
        return svc.task_move(args["slug"], args["new_story_slug"])
    elif name == "frai_task_log":
        return svc.task_log(args["slug"], args["message"])
    elif name == "frai_task_claim":
        return svc.task_claim(args["slug"], args["agent_id"])
    elif name == "frai_task_unclaim":
        return svc.task_unclaim(args["slug"])

    # === Sessions ===
    elif name == "frai_session_current":
        s = svc.session_current()
        return f"Session #{s['id']} started {s['started_at']}" if s else "No active session."
    elif name == "frai_session_list":
        sessions = svc.session_list(args.get("limit", 10))
        return _handle_list(sessions, lambda s: f"#{s['id']} [{s.get('ended_at','active')}] {s.get('summary','')[:60]}", "No sessions.")
    elif name == "frai_session_start":
        return svc.session_start()
    elif name == "frai_session_end":
        return svc.session_end(args.get("summary"))
    elif name == "frai_session_handoff":
        return svc.session_handoff(args["handoff"])
    elif name == "frai_session_last_handoff":
        ho = svc.session_last_handoff()
        return json.dumps(ho, indent=2, ensure_ascii=False) if ho else "No handoff found."

    # === Hierarchy ===
    elif name == "frai_epic_add":
        return svc.epic_add(args["slug"], args["title"], args.get("description"))
    elif name == "frai_epic_list":
        return _handle_list(svc.epic_list(), lambda e: f"[{e['status']}] {e['slug']}: {e['title']}", "No epics.")
    elif name == "frai_epic_done":
        return svc.epic_done(args["slug"])
    elif name == "frai_epic_delete":
        return svc.epic_delete(args["slug"])
    elif name == "frai_story_done":
        return svc.story_done(args["slug"])
    elif name == "frai_story_delete":
        return svc.story_delete(args["slug"])
    elif name == "frai_story_add":
        return svc.story_add(args["epic_slug"], args["slug"], args["title"], args.get("description"))
    elif name == "frai_story_list":
        return _handle_list(svc.story_list(args.get("epic_slug")), lambda s: f"[{s['status']}] {s['slug']}: {s['title']}", "No stories.")
    elif name == "frai_roadmap":
        return _handle_roadmap(svc, args)

    # === Knowledge ===
    elif name == "frai_memory_add":
        return svc.memory_add(args["type"], args["title"], args["content"],
                              args.get("tags"), args.get("task_slug"))
    elif name == "frai_memory_list":
        memories = svc.memory_list(args.get("type"), args.get("limit", 50))
        return _handle_list(memories, lambda r: f"#{r['id']} [{r['type']}] {r['title']}", "No memories.")
    elif name == "frai_memory_show":
        m = svc.memory_show(args["id"])
        return f"#{m['id']} [{m['type']}] {m['title']}\n{m['content']}"
    elif name == "frai_memory_delete":
        return svc.memory_delete(args["id"])
    elif name == "frai_memory_search":
        results = svc.memory_search(args["query"])
        return _handle_list(results, lambda r: f"#{r['id']} [{r['type']}] {r['title']}: {r['content'][:100]}", "No memories found.")

    # === Graph Memory ===
    elif name == "frai_memory_link":
        return svc.memory_link(
            args["source_type"], args["source_id"],
            args["target_type"], args["target_id"],
            args["relation"], args.get("confidence", 1.0), args.get("created_by"),
        )
    elif name == "frai_memory_unlink":
        return svc.memory_unlink(args["edge_id"], args.get("replacement_id"))
    elif name == "frai_memory_related":
        results = svc.memory_related(
            args["node_type"], args["node_id"],
            args.get("max_hops", 2), args.get("include_invalid", False),
        )
        if not results:
            return "No related nodes found."
        lines = []
        for r in results:
            rec = r.get("record", {})
            label = rec.get("title", rec.get("decision", ""))[:60]
            lines.append(f"[{r['depth']} hop] {r['node_type']}#{r['node_id']} --[{r.get('via_relation', '')}]--> {label}")
        return "\n".join(lines)
    elif name == "frai_memory_graph":
        edges = svc.memory_graph(
            args.get("node_type"), args.get("node_id"),
            args.get("relation"), args.get("include_invalid", False), args.get("limit", 50),
        )
        if not edges:
            return "No edges found."
        lines = []
        for e in edges:
            valid = "" if not e.get("valid_to") else f" [invalid]"
            lines.append(f"#{e['id']} {e['source_type']}#{e['source_id']} --[{e['relation']}]--> {e['target_type']}#{e['target_id']}{valid}")
        return "\n".join(lines)

    elif name == "frai_decide":
        return svc.decide(args["decision"], args.get("task_slug"), args.get("rationale"))
    elif name == "frai_decisions_list":
        decs = svc.decisions(args.get("limit", 20))
        return _handle_list(decs, lambda d: f"#{d['id']} {d['decision'][:80]}", "No decisions.")
    elif name == "frai_team":
        data = svc.team_status()
        if not data:
            return "No active tasks."
        lines = []
        for group in data:
            lines.append(f"{group['agent']}:")
            for t in group["tasks"]:
                lines.append(f"  [{t['status']}] {t['slug']}: {t['title']}")
        return "\n".join(lines)
    elif name == "frai_search":
        return _handle_search(svc, args)
    elif name == "frai_metrics":
        return _handle_metrics(svc)
    elif name == "frai_events":
        return _handle_events(svc, args)

    return f"Unknown tool: {name}"


def _handle_health(svc: Any) -> str:
    from frai_version import __version__
    try:
        row = svc.be._q1("SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table'")
        tables = row["cnt"] if row else 0
        schema_row = svc.be._q1("PRAGMA user_version")
        schema_ver = schema_row["user_version"] if schema_row else 0
        return json.dumps({
            "status": "ok",
            "version": __version__,
            "schema_version": schema_ver,
            "tables": tables,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def _handle_status(svc: Any) -> str:
    data = svc.get_status()
    counts = data["task_counts"]
    total = sum(counts.values())
    done = counts.get("done", 0)
    parts = [f"Tasks: {done}/{total} done"]
    for st in ("planning", "active", "blocked", "review"):
        if counts.get(st):
            parts.append(f"{counts[st]} {st}")
    session = data.get("session")
    parts.append(f"Session: #{session['id']}" if session else "Session: none")
    return ", ".join(parts)


def _handle_task_list(svc: Any, args: dict) -> str:
    tasks = svc.task_list(
        status=args.get("status"), story=args.get("story"),
        epic=args.get("epic"), role=args.get("role"),
        stack=args.get("stack"),
    )
    return _handle_list(tasks, lambda t: f"[{t['status']}] {t['slug']}: {t['title']}", "No tasks found.")


def _handle_task_show(svc: Any, args: dict) -> str:
    task = svc.task_show(args["slug"])
    lines = [f"Task: {task['slug']}", f"Title: {task['title']}", f"Status: {task['status']}"]
    for field in ("role", "stack", "complexity", "goal", "notes", "acceptance_criteria"):
        if task.get(field):
            lines.append(f"{field}: {task[field]}")
    if task.get("plan"):
        try:
            steps = json.loads(task["plan"])
            done_count = sum(1 for s in steps if s.get("done"))
            lines.append(f"Plan: {done_count}/{len(steps)} steps")
            for i, s in enumerate(steps, 1):
                mark = "x" if s.get("done") else " "
                lines.append(f"  [{mark}] {i}. {s['step']}")
        except (json.JSONDecodeError, TypeError):
            lines.append("Plan: (corrupted)")
    return "\n".join(lines)


def _handle_roadmap(svc: Any, args: dict) -> str:
    data = svc.get_roadmap(args.get("include_done", False))
    if not data:
        return "No epics."
    lines = []
    for epic in data:
        lines.append(f"[{epic['status']}] {epic['slug']}: {epic['title']}")
        for story in epic.get("stories", []):
            lines.append(f"  [{story['status']}] {story['slug']}: {story['title']}")
            for task in story.get("tasks", []):
                lines.append(f"    [{task['status']}] {task['slug']}: {task['title']}")
    return "\n".join(lines)


def _handle_search(svc: Any, args: dict) -> str:
    results = svc.search(args["query"], args.get("scope", "all"))
    lines = []
    for scope, items in results.items():
        if items:
            lines.append(f"--- {scope} ({len(items)}) ---")
            for item in items[:10]:
                if "slug" in item:
                    lines.append(f"  {item['slug']}: {item.get('title', item.get('decision', ''))}")
                elif "query" in item:
                    lines.append(f"  {item['query']}")
                else:
                    lines.append(f"  {item.get('title', str(item)[:80])}")
    return "\n".join(lines) if lines else "No results."


def _handle_metrics(svc: Any) -> str:
    m = svc.get_metrics()
    parts = [f"Tasks: {m['tasks_done']}/{m['tasks_total']} ({m['completion_pct']}%)"]
    if m["avg_task_hours"]:
        parts.append(f"Avg time: {m['avg_task_hours']}h")
    parts.append(f"Sessions: {m['sessions_total']} ({m['session_hours']}h)")
    return ", ".join(parts)


def _handle_events(svc: Any, args: dict) -> str:
    events = svc.events_list(
        entity_type=args.get("entity_type"),
        entity_id=args.get("entity_id"),
        n=args.get("limit", 50),
    )
    if not events:
        return "No events."
    lines = []
    for ev in events:
        actor = f" by {ev['actor']}" if ev.get("actor") else ""
        lines.append(f"[{ev['created_at']}] {ev['entity_type']}/{ev['entity_id']}: {ev['action']}{actor}")
    return "\n".join(lines)


def _handle_list(items: list, fmt, empty_msg: str = "None.") -> str:
    if not items:
        return empty_msg
    return "\n".join(fmt(item) for item in items)
