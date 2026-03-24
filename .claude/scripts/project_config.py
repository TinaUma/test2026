"""Frai config loader — find .frai/ dir, create service, gates config."""

from __future__ import annotations

import json
import os
import sys

from project_backend import SQLiteBackend
from project_service import ProjectService

# Data lives in .frai/ (IDE-agnostic)
FRAI_DIR = ".frai"
DB_NAME = "frai.db"
CONFIG_NAME = "config.json"

# --- Gate defaults ---

VALID_GATE_SEVERITIES = frozenset({"warn", "block"})
VALID_GATE_TRIGGERS = frozenset({"task-done", "commit", "review"})

# --- SENAR Rule 9.2: Session duration limit (minutes) ---
DEFAULT_SESSION_MAX_MINUTES = 120

DEFAULT_GATES: dict[str, dict] = {
    "pytest": {
        "enabled": True,
        "severity": "block",
        "trigger": ["task-done", "review"],
        "command": "pytest tests/ -x -q",
        "description": "Run pytest before task completion",
    },
    "ruff": {
        "enabled": True,
        "severity": "block",
        "trigger": ["commit"],
        "command": "ruff check {files}",
        "description": "Lint with ruff before commit",
    },
    "mypy": {
        "enabled": False,
        "severity": "warn",
        "trigger": ["commit"],
        "command": "mypy {files}",
        "description": "Type-check with mypy before commit",
    },
    "filesize": {
        "enabled": True,
        "severity": "warn",
        "trigger": ["task-done", "commit"],
        "command": None,
        "description": "Warn if files exceed max_lines threshold",
        "max_lines": 400,
    },
    "bandit": {
        "enabled": False,
        "severity": "warn",
        "trigger": ["review"],
        "command": "bandit -r {files} -q",
        "description": "Security scan with bandit",
    },
}


def find_frai_dir() -> str:
    """Find .frai/ directory, searching up from cwd. Env override: FRAI_DIR."""
    override = os.environ.get("FRAI_DIR")
    if override:
        return override
    d = os.getcwd()
    for _ in range(10):
        candidate = os.path.join(d, FRAI_DIR)
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    # Default to cwd
    return os.path.join(os.getcwd(), FRAI_DIR)


def get_db_path() -> str:
    return os.path.join(find_frai_dir(), DB_NAME)


def get_config_path() -> str:
    return os.path.join(find_frai_dir(), CONFIG_NAME)


def load_config() -> dict:
    path = get_config_path()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict) -> None:
    path = get_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_gates(cfg: dict | None = None) -> dict[str, dict]:
    """Load gates config: merge user overrides on top of defaults.

    Returns dict of gate_name -> gate_config.
    User can override any field per gate in config.json under "gates" key.
    """
    if cfg is None:
        cfg = load_config()
    user_gates = cfg.get("gates", {})
    merged: dict[str, dict] = {}
    # Start with defaults
    for name, defaults in DEFAULT_GATES.items():
        gate = dict(defaults)
        if name in user_gates:
            gate.update(user_gates[name])
        merged[name] = gate
    # Add custom user gates (not in defaults)
    for name, ucfg in user_gates.items():
        if name not in merged:
            merged[name] = ucfg
    return merged


def get_gates_for_trigger(trigger: str, cfg: dict | None = None) -> list[dict]:
    """Return enabled gates matching a specific trigger.

    Each returned dict includes a 'name' key.
    """
    all_gates = load_gates(cfg)
    result = []
    for name, gate in all_gates.items():
        if not gate.get("enabled", True):
            continue
        triggers = gate.get("trigger", [])
        if trigger in triggers:
            result.append({**gate, "name": name})
    return result


def get_service() -> ProjectService:
    """Create ProjectService with SQLite backend."""
    db_path = get_db_path()
    be = SQLiteBackend(db_path)
    return ProjectService(be)
