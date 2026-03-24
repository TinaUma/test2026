"""Jira REST API client — zero dependencies (stdlib only).

Supports both Jira Cloud (Atlassian) and Jira Server/Data Center.
Auth: PAT token (Bearer) or Basic (user:password).
"""

from __future__ import annotations

import base64
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class JiraClient:
    """Lightweight Jira REST API client."""

    def __init__(self, base_url: str, auth_header: str):
        self.base_url = base_url.rstrip("/")
        self.auth_header = auth_header

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        url = f"{self.base_url}/rest/api/2/{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        req = Request(url, data=body, method=method, headers={
            "Authorization": self.auth_header,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        })
        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Jira API {e.code}: {body_text[:500]}")

    def get(self, path: str) -> dict:
        return self._request("GET", path)

    def post(self, path: str, data: dict) -> dict:
        return self._request("POST", path, data)

    def put(self, path: str, data: dict) -> dict:
        return self._request("PUT", path, data)

    # --- Health ---

    def health(self) -> str:
        info = self.get("serverInfo")
        return f"Connected to {info.get('serverTitle', '?')} ({info.get('version', '?')})"

    # --- Issues ---

    def search(self, jql: str, max_results: int = 50, fields: str = "*navigable") -> dict:
        return self.post("search", {
            "jql": jql,
            "maxResults": max_results,
            "fields": fields.split(",") if isinstance(fields, str) else fields,
        })

    def get_issue(self, issue_key: str) -> dict:
        return self.get(f"issue/{issue_key}")

    def create_issue(self, fields: dict) -> dict:
        return self.post("issue", {"fields": fields})

    def update_issue(self, issue_key: str, fields: dict) -> dict:
        return self.put(f"issue/{issue_key}", {"fields": fields})

    def transition_issue(self, issue_key: str, transition_id: str) -> dict:
        return self.post(f"issue/{issue_key}/transitions", {
            "transition": {"id": transition_id},
        })

    def get_transitions(self, issue_key: str) -> list[dict]:
        result = self.get(f"issue/{issue_key}/transitions")
        return result.get("transitions", [])

    def add_comment(self, issue_key: str, body: str) -> dict:
        return self.post(f"issue/{issue_key}/comment", {"body": body})

    def add_worklog(self, issue_key: str, time_spent: str, comment: str = "") -> dict:
        data: dict = {"timeSpent": time_spent}
        if comment:
            data["comment"] = comment
        return self.post(f"issue/{issue_key}/worklog", data)

    # --- Projects ---

    def get_project(self, project_key: str) -> dict:
        return self.get(f"project/{project_key}")

    def list_projects(self) -> list[dict]:
        return self.get("project")  # type: ignore[return-value]


def _read_mcp_config(project_dir: str | None = None) -> dict:
    """Read jira config from .mcp.json env block."""
    if not project_dir:
        return {}
    mcp_path = os.path.join(project_dir, ".mcp.json")
    if not os.path.exists(mcp_path):
        return {}
    try:
        with open(mcp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("mcpServers", {}).get("jira", {}).get("env", {})
    except Exception:
        return {}


def get_client(project_dir: str | None = None) -> JiraClient:
    """Create client. Priority: .mcp.json env > environment variables.

    Env vars:
        JIRA_URL           — Jira base URL (e.g. https://jira.example.com)
        JIRA_TOKEN         — PAT token (Bearer auth, Jira Server/DC)
        JIRA_USER          — Username for Basic auth (Jira Cloud)
        JIRA_PASSWORD      — API token/password for Basic auth
    """
    mcp_env = _read_mcp_config(project_dir)

    base_url = mcp_env.get("JIRA_URL") or os.environ.get("JIRA_URL", "")
    if not base_url:
        raise RuntimeError(
            "JIRA_URL not set. Add to .mcp.json env block or set environment variable."
        )

    # PAT token (Bearer) — Jira Server/DC
    token = mcp_env.get("JIRA_TOKEN") or os.environ.get("JIRA_TOKEN", "")
    if token:
        return JiraClient(base_url, f"Bearer {token}")

    # Basic auth — Jira Cloud (user + API token)
    user = mcp_env.get("JIRA_USER") or os.environ.get("JIRA_USER", "")
    password = mcp_env.get("JIRA_PASSWORD") or os.environ.get("JIRA_PASSWORD", "")
    if user and password:
        creds = base64.b64encode(f"{user}:{password}".encode()).decode()
        return JiraClient(base_url, f"Basic {creds}")

    raise RuntimeError(
        "Jira auth not configured. Set JIRA_TOKEN (Bearer) or JIRA_USER+JIRA_PASSWORD (Basic)."
    )
