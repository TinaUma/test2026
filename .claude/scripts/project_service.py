"""Frai ProjectService — business logic orchestration.

Composes domain mixins: Hierarchy, Task, Session, Knowledge.
Validates input, enforces business rules, delegates to SQLiteBackend.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

from frai_utils import ServiceError, validate_length, validate_slug
from service_knowledge import KnowledgeMixin
from service_task import TaskMixin

if TYPE_CHECKING:
    from project_backend import SQLiteBackend


class HierarchyMixin:
    """Epic/story CRUD with validation."""

    be: SQLiteBackend

    def epic_add(self, slug: str, title: str, description: str | None = None) -> str:
        validate_slug(slug)
        validate_length("title", title)
        self.be.epic_add(slug, title, description)
        return f"Epic '{slug}' created."

    def epic_list(self) -> list[dict[str, Any]]:
        return self.be.epic_list()

    def epic_done(self, slug: str) -> str:
        epic = self._require_epic(slug)
        self.be.epic_update(slug, status="done")
        return f"Epic '{slug}' marked done."

    def epic_delete(self, slug: str) -> str:
        self._require_epic(slug)
        self.be.epic_delete(slug)
        return f"Epic '{slug}' deleted."

    def story_add(
        self, epic_slug: str, slug: str, title: str, description: str | None = None
    ) -> str:
        self._require_epic(epic_slug)
        validate_slug(slug)
        validate_length("title", title)
        self.be.story_add(epic_slug, slug, title, description)
        return f"Story '{slug}' created in epic '{epic_slug}'."

    def story_list(self, epic_slug: str | None = None) -> list[dict[str, Any]]:
        return self.be.story_list(epic_slug)

    def story_done(self, slug: str) -> str:
        self._require_story(slug)
        self.be.story_update(slug, status="done")
        return f"Story '{slug}' marked done."

    def story_delete(self, slug: str) -> str:
        self._require_story(slug)
        self.be.story_delete(slug)
        return f"Story '{slug}' deleted."


class SessionMixin:
    """Session lifecycle with handoff persistence."""

    be: SQLiteBackend

    def session_start(self) -> str:
        current = self.be.session_current()
        if current:
            return f"Session #{current['id']} already active (started {current['started_at']})."
        sid = self.be.session_start()
        return f"Session #{sid} started."

    def session_check_duration(self, max_minutes: int | None = None) -> str | None:
        """Check if current session exceeds max duration. Returns warning or None."""
        current = self.be.session_current()
        if not current or not current.get("started_at"):
            return None
        from datetime import datetime, timezone
        try:
            started = datetime.fromisoformat(current["started_at"].replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - started).total_seconds() / 60
            limit = max_minutes or 120
            if elapsed > limit:
                return (
                    f"Session #{current['id']} has been running for {int(elapsed)} min "
                    f"(limit: {limit} min). Consider ending with /end."
                )
        except (ValueError, TypeError):
            pass
        return None

    def session_end(self, summary: str | None = None) -> str:
        current = self.be.session_current()
        if not current:
            raise ServiceError("No active session")
        self.be.session_end(current["id"], summary)
        return f"Session #{current['id']} ended."

    def session_current(self) -> dict[str, Any] | None:
        return self.be.session_current()

    def session_list(self, n: int = 10) -> list[dict[str, Any]]:
        return self.be.session_list(n)

    def session_handoff(self, handoff: dict[str, Any]) -> str:
        current = self.be.session_current()
        if not current:
            raise ServiceError("No active session")
        self.be.session_update_handoff(current["id"], handoff)
        return f"Handoff saved for session #{current['id']}."

    def session_last_handoff(self) -> dict[str, Any] | None:
        row = self.be.session_last_handoff()
        if row and row.get("handoff"):
            return dict(json.loads(row["handoff"]))
        return None


class ProjectService(HierarchyMixin, TaskMixin, SessionMixin, KnowledgeMixin):
    """Frai project service — composes all domain mixins."""

    def __init__(self, be: SQLiteBackend) -> None:
        self.be = be

    def _require_epic(self, slug: str) -> dict[str, Any]:
        row = self.be.epic_get(slug)
        if not row:
            raise ServiceError(f"Epic '{slug}' not found")
        return row

    def _require_story(self, slug: str) -> dict[str, Any]:
        row = self.be.story_get(slug)
        if not row:
            raise ServiceError(f"Story '{slug}' not found")
        return row

    def _require_task(self, slug: str) -> dict[str, Any]:
        row = self.be.task_get(slug)
        if not row:
            raise ServiceError(f"Task '{slug}' not found")
        return row

    # --- Top-level operations ---

    def get_status(self) -> dict[str, Any]:
        return self.be.get_status_data()

    def get_metrics(self) -> dict[str, Any]:
        return self.be.get_metrics()

    def get_roadmap(self, include_done: bool = False) -> list[dict[str, Any]]:
        return self.be.get_roadmap_data(include_done)

    def search(self, query: str, scope: str = "all", n: int = 20) -> dict[str, list[dict[str, Any]]]:
        return self.be.search_all(query, scope, n)

    def fts_optimize(self) -> dict[str, str]:
        return self.be.fts_optimize()

    def audit_check(self) -> str | None:
        """Check if periodic audit is overdue (SENAR Rule 9.5). Returns warning or None."""
        row = self.be._q1("SELECT value FROM meta WHERE key='last_audit_session'")
        if not row:
            return "SENAR Rule 9.5: No audit has been performed yet. Run: .frai/frai audit mark"
        last_audit = int(row["value"])
        current = self.be.session_current()
        current_id = current["id"] if current else 0
        if current_id - last_audit >= 3:
            return (
                f"SENAR Rule 9.5: {current_id - last_audit} sessions since last audit. "
                f"Run a quality sweep, then: .frai/frai audit mark"
            )
        return None

    def audit_mark(self) -> str:
        """Mark periodic audit as completed for current session."""
        current = self.be.session_current()
        if not current:
            raise ServiceError("No active session")
        self.be._ex(
            "INSERT OR REPLACE INTO meta(key,value) VALUES('last_audit_session',?)",
            (str(current["id"]),),
        )
        return f"Audit marked at session #{current['id']}."

    # --- Skill Lifecycle ---

    @staticmethod
    def _validate_skill_name(name: str) -> None:
        import re
        if not name or ".." in name or "/" in name or "\\" in name:
            raise ServiceError(f"Invalid skill name '{name}': must not contain path separators or '..'")
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            raise ServiceError(f"Invalid skill name '{name}': must be lowercase alphanumeric with hyphens")

    @staticmethod
    def skill_activate(name: str, vendor_dir: str, skills_dst: str, lib_skills_dir: str) -> str:
        import shutil
        ProjectService._validate_skill_name(name)
        vendor_skill = ProjectService._find_vendor_skill(vendor_dir, name)
        if not vendor_skill:
            raise ServiceError(f"Skill '{name}' not found in vendor. Run bootstrap --update-deps first.")
        dst = os.path.join(skills_dst, name)
        if os.path.exists(dst):
            return f"Skill '{name}' already active."
        shutil.copytree(vendor_skill, dst)
        return f"Skill '{name}' activated. Restart your IDE window to use it."

    @staticmethod
    def skill_deactivate(name: str, skills_dst: str, lib_skills_dir: str) -> str:
        import shutil
        ProjectService._validate_skill_name(name)
        dst = os.path.join(skills_dst, name)
        if not os.path.exists(dst):
            raise ServiceError(f"Skill '{name}' is not active.")
        if os.path.isdir(os.path.join(lib_skills_dir, name)):
            raise ServiceError(f"Skill '{name}' is a core/extension skill, cannot deactivate.")
        shutil.rmtree(dst)
        return f"Skill '{name}' deactivated. Restart your IDE window to apply."

    @staticmethod
    def skill_list(vendor_dir: str, skills_dst: str) -> dict[str, list[dict[str, str]]]:
        active: list[dict[str, str]] = []
        vendored: list[dict[str, str]] = []
        active_names: set[str] = set()
        if os.path.isdir(skills_dst):
            active_names = {d for d in os.listdir(skills_dst) if os.path.isdir(os.path.join(skills_dst, d))}
        if os.path.isdir(vendor_dir):
            for vname in os.listdir(vendor_dir):
                vpath = os.path.join(vendor_dir, vname)
                if not os.path.isdir(vpath):
                    continue
                for item in os.listdir(vpath):
                    item_path = os.path.join(vpath, item)
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "SKILL.md")):
                        entry = {"name": item, "vendor": vname}
                        if item in active_names:
                            active.append(entry)
                        else:
                            vendored.append(entry)
        return {"active": active, "vendored": vendored}

    @staticmethod
    def _find_vendor_skill(vendor_dir: str, name: str) -> str | None:
        if not os.path.isdir(vendor_dir):
            return None
        for vname in os.listdir(vendor_dir):
            vpath = os.path.join(vendor_dir, vname)
            if not os.path.isdir(vpath):
                continue
            skill_path = os.path.join(vpath, name)
            if os.path.isdir(skill_path) and os.path.exists(os.path.join(skill_path, "SKILL.md")):
                return skill_path
        return None
