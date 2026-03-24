"""Bitrix24 REST API client — zero dependencies."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError


STATUS_NAME_TO_ID = {
    "new": 2,
    "in_progress": 3,
    "completed": 5,
    "deferred": 6,
}

STATUS_ID_TO_NAME = {v: k for k, v in STATUS_NAME_TO_ID.items()}

COMPLEXITY_TO_SP = {"simple": 1, "medium": 3, "complex": 8}


class BitrixClient:
    """Lightweight Bitrix24 REST API client over webhook."""

    def __init__(self, webhook_url: str, group_id: int = 297):
        self.webhook_url = webhook_url.rstrip("/")
        self.group_id = group_id

    def call(self, method: str, params: dict | None = None) -> dict:
        url = f"{self.webhook_url}/{method}.json"
        data = json.dumps(params or {}).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Bitrix24 API error {e.code}: {body[:300]}")

    # --- Health ---

    def health(self) -> str:
        result = self.call("app.info")
        return f"Connected. Group ID: {self.group_id}"

    # --- Epics ---

    def epic_list(self) -> list[dict]:
        result = self.call("tasks.api.scrum.epic.list", {
            "filter": {"GROUP_ID": self.group_id},
        })
        return result.get("result", [])

    def epic_add(self, name: str, description: str = "", color: str = "#69dadb") -> int:
        result = self.call("tasks.api.scrum.epic.add", {
            "fields": {
                "groupId": self.group_id,
                "name": name,
                "description": description,
                "color": color,
            }
        })
        return result.get("result", {}).get("id", 0)

    def epic_update(self, epic_id: int, **fields) -> None:
        self.call("tasks.api.scrum.epic.update", {
            "id": epic_id,
            "fields": fields,
        })

    # --- Tasks ---

    def task_list(self, status: str = "all", limit: int = 50) -> list[dict]:
        params: dict = {
            "filter": {"GROUP_ID": self.group_id},
            "select": ["ID", "TITLE", "STATUS", "TAGS", "RESPONSIBLE_ID", "DESCRIPTION"],
            "limit": limit,
        }
        if status != "all" and status in STATUS_NAME_TO_ID:
            params["filter"]["STATUS"] = STATUS_NAME_TO_ID[status]
        result = self.call("tasks.task.list", params)
        return result.get("result", {}).get("tasks", [])

    def task_add(self, title: str, description: str = "",
                 epic_id: int = 0, story_points: int = 0,
                 tags: list[str] | None = None,
                 responsible_id: int = 0) -> int:
        fields: dict = {
            "TITLE": title,
            "DESCRIPTION": description,
            "GROUP_ID": self.group_id,
        }
        if tags:
            fields["TAGS"] = tags
        if responsible_id:
            fields["RESPONSIBLE_ID"] = responsible_id

        result = self.call("tasks.task.add", {"fields": fields})
        task_id = result.get("result", {}).get("task", {}).get("id", 0)

        if task_id and (epic_id or story_points):
            scrum_fields: dict = {}
            if epic_id:
                scrum_fields["epicId"] = epic_id
            if story_points:
                scrum_fields["storyPoints"] = story_points
            self.call("tasks.api.scrum.task.update", {
                "id": task_id,
                "fields": scrum_fields,
            })

        return task_id

    def task_get(self, task_id: int) -> dict:
        result = self.call("tasks.task.get", {"taskId": task_id})
        return result.get("result", {}).get("task", {})

    def task_update(self, task_id: int, **fields) -> None:
        b24_fields: dict = {}
        if "title" in fields:
            b24_fields["TITLE"] = fields["title"]
        if "description" in fields:
            b24_fields["DESCRIPTION"] = fields["description"]
        if "status" in fields and fields["status"] in STATUS_NAME_TO_ID:
            b24_fields["STATUS"] = STATUS_NAME_TO_ID[fields["status"]]

        if b24_fields:
            self.call("tasks.task.update", {"taskId": task_id, "fields": b24_fields})

        scrum_fields: dict = {}
        if "story_points" in fields:
            scrum_fields["storyPoints"] = fields["story_points"]
        if "epic_id" in fields:
            scrum_fields["epicId"] = fields["epic_id"]
        if scrum_fields:
            self.call("tasks.api.scrum.task.update", {
                "id": task_id, "fields": scrum_fields,
            })

    def task_complete(self, task_id: int) -> None:
        self.call("tasks.task.update", {
            "taskId": task_id,
            "fields": {"STATUS": 5},
        })

    # --- Sprints ---

    def sprint_list(self) -> list[dict]:
        result = self.call("tasks.api.scrum.sprint.list", {
            "filter": {"GROUP_ID": self.group_id},
        })
        return result.get("result", [])

    def sprint_add(self, name: str, date_start: str, date_end: str,
                   status: str = "planned") -> int:
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=3))  # Moscow
        ds = datetime.strptime(date_start, "%Y-%m-%d").replace(hour=0, minute=0, tzinfo=tz)
        de = datetime.strptime(date_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=tz)
        result = self.call("tasks.api.scrum.sprint.add", {
            "fields": {
                "groupId": self.group_id,
                "name": name,
                "dateStart": ds.isoformat(),
                "dateEnd": de.isoformat(),
                "status": status,
                "createdBy": 49749,
            }
        })
        return result.get("result", {}).get("id", 0) if isinstance(result.get("result"), dict) else result.get("result", 0)

    def sprint_start(self, sprint_id: int) -> None:
        self.call("tasks.api.scrum.sprint.update", {
            "id": sprint_id,
            "fields": {"status": "active"},
        })

    def sprint_complete(self, sprint_id: int) -> None:
        self.call("tasks.api.scrum.sprint.complete", {"id": sprint_id})

    def sprint_get(self, sprint_id: int) -> dict:
        result = self.call("tasks.api.scrum.sprint.get", {"id": sprint_id})
        return result.get("result", {})

    def task_move_to_sprint(self, task_id: int, sprint_id: int) -> None:
        self.call("tasks.api.scrum.task.update", {
            "id": task_id,
            "fields": {"sprintId": sprint_id},
        })

    # --- Backlog ---

    def backlog_get(self) -> dict:
        result = self.call("tasks.api.scrum.backlog.get", {
            "filter": {"GROUP_ID": self.group_id},
        })
        return result.get("result", {})


def _read_mcp_config(project_dir: str | None = None) -> dict:
    """Read bitrix24 config from .mcp.json env block."""
    if not project_dir:
        return {}
    mcp_path = os.path.join(project_dir, ".mcp.json")
    if not os.path.exists(mcp_path):
        return {}
    try:
        with open(mcp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("mcpServers", {}).get("bitrix24", {}).get("env", {})
    except Exception:
        return {}


def get_client(project_dir: str | None = None) -> BitrixClient:
    """Create client. Priority: .mcp.json env > environment variables."""
    mcp_env = _read_mcp_config(project_dir)

    webhook_url = (
        mcp_env.get("BITRIX24_WEBHOOK_URL")
        or os.environ.get("BITRIX24_WEBHOOK_URL", "")
    )
    if not webhook_url:
        raise RuntimeError(
            "BITRIX24_WEBHOOK_URL not set. "
            "Add to .mcp.json: \"bitrix24\": { \"env\": { \"BITRIX24_WEBHOOK_URL\": \"...\" } } "
            "or set environment variable."
        )
    group_id = int(
        mcp_env.get("BITRIX24_SCRUM_GROUP_ID")
        or os.environ.get("BITRIX24_SCRUM_GROUP_ID", "297")
    )
    return BitrixClient(webhook_url, group_id)
