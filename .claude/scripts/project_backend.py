"""Frai SQLiteBackend — CRUD. Single-file SQLite, zero deps."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from typing import Any

from backend_queries import BackendQueriesMixin
from backend_migrations import run_migrations
from backend_schema import (
    FTS_SQL, FTS_TRIGGERS_SQL, INDEXES_SQL, SCHEMA_SQL, SCHEMA_VERSION,
)
from frai_utils import utcnow_iso

logger = logging.getLogger("frai.backend")

# Column whitelists for safe UPDATE operations
_EPIC_FIELDS = frozenset({"title", "status", "description"})
_STORY_FIELDS = frozenset({"title", "status", "description"})
_TASK_FIELDS = frozenset({
    "title", "status", "stack", "complexity", "role", "score",
    "goal", "plan", "notes", "acceptance_criteria", "relevant_files",
    "started_at", "completed_at", "blocked_at", "attempts", "story_id",
    "claimed_by", "defect_of", "updated_at",
})


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


class SQLiteBackend(BackendQueriesMixin):
    """All DB operations for Frai. Single SQLite file, FTS5 search."""

    def __init__(self, db_path: str) -> None:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._conn = sqlite3.connect(db_path, timeout=10)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._in_tx = False
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(SCHEMA_SQL)
        cur.executescript(FTS_SQL)
        cur.executescript(FTS_TRIGGERS_SQL)
        cur.executescript(INDEXES_SQL)
        row = cur.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        if not row:
            cur.execute(
                "INSERT INTO meta(key,value) VALUES('schema_version',?)",
                (str(SCHEMA_VERSION),),
            )
        else:
            current_ver = int(row[0])
            if current_ver < SCHEMA_VERSION:
                # Backup DB before migration
                import shutil
                db_path = self._conn.execute("PRAGMA database_list").fetchone()[2]
                backup_path = f"{db_path}.bak.v{current_ver}"
                if db_path and not os.path.exists(backup_path):
                    try:
                        shutil.copy2(db_path, backup_path)
                        logger.info("Backup created: %s", backup_path)
                    except OSError:
                        pass  # best effort
                new_ver = run_migrations(self._conn, current_ver)
                cur.execute(
                    "UPDATE meta SET value=? WHERE key='schema_version'",
                    (str(new_ver),),
                )
                # Rebuild FTS indexes after migration
                for fts_table in ("fts_tasks", "fts_memory", "fts_decisions"):
                    try:
                        cur.execute(f"INSERT INTO {fts_table}({fts_table}) VALUES('rebuild')")
                    except Exception:
                        pass  # FTS table may not exist yet
                logger.info("Schema migrated %d → %d", current_ver, new_ver)
        self._conn.commit()

    def close(self) -> None:
        """Close connection with WAL checkpoint."""
        try:
            self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception:
            pass
        self._conn.close()

    def __enter__(self) -> "SQLiteBackend":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # --- helpers ---

    def _q(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        return [_row_to_dict(r) for r in self._conn.execute(sql, params)]

    def _q1(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        row = self._conn.execute(sql, params).fetchone()
        return _row_to_dict(row) if row else None

    def _ex(self, sql: str, params: tuple = ()) -> int:
        cur = self._conn.execute(sql, params)
        if not self._in_tx:
            self._conn.commit()
        return cur.rowcount

    def _ins(self, sql: str, params: tuple = ()) -> int:
        cur = self._conn.execute(sql, params)
        if not self._in_tx:
            self._conn.commit()
        return cur.lastrowid or 0

    def begin_tx(self) -> None:
        """Begin explicit transaction for multi-step operations."""
        if self._in_tx:
            return  # already in transaction, no nesting
        self._conn.execute("BEGIN IMMEDIATE")
        self._in_tx = True

    def commit_tx(self) -> None:
        """Commit explicit transaction."""
        self._conn.commit()
        self._in_tx = False

    def rollback_tx(self) -> None:
        """Rollback explicit transaction."""
        self._conn.rollback()
        self._in_tx = False

    def _update(self, table: str, allowed: frozenset[str], slug_col: str, slug: str, **fields: Any) -> int:
        """Safe UPDATE — only whitelisted columns allowed."""
        if "updated_at" in allowed:
            fields["updated_at"] = utcnow_iso()
        bad = set(fields) - allowed
        if bad:
            raise ValueError(f"Invalid fields for {table}: {bad}")
        sets = ", ".join(f"{k}=?" for k in fields)
        vals = tuple(fields.values()) + (slug,)
        return self._ex(f"UPDATE {table} SET {sets} WHERE {slug_col}=?", vals)

    def epic_add(self, slug: str, title: str, description: str | None = None) -> None:
        self._ins(
            "INSERT INTO epics(slug,title,description,created_at) VALUES(?,?,?,?)",
            (slug, title, description, utcnow_iso()),
        )

    def epic_get(self, slug: str) -> dict[str, Any] | None:
        return self._q1("SELECT * FROM epics WHERE slug=?", (slug,))

    def epic_list(self) -> list[dict[str, Any]]:
        return self._q("SELECT * FROM epics ORDER BY created_at")

    def epic_update(self, slug: str, **fields: Any) -> int:
        return self._update("epics", _EPIC_FIELDS, "slug", slug, **fields)

    def epic_delete(self, slug: str) -> int:
        return self._ex("DELETE FROM epics WHERE slug=?", (slug,))

    def story_add(
        self, epic_slug: str, slug: str, title: str, description: str | None = None
    ) -> None:
        epic = self.epic_get(epic_slug)
        if not epic:
            raise ValueError(f"Epic '{epic_slug}' not found")
        self._ins(
            "INSERT INTO stories(epic_id,slug,title,description,created_at) VALUES(?,?,?,?,?)",
            (epic["id"], slug, title, description, utcnow_iso()),
        )

    def story_get(self, slug: str) -> dict[str, Any] | None:
        return self._q1(
            "SELECT s.*, e.slug AS epic_slug FROM stories s "
            "JOIN epics e ON s.epic_id=e.id WHERE s.slug=?",
            (slug,),
        )

    def story_list(self, epic_slug: str | None = None) -> list[dict[str, Any]]:
        if epic_slug:
            return self._q(
                "SELECT s.*, e.slug AS epic_slug FROM stories s "
                "JOIN epics e ON s.epic_id=e.id WHERE e.slug=? ORDER BY s.created_at",
                (epic_slug,),
            )
        return self._q(
            "SELECT s.*, e.slug AS epic_slug FROM stories s "
            "JOIN epics e ON s.epic_id=e.id ORDER BY s.created_at"
        )

    def story_update(self, slug: str, **fields: Any) -> int:
        return self._update("stories", _STORY_FIELDS, "slug", slug, **fields)

    def story_delete(self, slug: str) -> int:
        return self._ex("DELETE FROM stories WHERE slug=?", (slug,))

    def story_active_task_count(self, story_slug: str) -> int:
        row = self._q1(
            "SELECT COUNT(*) as cnt FROM tasks t "
            "JOIN stories s ON t.story_id=s.id "
            "WHERE s.slug=? AND t.status NOT IN ('done')",
            (story_slug,),
        )
        return row["cnt"] if row else 0

    def epic_undone_story_count(self, epic_slug: str) -> int:
        row = self._q1(
            "SELECT COUNT(*) as cnt FROM stories s "
            "JOIN epics e ON s.epic_id=e.id "
            "WHERE e.slug=? AND s.status != 'done'",
            (epic_slug,),
        )
        return row["cnt"] if row else 0

    def task_add(
        self, story_slug: str | None, slug: str, title: str,
        stack: str | None = None, complexity: str | None = None,
        score: int | None = None, goal: str | None = None,
        role: str | None = None, defect_of: str | None = None,
    ) -> str:
        story_id = None
        if story_slug:
            story = self.story_get(story_slug)
            if not story:
                raise ValueError(f"Story '{story_slug}' not found")
            story_id = story["id"]
        now = utcnow_iso()
        self._ins(
            "INSERT INTO tasks(story_id,slug,title,stack,complexity,score,goal,role,"
            "defect_of,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (story_id, slug, title, stack, complexity, score, goal, role, defect_of, now, now),
        )
        return slug

    def task_get(self, slug: str) -> dict[str, Any] | None:
        return self._q1("SELECT * FROM tasks WHERE slug=?", (slug,))

    def task_get_full(self, slug: str) -> dict[str, Any] | None:
        return self._q1(
            "SELECT t.*, s.slug AS story_slug, e.slug AS epic_slug "
            "FROM tasks t LEFT JOIN stories s ON t.story_id=s.id "
            "LEFT JOIN epics e ON s.epic_id=e.id WHERE t.slug=?",
            (slug,),
        )

    def task_list(
        self, status: str | None = None, story: str | None = None,
        epic: str | None = None, role: str | None = None,
        stack: str | None = None,
    ) -> list[dict[str, Any]]:
        sql = (
            "SELECT t.*, s.slug AS story_slug, e.slug AS epic_slug "
            "FROM tasks t LEFT JOIN stories s ON t.story_id=s.id "
            "LEFT JOIN epics e ON s.epic_id=e.id WHERE 1=1"
        )
        params: list[Any] = []
        if status:
            placeholders = ",".join("?" for _ in status.split(","))
            sql += f" AND t.status IN ({placeholders})"
            params.extend(status.split(","))
        if story:
            sql += " AND s.slug=?"
            params.append(story)
        if epic:
            sql += " AND e.slug=?"
            params.append(epic)
        if role:
            sql += " AND t.role=?"
            params.append(role)
        if stack:
            sql += " AND t.stack=?"
            params.append(stack)
        sql += " ORDER BY t.created_at"
        return self._q(sql, tuple(params))

    def task_update(self, slug: str, **fields: Any) -> int:
        return self._update("tasks", _TASK_FIELDS, "slug", slug, **fields)

    def task_append_notes(self, slug: str, message: str) -> None:
        """Append a timestamped log entry to task notes (atomic, no read-modify-write)."""
        now = utcnow_iso()
        entry = f"[{now}] {message}"
        rows = self._ex(
            "UPDATE tasks SET notes = CASE WHEN notes IS NULL OR notes = '' "
            "THEN ? ELSE notes || char(10) || ? END, updated_at=? WHERE slug=?",
            (entry, entry, now, slug),
        )
        if rows == 0:
            raise ValueError(f"Task '{slug}' not found")

    def task_claim(self, slug: str, agent_id: str, now: str) -> int:
        """Atomic claim: only succeeds if unclaimed or same agent."""
        rows = self._ex(
            "UPDATE tasks SET claimed_by=?, updated_at=? "
            "WHERE slug=? AND (claimed_by IS NULL OR claimed_by=?)",
            (agent_id, now, slug, agent_id),
        )
        if rows == 0:
            task = self.task_get(slug)
            claimed_by = task["claimed_by"] if task else "unknown"
            raise ValueError(f"Task '{slug}' already claimed by '{claimed_by}'")
        return rows

    def task_delete(self, slug: str) -> int:
        return self._ex("DELETE FROM tasks WHERE slug=?", (slug,))

    def session_start(self) -> int:
        return self._ins("INSERT INTO sessions(started_at) VALUES(?)", (utcnow_iso(),))

    def session_end(self, sid: int, summary: str | None = None) -> None:
        self._ex(
            "UPDATE sessions SET ended_at=?, summary=? WHERE id=?",
            (utcnow_iso(), summary, sid),
        )

    def session_current(self) -> dict[str, Any] | None:
        return self._q1(
            "SELECT * FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1"
        )

    def session_list(self, n: int = 10) -> list[dict[str, Any]]:
        return self._q("SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (n,))

    def session_update_tasks_done(self, sid: int, slugs: list[str]) -> None:
        self._ex("UPDATE sessions SET tasks_done=? WHERE id=?", (json.dumps(slugs), sid))

    def session_update_handoff(self, sid: int, handoff: dict[str, Any]) -> None:
        self._ex("UPDATE sessions SET handoff=? WHERE id=?", (json.dumps(handoff), sid))

    def session_last_handoff(self) -> dict[str, Any] | None:
        return self._q1(
            "SELECT * FROM sessions WHERE handoff IS NOT NULL ORDER BY id DESC LIMIT 1"
        )

    def _resolve_task_slug(self, task_slug: str | None) -> str | None:
        """Validate task_slug exists, return None if not found."""
        if not task_slug:
            return None
        if self.task_get(task_slug):
            return task_slug
        return None

    def decision_add(self, text: str, task_slug: str | None = None, rationale: str | None = None) -> int:
        return self._ins(
            "INSERT INTO decisions(decision,task_slug,rationale,created_at) VALUES(?,?,?,?)",
            (text, self._resolve_task_slug(task_slug), rationale, utcnow_iso()),
        )

    def decision_list(self, n: int = 20) -> list[dict[str, Any]]:
        return self._q("SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (n,))

    def decisions_for_task(self, slug: str) -> list[dict[str, Any]]:
        return self._q("SELECT * FROM decisions WHERE task_slug=? ORDER BY id", (slug,))

    def memory_add(self, mem_type: str, title: str, content: str,
                   tags: list[str] | None = None, task_slug: str | None = None) -> int:
        now = utcnow_iso()
        return self._ins(
            "INSERT INTO memory(type,title,content,tags,task_slug,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (mem_type, title, content, json.dumps(tags) if tags else None,
             self._resolve_task_slug(task_slug), now, now),
        )

    def memory_list(self, mem_type: str | None = None, n: int = 50) -> list[dict[str, Any]]:
        if mem_type:
            return self._q("SELECT * FROM memory WHERE type=? ORDER BY id DESC LIMIT ?", (mem_type, n))
        return self._q("SELECT * FROM memory ORDER BY id DESC LIMIT ?", (n,))

    def memory_get(self, mid: int) -> dict[str, Any] | None:
        return self._q1("SELECT * FROM memory WHERE id=?", (mid,))

    def memory_delete(self, mid: int) -> int:
        return self._ex("DELETE FROM memory WHERE id=?", (mid,))

    # --- graph memory (memory_edges) ---

    _VALID_EDGE_RELATIONS = frozenset({"supersedes", "caused_by", "relates_to", "contradicts"})
    _VALID_NODE_TYPES = frozenset({"memory", "decision"})

    def edge_add(
        self, source_type: str, source_id: int,
        target_type: str, target_id: int,
        relation: str, confidence: float = 1.0,
        created_by: str | None = None,
    ) -> int:
        """Add a graph edge between two memory/decision nodes."""
        now = utcnow_iso()
        return self._ins(
            "INSERT INTO memory_edges(source_type,source_id,target_type,target_id,"
            "relation,confidence,created_by,valid_from,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (source_type, source_id, target_type, target_id,
             relation, confidence, created_by, now, now),
        )

    def edge_invalidate(self, edge_id: int, replacement_id: int | None = None) -> int:
        """Soft-invalidate an edge (Graphiti approach: never delete)."""
        return self._ex(
            "UPDATE memory_edges SET valid_to=?, invalidated_by=? WHERE id=? AND valid_to IS NULL",
            (utcnow_iso(), replacement_id, edge_id),
        )

    def edge_get(self, edge_id: int) -> dict[str, Any] | None:
        return self._q1("SELECT * FROM memory_edges WHERE id=?", (edge_id,))

    def edge_list(
        self, node_type: str | None = None, node_id: int | None = None,
        relation: str | None = None, include_invalid: bool = False,
        n: int = 50,
    ) -> list[dict[str, Any]]:
        """List edges, optionally filtered by node or relation."""
        sql = "SELECT * FROM memory_edges WHERE 1=1"
        params: list[Any] = []
        if not include_invalid:
            sql += " AND valid_to IS NULL"
        if node_type and node_id is not None:
            sql += " AND ((source_type=? AND source_id=?) OR (target_type=? AND target_id=?))"
            params.extend([node_type, node_id, node_type, node_id])
        if relation:
            sql += " AND relation=?"
            params.append(relation)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(n)
        return self._q(sql, tuple(params))

    def edge_list_for_node(self, node_type: str, node_id: int,
                           include_invalid: bool = False) -> list[dict[str, Any]]:
        """All edges connected to a specific node."""
        sql = ("SELECT * FROM memory_edges WHERE "
               "(source_type=? AND source_id=?) OR (target_type=? AND target_id=?)")
        params: list[Any] = [node_type, node_id, node_type, node_id]
        if not include_invalid:
            sql += " AND valid_to IS NULL"
        sql += " ORDER BY created_at DESC"
        return self._q(sql, tuple(params))

    def exploration_start(self, title: str, time_limit_min: int = 30) -> int:
        now = utcnow_iso()
        return self._ins("INSERT INTO explorations(title,time_limit_min,started_at,created_at) VALUES(?,?,?,?)",
                         (title, time_limit_min, now, now))

    def exploration_current(self) -> dict[str, Any] | None:
        return self._q1("SELECT * FROM explorations WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1")

    def exploration_end(self, eid: int, summary: str | None = None, task_slug: str | None = None) -> None:
        self._ex("UPDATE explorations SET ended_at=?, summary=?, task_slug=? WHERE id=?",
                 (utcnow_iso(), summary, task_slug, eid))

    # search_all, get_status_data, get_metrics, get_roadmap_data, events_list, memory_search
    # → inherited from BackendQueriesMixin (backend_queries.py)
