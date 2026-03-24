"""Frai CLI handlers — memory, gates, skill, fts, update-claudemd commands."""

from __future__ import annotations

import json
from typing import Any

from project_service import ProjectService


def cmd_memory(svc: ProjectService, args: Any) -> None:
    c = args.memory_cmd
    if c == "add":
        print(svc.memory_add(args.mem_type, args.title, args.content, args.tags, args.task))
    elif c == "list":
        rows = svc.memory_list(args.mem_type, args.limit)
        if not rows:
            print("  (no memories)")
            return
        for r in rows:
            tags = ""
            if r.get("tags"):
                try:
                    tags = " " + ", ".join(json.loads(r["tags"]))
                except (json.JSONDecodeError, TypeError):
                    pass
            print(f"  #{r['id']} [{r['type']}] {r['title']}{tags}")
    elif c == "search":
        rows = svc.memory_search(args.query)
        if not rows:
            print("  No results.")
            return
        for r in rows:
            print(f"  #{r['id']} [{r['type']}] {r['title']}")
    elif c == "show":
        r = svc.memory_show(args.id)
        print(f"#{r['id']} [{r['type']}] {r['title']}")
        print(f"Created: {r.get('created_at', '')}")
        if r.get("tags"):
            try:
                print(f"Tags: {', '.join(json.loads(r['tags']))}")
            except (json.JSONDecodeError, TypeError):
                pass
        if r.get("task_slug"):
            print(f"Task: {r['task_slug']}")
        print(f"\n{r['content']}")
    elif c == "delete":
        print(svc.memory_delete(args.id))
    elif c == "link":
        print(svc.memory_link(
            args.source_type, args.source_id,
            args.target_type, args.target_id,
            args.relation, args.confidence, args.created_by,
        ))
    elif c == "unlink":
        print(svc.memory_unlink(args.edge_id, args.replacement))
    elif c == "related":
        results = svc.memory_related(args.node_type, args.node_id, args.hops, args.include_invalid)
        if not results:
            print("  No related nodes found.")
            return
        for r in results:
            rec = r.get("record", {})
            ntype = r["node_type"]
            nid = r["node_id"]
            depth = r["depth"]
            rel = r.get("via_relation", "")
            label = rec.get("title", rec.get("decision", ""))[:60]
            print(f"  [{depth} hop] {ntype}#{nid} --[{rel}]--> {label}")
    elif c == "graph":
        edges = svc.memory_graph(
            args.node_type, args.node_id, args.relation, args.include_invalid, args.limit,
        )
        if not edges:
            print("  No edges found.")
            return
        for e in edges:
            valid = "" if not e.get("valid_to") else f" [invalid {e['valid_to'][:10]}]"
            conf = f" ({e['confidence']:.0%})" if e["confidence"] < 1.0 else ""
            print(f"  #{e['id']} {e['source_type']}#{e['source_id']} "
                  f"--[{e['relation']}]--> {e['target_type']}#{e['target_id']}"
                  f"{conf}{valid}")


def cmd_update_claudemd(svc: ProjectService, args: Any) -> None:
    """Update <!-- DYNAMIC:START --> section in CLAUDE.md."""
    import os
    import subprocess

    # Find CLAUDE.md
    claudemd = args.claudemd
    if not claudemd:
        # Auto-detect: look in cwd, then parent dirs
        for candidate in ["CLAUDE.md", ".claude/CLAUDE.md"]:
            if os.path.exists(candidate):
                claudemd = candidate
                break
    if not claudemd or not os.path.exists(claudemd):
        print("Error: CLAUDE.md not found. Use --claudemd to specify path.")
        return

    # Gather data
    status = svc.get_status()
    tasks = svc.task_list()
    session = svc.session_current()

    # Build dynamic section
    active = [t for t in tasks if t["status"] == "active"]
    blocked = [t for t in tasks if t["status"] == "blocked"]
    done_count = sum(1 for t in tasks if t["status"] == "done")
    total = len(tasks)

    # Get branch
    try:
        r = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5)
        branch = r.stdout.strip() or "unknown"
    except Exception:
        branch = "unknown"

    session_info = f"#{session['id']} (active)" if session else "none"

    lines = [
        f"## Current State",
        f"Session: {session_info} | Branch: {branch} | Version: {_get_version()}",
        f"Tasks: {done_count}/{total} done, {len(active)} active, {len(blocked)} blocked",
    ]
    if active:
        lines.append(f"Active: {', '.join(t['slug'] for t in active)}")
    if blocked:
        lines.append(f"Blocked: {', '.join(t['slug'] for t in blocked)}")

    dynamic_content = "\n".join(lines)

    # Read and replace
    with open(claudemd, encoding="utf-8") as f:
        content = f.read()

    marker_start = "<!-- DYNAMIC:START -->"
    marker_end = "<!-- DYNAMIC:END -->"

    if marker_start in content:
        if marker_end in content:
            before = content[:content.index(marker_start) + len(marker_start)]
            after = content[content.index(marker_end):]
            content = f"{before}\n{dynamic_content}\n{after}"
        else:
            # No end marker — replace from start marker to end of file
            before = content[:content.index(marker_start) + len(marker_start)]
            content = f"{before}\n{dynamic_content}\n{marker_end}\n"
    else:
        print("Warning: <!-- DYNAMIC:START --> marker not found in CLAUDE.md")
        return

    with open(claudemd, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"CLAUDE.md updated ({claudemd}).")


