"""Frai TaskMixin — task lifecycle with strict workflow enforcement."""

from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING, Any

from frai_utils import ServiceError, validate_content, validate_length, validate_slug
from project_types import (
    COMPLEXITY_SP, VALID_COMPLEXITIES,
    VALID_STACKS, VALID_TASK_STATUSES,
)

if TYPE_CHECKING:
    from project_backend import SQLiteBackend


class TaskMixin:
    """Task lifecycle with strict workflow enforcement."""

    be: SQLiteBackend

    def task_add(
        self, story_slug: str | None, slug: str, title: str,
        stack: str | None = None, complexity: str | None = None,
        goal: str | None = None, role: str | None = None,
        defect_of: str | None = None,
    ) -> str:
        if story_slug:
            self._require_story(story_slug)
        validate_slug(slug)
        validate_length("title", title)
        if complexity and complexity not in VALID_COMPLEXITIES:
            raise ServiceError(f"Invalid complexity '{complexity}', must be one of {VALID_COMPLEXITIES}")
        if stack and stack not in VALID_STACKS:
            raise ServiceError(f"Invalid stack '{stack}', must be one of {sorted(VALID_STACKS)}")
        if defect_of:
            self._require_task(defect_of)  # parent must exist
        validate_content("goal", goal)
        score = COMPLEXITY_SP.get(complexity, 1) if complexity else 1
        self.be.task_add(story_slug, slug, title, stack, complexity, score, goal, role, defect_of)
        warnings: list[str] = []
        if not goal or not goal.strip():
            warnings.append("goal")
        # AC is set via task update, so warn if goal is missing (AC likely missing too)
        msg = f"Task '{slug}' created."
        if warnings:
            msg += f"\n⚠ QG-0 warning: missing {', '.join(warnings)}. Task won't start without goal + acceptance_criteria."
        return msg

    def task_list(
        self, status: str | None = None, story: str | None = None,
        epic: str | None = None, role: str | None = None,
        stack: str | None = None,
    ) -> list[dict[str, Any]]:
        if status:
            for s in status.split(","):
                if s not in VALID_TASK_STATUSES:
                    raise ServiceError(f"Invalid status '{s}', must be one of {sorted(VALID_TASK_STATUSES)}")
        return self.be.task_list(status, story, epic, role, stack)

    def task_show(self, slug: str) -> dict[str, Any]:
        task = self.be.task_get_full(slug)
        if not task:
            raise ServiceError(f"Task '{slug}' not found")
        task["decisions"] = self.be.decisions_for_task(slug)
        return task

    def task_start(self, slug: str, _internal_force: bool = False) -> str:
        task = self._require_task(slug)
        if task["status"] == "done":
            raise ServiceError(f"Task '{slug}' is already done")
        if task["status"] == "active":
            return f"Task '{slug}' is already active."
        # QG-0: Context Gate — goal and acceptance_criteria required before work
        if not _internal_force:
            missing = []
            if not task.get("goal") or not task["goal"].strip():
                missing.append("goal")
            if not task.get("acceptance_criteria") or not task["acceptance_criteria"].strip():
                missing.append("acceptance_criteria")
            if missing:
                raise ServiceError(
                    f"QG-0 Context Gate: '{slug}' cannot start — missing {', '.join(missing)}. "
                    f"Fix: .frai/frai task update {slug} --goal '...' --acceptance-criteria '...'"
                )
        updates: dict[str, Any] = {"status": "active", "attempts": task.get("attempts", 0) + 1}
        if not task.get("started_at"):
            from frai_utils import utcnow_iso
            updates["started_at"] = utcnow_iso()
        self.be.begin_tx()
        try:
            self.be.task_update(slug, **updates)
            self._cascade_start(slug)
            self.be.commit_tx()
        except Exception:
            self.be.rollback_tx()
            raise
        return f"Task '{slug}' started (attempt #{updates['attempts']})."

    def task_done(self, slug: str, force: bool = False, relevant_files: list[str] | None = None,
                  ac_verified: bool = False) -> str:
        task = self._require_task(slug)
        if task["status"] == "done":
            raise ServiceError(f"Task '{slug}' is already done")
        # QG-2: AC verification — each acceptance criterion must be verified
        if task.get("acceptance_criteria") and not force:
            if not ac_verified:
                raise ServiceError(
                    f"QG-2: '{slug}' cannot complete — acceptance criteria not verified. "
                    f"Verify each criterion, then: .frai/frai task done {slug} --ac-verified"
                )
            # QG-2 hardening: require verification evidence in task notes
            notes = task.get("notes") or ""
            ac_lines = [l.strip() for l in task["acceptance_criteria"].strip().splitlines() if l.strip()]
            if ac_lines and "AC verified" not in notes and "ac verified" not in notes.lower():
                raise ServiceError(
                    f"QG-2: '{slug}' has {len(ac_lines)} acceptance criteria but no verification "
                    f"evidence in task notes. Log verification first: "
                    f".frai/frai task log {slug} \"AC verified: 1. ... 2. ...\""
                )
        # plan completion gate
        if task.get("plan") and not force:
            try:
                steps = json.loads(task["plan"])
                total = len(steps)
                done_count = sum(1 for s in steps if s.get("done"))
                if done_count < total:
                    raise ServiceError(
                        f"Plan incomplete ({done_count}/{total} steps). "
                        f"Complete remaining steps with: .frai/frai task step {slug} N"
                    )
            except (json.JSONDecodeError, TypeError) as e:
                raise ServiceError(f"Corrupted plan data for task '{slug}': {e}")
        # QG-2 Implementation Gate: run quality gates (pytest, ruff, etc.)
        if not force and not os.environ.get("FRAI_SKIP_GATES"):
            try:
                from gate_runner import run_gates
                gate_passed, gate_results = run_gates("task-done", relevant_files)
                if gate_results:
                    summary = ", ".join(
                        r["name"] + "=" + ("PASS" if r["passed"] else "FAIL")
                        for r in gate_results
                    )
                    self.be.task_append_notes(slug, f"Gates: {summary}")
                if not gate_passed:
                    failed = [r for r in gate_results if not r["passed"] and r["severity"] == "block"]
                    details = "; ".join(f"{r['name']}: {r['output'][:100]}" for r in failed)
                    raise ServiceError(
                        f"QG-2 Implementation Gate: blocking gates failed for '{slug}'. "
                        f"Fix issues first: {details}"
                    )
            except ImportError:
                pass  # gate_runner not available
        from frai_utils import utcnow_iso
        updates: dict[str, Any] = {"status": "done", "completed_at": utcnow_iso()}
        if relevant_files:
            updates["relevant_files"] = json.dumps(relevant_files)
        # Atomic: task update + cascade + audit in one transaction
        self.be.begin_tx()
        try:
            self.be.task_update(slug, **updates)
            msgs = [f"Task '{slug}' completed."]
            if force:
                # Log gate bypass for compliance tracking
                self.be.task_append_notes(slug, "GATE BYPASS: --force used, QG-2 skipped")
                self.be._conn.execute(
                    "INSERT INTO events(entity_type,entity_id,action,details,created_at) "
                    "VALUES('task',?,'gate_bypass',?,?)",
                    (slug, '{"gate":"QG-2","reason":"--force"}', utcnow_iso()),
                )
                msgs.append("WARNING: --force used, gates bypassed.")
            msgs.extend(self._cascade_done(slug))
            self.be.commit_tx()
        except Exception:
            self.be.rollback_tx()
            raise
        return " ".join(msgs)

    def task_block(self, slug: str, reason: str | None = None) -> str:
        self._require_task(slug)
        from frai_utils import utcnow_iso
        updates: dict[str, Any] = {"status": "blocked", "blocked_at": utcnow_iso()}
        self.be.task_update(slug, **updates)
        if reason:
            self.be.task_append_notes(slug, f"BLOCKED: {reason}")
        return f"Task '{slug}' blocked."

    def task_unblock(self, slug: str) -> str:
        task = self._require_task(slug)
        if task["status"] != "blocked":
            raise ServiceError(f"Task '{slug}' is not blocked (status: {task['status']})")
        self.be.task_update(slug, status="active", blocked_at=None)
        return f"Task '{slug}' unblocked."

    def task_review(self, slug: str) -> str:
        self._require_task(slug)
        self.be.task_update(slug, status="review")
        return f"Task '{slug}' moved to review."

    def task_update(self, slug: str, **fields: Any) -> str:
        self._require_task(slug)
        if "status" in fields and fields["status"] not in VALID_TASK_STATUSES:
            raise ServiceError(f"Invalid status '{fields['status']}', must be one of {sorted(VALID_TASK_STATUSES)}")
        if "complexity" in fields and fields["complexity"] and fields["complexity"] not in VALID_COMPLEXITIES:
            raise ServiceError(f"Invalid complexity '{fields['complexity']}', must be one of {VALID_COMPLEXITIES}")
        if "stack" in fields and fields["stack"] and fields["stack"] not in VALID_STACKS:
            raise ServiceError(f"Invalid stack '{fields['stack']}', must be one of {sorted(VALID_STACKS)}")
        self.be.task_update(slug, **fields)
        return f"Task '{slug}' updated."

    def task_delete(self, slug: str) -> str:
        self._require_task(slug)
        self.be.task_delete(slug)
        return f"Task '{slug}' deleted."

    def task_plan(self, slug: str, steps: list[str]) -> str:
        if not steps:
            raise ServiceError("Plan must have at least one step")
        for i, s in enumerate(steps, 1):
            if not s or not s.strip():
                raise ServiceError(f"Plan step {i} is empty")
        self._require_task(slug)
        plan_data = [{"step": s, "done": False} for s in steps]
        self.be.task_update(slug, plan=json.dumps(plan_data))
        return f"Plan set for '{slug}' ({len(steps)} steps)."

    def task_step(self, slug: str, step_num: int) -> str:
        task = self._require_task(slug)
        if not task.get("plan"):
            raise ServiceError(f"Task '{slug}' has no plan")
        try:
            steps = json.loads(task["plan"])
        except (json.JSONDecodeError, TypeError) as e:
            raise ServiceError(f"Corrupted plan data for task '{slug}': {e}")
        if step_num < 1 or step_num > len(steps):
            raise ServiceError(f"Step {step_num} out of range (1-{len(steps)})")
        steps[step_num - 1]["done"] = True
        self.be.task_update(slug, plan=json.dumps(steps))
        done_count = sum(1 for s in steps if s.get("done"))
        return f"Step {step_num} done ({done_count}/{len(steps)})."

    def task_quick(self, title: str, goal: str | None = None,
                   role: str | None = None, stack: str | None = None) -> str:
        """Quick-create a task from minimal input (auto-slug, no story required)."""
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "task"
        if self.be.task_get(slug):
            suffix = os.urandom(3).hex()
            slug = f"{slug[:44]}-{suffix}"
        return self.task_add(None, slug, title, stack=stack, goal=goal, role=role)

    def task_next(self, agent_id: str | None = None) -> dict[str, Any] | None:
        """Pick the next available task: highest-score unclaimed planning task.

        QG-0 is enforced — only tasks with goal + AC can be started.
        Tasks without goal/AC are returned but NOT auto-started.
        """
        tasks = self.be.task_list(status="planning")
        candidates = [t for t in tasks if not t.get("claimed_by")]
        if not candidates:
            return None
        candidates.sort(key=lambda t: t.get("score") or 0, reverse=True)
        task = candidates[0]
        if agent_id:
            self.task_claim(task["slug"], agent_id)
            # QG-0 enforced: try without force, handle gracefully if gate fails
            try:
                self.task_start(task["slug"])
            except ServiceError:
                pass  # Task claimed but not started — agent must set goal/AC first
            task = self.be.task_get(task["slug"]) or task
        return task

    def task_claim(self, slug: str, agent_id: str) -> str:
        """Claim a task for an agent. Atomic UPDATE prevents race conditions."""
        self._require_task(slug)
        from frai_utils import utcnow_iso
        self.be.task_claim(slug, agent_id, utcnow_iso())
        return f"Task '{slug}' claimed by '{agent_id}'."

    def task_unclaim(self, slug: str) -> str:
        self._require_task(slug)
        self.be.task_update(slug, claimed_by=None)
        return f"Task '{slug}' unclaimed."

    def task_log(self, slug: str, message: str) -> str:
        """Append a timestamped log entry to task notes. Crash-safe journaling."""
        self._require_task(slug)
        validate_content("log message", message)
        self.be.task_append_notes(slug, message)
        return f"Logged to '{slug}'."

    def team_status(self) -> list[dict[str, Any]]:
        """Return tasks grouped by agent (claimed_by)."""
        tasks = self.be.task_list()
        agents: dict[str, list[dict[str, Any]]] = {}
        for t in tasks:
            agent = t.get("claimed_by") or "(unclaimed)"
            if t["status"] != "done":
                agents.setdefault(agent, []).append(t)
        return [{"agent": a, "tasks": ts} for a, ts in agents.items()]

    def task_move(self, slug: str, new_story_slug: str) -> str:
        self._require_task(slug)
        story = self._require_story(new_story_slug)
        self.be.task_update(slug, story_id=story["id"])
        return f"Task '{slug}' moved to story '{new_story_slug}'."

    def _cascade_start(self, task_slug: str) -> None:
        """Auto-start parent story and epic when first task starts."""
        task = self.be.task_get_full(task_slug)
        if not task:
            return
        if task.get("story_slug"):
            story = self.be.story_get(task["story_slug"])
            if story and story["status"] == "open":
                self.be.story_update(story["slug"], status="active")
            if task.get("epic_slug"):
                epic = self.be.epic_get(task["epic_slug"])
                if epic and epic["status"] not in ("active", "done"):
                    self.be.epic_update(task["epic_slug"], status="active")

    def _cascade_done(self, task_slug: str) -> list[str]:
        """Auto-close parent story/epic if all tasks done."""
        msgs: list[str] = []
        task = self.be.task_get_full(task_slug)
        if not task or not task.get("story_slug"):
            return msgs
        remaining = self.be.story_active_task_count(task["story_slug"])
        if remaining == 0:
            self.be.story_update(task["story_slug"], status="done")
            msgs.append(f"Story '{task['story_slug']}' auto-closed.")
            if task.get("epic_slug"):
                undone = self.be.epic_undone_story_count(task["epic_slug"])
                if undone == 0:
                    self.be.epic_update(task["epic_slug"], status="done")
                    msgs.append(f"Epic '{task['epic_slug']}' auto-closed.")
        return msgs
