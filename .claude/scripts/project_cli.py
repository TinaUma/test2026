"""Frai CLI handlers — dispatch + formatting for core commands."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

from project_config import find_frai_dir, get_config_path, save_config
from frai_utils import ServiceError
from project_service import ProjectService


def _print_table(rows: list[dict[str, Any]], columns: list[str]) -> None:
    """Print a simple table."""
    if not rows:
        print("  (none)")
        return
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    header = "  ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))


def cmd_init(svc: ProjectService, args: Any) -> None:
    """Initialize Frai project."""
    frai_dir = find_frai_dir()
    os.makedirs(frai_dir, exist_ok=True)
    cfg_path = get_config_path()
    if not os.path.exists(cfg_path):
        save_config({"project": args.name, "version": 1})
        print(f"Config created: {cfg_path}")
    else:
        print(f"Config already exists: {cfg_path}")
    print(f"Database: {os.path.join(frai_dir, 'frai.db')}")
    print(f"Project '{args.name}' initialized.")


def cmd_status(svc: ProjectService, args: Any) -> None:
    data = svc.get_status()
    counts = data["task_counts"]
    total = sum(counts.values())
    done = counts.get("done", 0)
    print(f"Tasks: {done}/{total} done", end="")
    for st in ("planning", "active", "blocked", "review"):
        if counts.get(st):
            print(f", {counts[st]} {st}", end="")
    print()
    if data["session"]:
        print(f"Session: #{data['session']['id']} (started {data['session']['started_at']})")
        # SENAR Rule 9.2: session duration warning
        from project_config import load_config, DEFAULT_SESSION_MAX_MINUTES
        cfg = load_config()
        max_min = cfg.get("session_max_minutes", DEFAULT_SESSION_MAX_MINUTES)
        warning = svc.session_check_duration(max_min)
        if warning:
            print(f"  WARNING: {warning}")
    else:
        print("Session: none active")
    if data["epics"]:
        print(f"Epics: {len(data['epics'])}")


def cmd_epic(svc: ProjectService, args: Any) -> None:
    if args.epic_cmd == "add":
        print(svc.epic_add(args.slug, args.title, args.description))
    elif args.epic_cmd == "list":
        _print_table(svc.epic_list(), ["slug", "title", "status"])
    elif args.epic_cmd == "done":
        print(svc.epic_done(args.slug))
    elif args.epic_cmd == "delete":
        print(svc.epic_delete(args.slug))
    else:
        print("Usage: frai epic [add|list|done|delete]")


def cmd_story(svc: ProjectService, args: Any) -> None:
    if args.story_cmd == "add":
        print(svc.story_add(args.epic_slug, args.slug, args.title, args.description))
    elif args.story_cmd == "list":
        _print_table(svc.story_list(args.epic), ["slug", "title", "status", "epic_slug"])
    elif args.story_cmd == "done":
        print(svc.story_done(args.slug))
    elif args.story_cmd == "delete":
        print(svc.story_delete(args.slug))
    else:
        print("Usage: frai story [add|list|done|delete]")


def cmd_task(svc: ProjectService, args: Any) -> None:
    c = args.task_cmd
    if c == "add":
        slug = args.slug or _auto_slug(args.title)
        story_slug = getattr(args, "story_slug", None)
        defect_of = getattr(args, "defect_of", None)
        print(svc.task_add(story_slug, slug, args.title,
                           args.stack, args.complexity, args.goal, args.role, defect_of))
    elif c == "list":
        tasks = svc.task_list(args.status, args.story, args.epic, args.role, args.stack)
        _print_table(tasks, ["slug", "title", "status", "story_slug", "role", "stack"])
    elif c == "show":
        task = svc.task_show(args.slug)
        _print_task_detail(task)
    elif c == "start":
        print(svc.task_start(args.slug))
    elif c == "done":
        print(svc.task_done(args.slug, args.force, args.relevant_files, args.ac_verified))
    elif c == "block":
        print(svc.task_block(args.slug, args.reason))
    elif c == "unblock":
        print(svc.task_unblock(args.slug))
    elif c == "review":
        print(svc.task_review(args.slug))
    elif c == "update":
        fields = {}
        for k in ("title", "goal", "notes", "stack", "complexity", "role"):
            v = getattr(args, k, None)
            if v is not None:
                fields[k] = v
        if args.ac is not None:
            fields["acceptance_criteria"] = args.ac
        if fields:
            print(svc.task_update(args.slug, **fields))
        else:
            print("No fields to update.")
    elif c == "delete":
        print(svc.task_delete(args.slug))
    elif c == "plan":
        print(svc.task_plan(args.slug, args.steps))
    elif c == "step":
        print(svc.task_step(args.slug, args.step_num))
    elif c == "move":
        print(svc.task_move(args.slug, args.new_story_slug))
    elif c == "claim":
        print(svc.task_claim(args.slug, args.agent_id))
    elif c == "unclaim":
        print(svc.task_unclaim(args.slug))
    elif c == "quick":
        print(svc.task_quick(args.title, args.goal, args.role, args.stack))
    elif c == "next":
        next_task = svc.task_next(args.agent)
        if next_task:
            action = "claimed and started" if args.agent else "suggested"
            print(f"Next task ({action}): {next_task['slug']} — {next_task['title']}")
        else:
            print("No available tasks.")
    elif c == "log":
        print(svc.task_log(args.slug, args.message))
    else:
        subcmds = "add, list, show, start, done, block, unblock, review, update, delete, plan, step, quick, next, move, claim, unclaim, log"
        if c:
            from difflib import get_close_matches
            matches = get_close_matches(c, subcmds.replace(" ", "").split(","), n=2, cutoff=0.5)
            if matches:
                print(f"Unknown subcommand 'task {c}'. Did you mean: {', '.join(matches)}?", file=sys.stderr)
                return
        print(f"Usage: frai task [{subcmds}]")


def cmd_team(svc: ProjectService, args: Any) -> None:
    data = svc.team_status()
    if not data:
        print("No active tasks.")
        return
    for group in data:
        print(f"\n{group['agent']}:")
        for t in group["tasks"]:
            print(f"  [{t['status']}] {t['slug']}: {t['title']}")


def cmd_session(svc: ProjectService, args: Any) -> None:
    c = args.session_cmd
    if c == "start":
        print(svc.session_start())
    elif c == "end":
        print(svc.session_end(args.summary))
    elif c == "current":
        s = svc.session_current()
        if s:
            print(f"Session #{s['id']} started {s['started_at']}")
        else:
            print("No active session.")
    elif c == "list":
        sessions = svc.session_list(args.limit)
        _print_table(sessions, ["id", "started_at", "ended_at", "summary"])
    elif c == "handoff":
        try:
            data = json.loads(args.json_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error: invalid JSON for handoff: {e}", file=sys.stderr)
            return
        print(svc.session_handoff(data))
    elif c == "last-handoff":
        ho = svc.session_last_handoff()
        if ho:
            print(json.dumps(ho, indent=2, ensure_ascii=False))
        else:
            print("No handoff found.")
    else:
        print("Usage: frai session [start|end|current|list|handoff|last-handoff]")


def cmd_decide(svc: ProjectService, args: Any) -> None:
    print(svc.decide(args.text, args.task, args.rationale))


def cmd_decisions(svc: ProjectService, args: Any) -> None:
    _print_table(svc.decisions(args.limit), ["id", "decision", "task_slug", "created_at"])


def cmd_roadmap(svc: ProjectService, args: Any) -> None:
    data = svc.get_roadmap(args.include_done)
    if not data:
        print("No epics.")
        return
    for epic in data:
        print(f"[{epic['status']}] {epic['slug']}: {epic['title']}")
        for story in epic.get("stories", []):
            print(f"  [{story['status']}] {story['slug']}: {story['title']}")
            for task in story.get("tasks", []):
                print(f"    [{task['status']}] {task['slug']}: {task['title']}")


def cmd_metrics(svc: ProjectService, args: Any) -> None:
    m = svc.get_metrics()
    print(f"Tasks: {m['tasks_done']}/{m['tasks_total']} done ({m['completion_pct']}%)")
    for status, cnt in sorted(m["tasks"].items()):
        print(f"  {status}: {cnt}")
    # SENAR mandatory metrics
    print(f"\n--- SENAR Metrics ---")
    print(f"Throughput:    {m['throughput']} tasks/session")
    lt = f"{m['lead_time_hours']}h" if m.get('lead_time_hours') is not None else "n/a"
    print(f"Lead Time:     {lt} (avg created→done)")
    print(f"FPSR:          {m['fpsr']}% (first-pass success rate)")
    print(f"DER:           {m['der']}% (defect escape rate)")
    # Recommended
    ct = f"{m['cycle_time_hours']}h" if m.get('cycle_time_hours') is not None else "n/a"
    print(f"Cycle Time:    {ct} (avg started→done)")
    print(f"Knowledge CR:  {m['knowledge_capture_rate']} entries/task")
    print(f"\nSessions: {m['sessions_total']} ({m['session_hours']}h total)")
    if m["stories"]:
        total_s = sum(m["stories"].values())
        done_s = m["stories"].get("done", 0)
        print(f"Stories: {done_s}/{total_s} done")


def cmd_search(svc: ProjectService, args: Any) -> None:
    results = svc.search(args.query, args.scope, getattr(args, "limit", 20))
    for scope, items in results.items():
        if items:
            print(f"\n--- {scope} ({len(items)} results) ---")
            for item in items[:10]:
                if "slug" in item:
                    print(f"  {item['slug']}: {item.get('title', item.get('decision', ''))}")
                else:
                    print(f"  {item.get('title', item.get('decision', str(item)[:80]))}")
                snippet = item.get("_snippet")
                if snippet:
                    print(f"    {snippet}")


def cmd_events(svc: ProjectService, args: Any) -> None:
    events = svc.events_list(
        entity_type=args.entity, entity_id=args.entity_id, n=args.limit,
    )
    if not events:
        print("No events found.")
        return
    for ev in events:
        actor = f" by {ev['actor']}" if ev.get("actor") else ""
        print(f"[{ev['created_at']}] {ev['entity_type']}/{ev['entity_id']}: "
              f"{ev['action']}{actor}")
        if ev.get("details"):
            print(f"  {ev['details']}")


def cmd_dead_end(svc: ProjectService, args: Any) -> None:
    print(svc.dead_end(args.approach, args.reason, args.tags, args.task))


def cmd_explore(svc: ProjectService, args: Any) -> None:
    c = args.explore_cmd
    if c == "start":
        print(svc.exploration_start(args.title, args.time_limit))
    elif c == "end":
        print(svc.exploration_end(args.summary, args.create_task))
    elif c == "current":
        exp = svc.exploration_current()
        if exp:
            elapsed = exp.get("elapsed_min", "?")
            limit = exp.get("time_limit_min", 30)
            over = " [OVER LIMIT]" if exp.get("over_limit") else ""
            print(f"Exploration #{exp['id']}: {exp['title']}")
            print(f"  Elapsed: {elapsed} min / {limit} min{over}")
        else:
            print("No active exploration.")
    else:
        print("Usage: frai explore [start|end|current]")


def cmd_audit(svc: ProjectService, args: Any) -> None:
    c = getattr(args, "audit_cmd", None)
    if c == "check":
        warning = svc.audit_check()
        if warning:
            print(f"WARNING: {warning}")
        else:
            print("Audit is up to date.")
    elif c == "mark":
        print(svc.audit_mark())
    else:
        warning = svc.audit_check()
        if warning:
            print(f"WARNING: {warning}")
        else:
            print("Audit is up to date.")


def _auto_slug(title: str) -> str:
    """Generate slug from title."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:50] if slug else "task"


def _print_task_detail(task: dict[str, Any]) -> None:
    """Print full task details."""
    print(f"Task: {task['slug']}")
    print(f"Title: {task['title']}")
    print(f"Status: {task['status']}")
    for field in ("story_slug", "epic_slug", "role", "stack", "complexity",
                  "goal", "acceptance_criteria", "notes", "started_at",
                  "completed_at", "blocked_at", "relevant_files",
                  "defect_of", "claimed_by", "attempts"):
        val = task.get(field)
        if val:
            print(f"{field}: {val}")
    if task.get("plan"):
        try:
            steps = json.loads(task["plan"])
            done_count = sum(1 for s in steps if s.get("done"))
            print(f"Plan: {done_count}/{len(steps)} steps done")
            for i, s in enumerate(steps, 1):
                mark = "x" if s.get("done") else " "
                print(f"  [{mark}] {i}. {s['step']}")
        except (json.JSONDecodeError, TypeError):
            print(f"Plan: (corrupted data)")
    decisions = task.get("decisions", [])
    if decisions:
        print(f"Decisions ({len(decisions)}):")
        for d in decisions:
            print(f"  - {d['decision']}")
