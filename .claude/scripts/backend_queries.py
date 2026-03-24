"""Frai backend queries — complex aggregations and search.

Separated from project_backend.py to keep CRUD layer clean.
These are mixed into SQLiteBackend via BackendQueriesMixin.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


def _sanitize_fts5(query: str) -> str:
    """Sanitize query for FTS5 MATCH — preserve phrases in quotes, escape the rest."""
    phrases: list[str] = []
    def _extract_phrase(m: re.Match) -> str:
        text = m.group(1).strip()
        if text:
            phrases.append(f'"{text}"')
        return " "
    # Extract "quoted phrases" before stripping
    remaining = re.sub(r'"([^"]*)"', _extract_phrase, query)
    # Strip FTS5 operators, special chars, AND leftover unpaired quotes
    remaining = re.sub(r'["\(\)\*\:\^]', " ", remaining)
    # Remove FTS5 boolean/proximity operators as whole words
    remaining = re.sub(r"\b(AND|OR|NOT|NEAR)\b", " ", remaining)
    remaining = re.sub(r"\s+", " ", remaining).strip()
    parts = ([remaining] if remaining else []) + phrases
    return " ".join(parts) if parts else ""


class BackendQueriesMixin:
    """Complex queries: search, metrics, roadmap, events."""

    # --- Search ---

    def memory_search(self, query: str, n: int = 20) -> list[dict[str, Any]]:
        q = _sanitize_fts5(query)
        if not q:
            return []
        return self._q(
            "SELECT m.*, snippet(fts_memory, 1, '>>>', '<<<', '...', 32) AS _snippet "
            "FROM memory m JOIN fts_memory f ON m.id=f.rowid "
            "WHERE fts_memory MATCH ? ORDER BY bm25(fts_memory, 10.0, 1.0, 3.0) LIMIT ?", (q, n),
        )

    def search_all(
        self, query: str, scope: str = "all", n: int = 20,
    ) -> dict[str, list[dict[str, Any]]]:
        q = _sanitize_fts5(query)
        results: dict[str, list[dict[str, Any]]] = {}
        if not q:
            return results
        if scope in ("all", "tasks"):
            results["tasks"] = self._q(
                "SELECT t.*, snippet(fts_tasks, 1, '>>>', '<<<', '...', 32) AS _snippet "
                "FROM tasks t JOIN fts_tasks f ON t.id=f.rowid "
                "WHERE fts_tasks MATCH ? ORDER BY bm25(fts_tasks, 5.0, 10.0, 3.0, 1.0, 1.0) LIMIT ?", (q, n),
            )
        if scope in ("all", "memory"):
            # Pass pre-sanitized q directly to _q, avoid double-sanitization
            results["memory"] = self._q(
                "SELECT m.*, snippet(fts_memory, 1, '>>>', '<<<', '...', 32) AS _snippet "
                "FROM memory m JOIN fts_memory f ON m.id=f.rowid "
                "WHERE fts_memory MATCH ? ORDER BY bm25(fts_memory, 10.0, 1.0, 3.0) LIMIT ?", (q, n),
            )
        if scope in ("all", "decisions"):
            results["decisions"] = self._q(
                "SELECT d.*, snippet(fts_decisions, 0, '>>>', '<<<', '...', 32) AS _snippet "
                "FROM decisions d JOIN fts_decisions f ON d.id=f.rowid "
                "WHERE fts_decisions MATCH ? ORDER BY bm25(fts_decisions, 10.0, 1.0) LIMIT ?", (q, n),
            )
        return results

    # --- FTS Maintenance ---

    _FTS_TABLES = ("fts_tasks", "fts_memory", "fts_decisions")

    def fts_optimize(self) -> dict[str, str]:
        """Run FTS5 optimize on all full-text indexes."""
        results: dict[str, str] = {}
        for table in self._FTS_TABLES:
            try:
                self._ex(f"INSERT INTO {table}({table}) VALUES('optimize')")
                results[table] = "ok"
            except Exception as e:
                results[table] = str(e)
        return results

    # --- Status & Metrics ---

    def get_status_data(self) -> dict[str, Any]:
        tasks = self._q("SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status")
        return {
            "task_counts": {r["status"]: r["cnt"] for r in tasks},
            "epics": self.epic_list(),
            "session": self.session_current(),
        }

    def get_metrics(self) -> dict[str, Any]:
        """Aggregate project metrics: SENAR mandatory (throughput, lead time, FPSR, DER)
        plus recommended (cycle time, knowledge capture rate, cost/task)."""
        task_counts = {r["status"]: r["cnt"] for r in self._q(
            "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
        )}
        total = sum(task_counts.values())
        done = task_counts.get("done", 0)

        # Cycle time: avg(completed_at - started_at) in hours
        avg_time = self._q1(
            "SELECT AVG((julianday(completed_at) - julianday(started_at)) * 24) as avg_hours "
            "FROM tasks WHERE status='done' AND started_at IS NOT NULL AND completed_at IS NOT NULL"
        )
        avg_hours = round(avg_time["avg_hours"], 1) if avg_time and avg_time["avg_hours"] else None

        # Lead time: avg(completed_at - created_at) in hours
        lead_time = self._q1(
            "SELECT AVG((julianday(completed_at) - julianday(created_at)) * 24) as avg_hours "
            "FROM tasks WHERE status='done' AND completed_at IS NOT NULL"
        )
        lead_hours = round(lead_time["avg_hours"], 1) if lead_time and lead_time["avg_hours"] else None

        # Session stats
        session_stats = self._q1(
            "SELECT COUNT(*) as total, "
            "SUM((julianday(COALESCE(ended_at, datetime('now'))) - julianday(started_at)) * 24) as hours "
            "FROM sessions"
        )
        sessions_total = session_stats["total"] if session_stats else 0

        # SENAR Metric 1: Throughput = tasks_done / sessions
        throughput = round(done / sessions_total, 2) if sessions_total else 0

        # SENAR Metric 3: FPSR = tasks with attempts=1 / total done * 100
        fpsr_row = self._q1(
            "SELECT COUNT(*) as cnt FROM tasks WHERE status='done' AND attempts=1"
        )
        first_pass = fpsr_row["cnt"] if fpsr_row else 0
        fpsr = round(first_pass / done * 100, 1) if done else 0

        # SENAR Metric 4: DER = unique parent tasks with defects / non-defect done tasks * 100
        der_row = self._q1(
            "SELECT COUNT(DISTINCT defect_of) as cnt FROM tasks WHERE defect_of IS NOT NULL"
        )
        defect_count = der_row["cnt"] if der_row else 0
        non_defect_done_row = self._q1(
            "SELECT COUNT(*) as cnt FROM tasks WHERE status='done' AND defect_of IS NULL"
        )
        non_defect_done = non_defect_done_row["cnt"] if non_defect_done_row else 0
        der = round(defect_count / non_defect_done * 100, 1) if non_defect_done else 0

        # Knowledge Capture Rate = memory entries / done tasks
        mem_row = self._q1("SELECT COUNT(*) as cnt FROM memory")
        mem_count = mem_row["cnt"] if mem_row else 0
        kcr = round(mem_count / done, 2) if done else 0

        story_counts = {r["status"]: r["cnt"] for r in self._q(
            "SELECT status, COUNT(*) as cnt FROM stories GROUP BY status"
        )}

        return {
            "tasks": task_counts,
            "tasks_total": total,
            "tasks_done": done,
            "completion_pct": round(done / total * 100, 1) if total else 0,
            # SENAR mandatory metrics
            "throughput": throughput,
            "lead_time_hours": lead_hours,
            "fpsr": fpsr,
            "der": der,
            # SENAR recommended metrics
            "cycle_time_hours": avg_hours,
            "knowledge_capture_rate": kcr,
            # Legacy
            "avg_task_hours": avg_hours,
            "sessions_total": sessions_total,
            "session_hours": round(session_stats["hours"], 1) if session_stats and session_stats["hours"] else 0,
            "stories": story_counts,
        }

    # --- Roadmap ---

    def get_roadmap_data(self, include_done: bool = False) -> list[dict[str, Any]]:
        all_tasks = self._q(
            "SELECT t.*, s.slug AS story_slug, s.title AS story_title, "
            "s.status AS story_status, e.slug AS epic_slug, e.title AS epic_title, "
            "e.status AS epic_status "
            "FROM tasks t "
            "LEFT JOIN stories s ON t.story_id=s.id "
            "LEFT JOIN epics e ON s.epic_id=e.id "
            "ORDER BY e.created_at, s.created_at, t.created_at"
        )
        epics = {e["slug"]: e for e in self.epic_list()}
        stories_by_epic: dict[str, list[dict[str, Any]]] = {}
        for s in self._q(
            "SELECT s.*, e.slug AS epic_slug FROM stories s "
            "JOIN epics e ON s.epic_id=e.id ORDER BY s.created_at"
        ):
            stories_by_epic.setdefault(s["epic_slug"], []).append(s)

        tree: dict[str, dict[str, Any]] = {}
        task_map: dict[str, list[dict[str, Any]]] = {}

        for t in all_tasks:
            ss = t.get("story_slug")
            if ss:
                task_map.setdefault(ss, []).append(t)

        for epic_slug, epic in epics.items():
            if not include_done and epic["status"] == "done":
                continue
            epic_data: dict[str, Any] = {**epic, "stories": []}
            for story in stories_by_epic.get(epic_slug, []):
                if not include_done and story["status"] == "done":
                    continue
                tasks = task_map.get(story["slug"], [])
                if not include_done:
                    tasks = [t for t in tasks if t["status"] != "done"]
                epic_data["stories"].append({**story, "tasks": tasks})
            tree[epic_slug] = epic_data

        return list(tree.values())

    # --- Graph Memory ---

    def graph_related(
        self, node_type: str, node_id: int, max_hops: int = 2,
        include_invalid: bool = False,
    ) -> list[dict[str, Any]]:
        """Find related nodes via recursive CTE graph traversal (1-N hops)."""
        max_hops = min(max_hops, 3)  # cap depth to prevent runaway
        valid_filter = "" if include_invalid else "AND e.valid_to IS NULL"
        sql = f"""
        WITH RECURSIVE reachable(node_type, node_id, depth, via_edge, via_relation) AS (
            -- seed: direct neighbors
            SELECT e.target_type, e.target_id, 1, e.id, e.relation
            FROM memory_edges e
            WHERE e.source_type=? AND e.source_id=? {valid_filter}
            UNION
            SELECT e.source_type, e.source_id, 1, e.id, e.relation
            FROM memory_edges e
            WHERE e.target_type=? AND e.target_id=? {valid_filter}
            UNION ALL
            -- recurse: neighbors of neighbors
            SELECT e.target_type, e.target_id, r.depth+1, e.id, e.relation
            FROM reachable r
            JOIN memory_edges e ON e.source_type=r.node_type AND e.source_id=r.node_id
                {valid_filter}
            WHERE r.depth < ? AND NOT (e.target_type=? AND e.target_id=?)
            UNION ALL
            SELECT e.source_type, e.source_id, r.depth+1, e.id, e.relation
            FROM reachable r
            JOIN memory_edges e ON e.target_type=r.node_type AND e.target_id=r.node_id
                {valid_filter}
            WHERE r.depth < ? AND NOT (e.source_type=? AND e.source_id=?)
        )
        SELECT DISTINCT node_type, node_id, MIN(depth) as depth,
               via_edge, via_relation
        FROM reachable
        WHERE NOT (node_type=? AND node_id=?)
        GROUP BY node_type, node_id
        ORDER BY depth, node_type, node_id
        """
        params = (
            node_type, node_id,
            node_type, node_id,
            max_hops, node_type, node_id,
            max_hops, node_type, node_id,
            node_type, node_id,
        )
        return self._q(sql, params)

    def graph_resolve_nodes(self, node_refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Resolve node references to full records. node_refs: [{node_type, node_id, ...}]."""
        results = []
        for ref in node_refs:
            ntype, nid = ref["node_type"], ref["node_id"]
            if ntype == "memory":
                row = self._q1("SELECT * FROM memory WHERE id=?", (nid,))
            elif ntype == "decision":
                row = self._q1("SELECT * FROM decisions WHERE id=?", (nid,))
            else:
                row = None
            if row:
                results.append({**ref, "record": row})
        return results

    # --- Events ---

    def events_list(
        self, entity_type: str | None = None, entity_id: str | None = None,
        n: int = 50,
    ) -> list[dict[str, Any]]:
        """List audit events with optional filters."""
        n = min(n, 1000)
        sql = "SELECT * FROM events WHERE 1=1"
        params: list[Any] = []
        if entity_type:
            sql += " AND entity_type=?"
            params.append(entity_type)
        if entity_id:
            sql += " AND entity_id=?"
            params.append(entity_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(n)
        return self._q(sql, tuple(params))