def _get_version() -> str:
    """Get Frai version from frai_version.py."""
    try:
        from frai_version import __version__
        return __version__
    except ImportError:
        return "unknown"


def cmd_fts(svc: ProjectService, args: Any) -> None:
    c = getattr(args, "fts_cmd", None)
    if c == "optimize":
        results = svc.fts_optimize()
        for table, status in results.items():
            print(f"  {table}: {status}")
        print("FTS5 optimization complete.")
    else:
        print("Usage: frai fts optimize")


def cmd_skill(svc: ProjectService, args: Any) -> None:
    """Handle skill lifecycle: activate, deactivate, list."""
    import os

    c = getattr(args, "skill_cmd", None)
    project_dir = os.getcwd()
    vendor_dir = os.path.join(project_dir, ".frai", "vendor")
    skills_dst = os.path.join(project_dir, ".claude", "skills")
    lib_skills_dir = os.path.join(project_dir, "agents", "claude", "skills")

    if c == "activate":
        print(svc.skill_activate(args.name, vendor_dir, skills_dst, lib_skills_dir))
    elif c == "deactivate":
        print(svc.skill_deactivate(args.name, skills_dst, lib_skills_dir))
    elif c == "list":
        data = svc.skill_list(vendor_dir, skills_dst)
        print("Skills:")
        for s in sorted(data["active"], key=lambda x: x["name"]):
            print(f"  [ACTIVE  ] {s['name']}")
        for s in sorted(data["vendored"], key=lambda x: x["name"]):
            print(f"  [VENDORED] {s['name']}")
        if not data["active"] and not data["vendored"]:
            print("  (none)")
    else:
        print("Usage: frai skill [activate|deactivate|list]")


def cmd_gates(_svc: ProjectService, args: Any) -> None:
    """Handle gates subcommands: status, list, enable, disable."""
    from project_config import load_config, load_gates, save_config, VALID_GATE_TRIGGERS

    c = args.gates_cmd
    if not c:
        c = "status"

    if c in ("status", "list"):
        gates = load_gates()
        if not gates:
            print("No gates configured.")
            return
        print("Quality Gates:")
        for name, gate in sorted(gates.items()):
            status = "ON" if gate.get("enabled", True) else "OFF"
            severity = gate.get("severity", "warn")
            triggers = ", ".join(gate.get("trigger", []))
            desc = gate.get("description", "")
            cmd = gate.get("command") or "(built-in)"
            print(f"  [{status}] {name} ({severity}) -> {triggers}")
            print(f"         {desc}")
            if c == "status" and gate.get("enabled", True):
                print(f"         cmd: {cmd}")
        # QG-0 readiness report
        if c == "status":
            try:
                tasks = _svc.task_list("planning")
                no_goal = [t for t in tasks if not t.get("goal") or not str(t["goal"]).strip()]
                no_ac = [t for t in tasks if not t.get("acceptance_criteria") or not str(t["acceptance_criteria"]).strip()]
                if no_goal or no_ac:
                    print(f"\n  QG-0 Readiness ({len(tasks)} planning tasks):")
                    if no_goal:
                        slugs = ", ".join(t["slug"] for t in no_goal[:5])
                        more = f" (+{len(no_goal) - 5})" if len(no_goal) > 5 else ""
                        print(f"    ⚠ {len(no_goal)} without goal: {slugs}{more}")
                    if no_ac:
                        slugs = ", ".join(t["slug"] for t in no_ac[:5])
                        more = f" (+{len(no_ac) - 5})" if len(no_ac) > 5 else ""
                        print(f"    ⚠ {len(no_ac)} without acceptance_criteria: {slugs}{more}")
                elif tasks:
                    print(f"\n  QG-0 Readiness: all {len(tasks)} planning tasks have goal + AC")
            except Exception:
                pass  # DB not available or no tasks table

    elif c == "enable":
        cfg = load_config()
        cfg.setdefault("gates", {}).setdefault(args.name, {})["enabled"] = True
        save_config(cfg)
        print(f"Gate '{args.name}' enabled.")

    elif c == "disable":
        cfg = load_config()
        cfg.setdefault("gates", {}).setdefault(args.name, {})["enabled"] = False
        save_config(cfg)
        print(f"Gate '{args.name}' disabled.")
