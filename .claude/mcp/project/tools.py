"""Frai MCP tool definitions — JSON schemas for all project tools."""

from __future__ import annotations

TOOLS = [
    # === Health ===
    {
        "name": "frai_health",
        "description": "Health check — version, DB status, table count. Use to verify server is alive.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # === Core: task + session + status ===
    {
        "name": "frai_status",
        "description": "Get project status: task counts, active session, epics",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "frai_task_list",
        "description": "List tasks with optional filters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status (comma-separated): planning,active,blocked,review,done"},
                "story": {"type": "string", "description": "Filter by story slug"},
                "epic": {"type": "string", "description": "Filter by epic slug"},
                "role": {"type": "string", "description": "Filter by role"},
                "stack": {"type": "string", "description": "Filter by stack"},
            },
        },
    },
    {
        "name": "frai_task_show",
        "description": "Show full task details including plan steps and decisions",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_add",
        "description": "Create a new task (optionally in a story)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "story_slug": {"type": "string", "description": "Parent story slug (optional)"},
                "slug": {"type": "string"},
                "title": {"type": "string"},
                "goal": {"type": "string"},
                "role": {"type": "string", "description": "Free-text role (e.g. developer, architect, qa)"},
                "complexity": {"type": "string", "enum": ["simple", "medium", "complex"]},
                "stack": {"type": "string"},
            },
            "required": ["slug", "title"],
        },
    },
    {
        "name": "frai_task_start",
        "description": "Start working on a task (sets status to active)",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_done",
        "description": "Complete a task. Auto-closes parent story/epic if all tasks done",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "force": {"type": "boolean", "description": "Skip plan completion check"},
                "relevant_files": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_block",
        "description": "Block a task with optional reason",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_unblock",
        "description": "Unblock a task (sets status back to active)",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_update",
        "description": "Update task fields (title, goal, notes, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "title": {"type": "string"},
                "goal": {"type": "string"},
                "notes": {"type": "string"},
                "acceptance_criteria": {"type": "string"},
                "stack": {"type": "string"},
                "complexity": {"type": "string", "enum": ["simple", "medium", "complex"]},
                "role": {"type": "string", "description": "Free-text role"},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_plan",
        "description": "Set plan steps for a task",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "steps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["slug", "steps"],
        },
    },
    {
        "name": "frai_task_step",
        "description": "Mark a plan step as done",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "step_num": {"type": "integer", "description": "Step number (1-based)"},
            },
            "required": ["slug", "step_num"],
        },
    },
    {
        "name": "frai_task_delete",
        "description": "Delete a task",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_review",
        "description": "Set task status to review",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_task_move",
        "description": "Move task to a different story",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "new_story_slug": {"type": "string"},
            },
            "required": ["slug", "new_story_slug"],
        },
    },
    {
        "name": "frai_task_log",
        "description": "Append a timestamped log entry to task notes. Use for continuous journaling — crash-safe progress tracking",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "message": {"type": "string", "description": "Log message (appended with timestamp)"},
            },
            "required": ["slug", "message"],
        },
    },
    {
        "name": "frai_task_claim",
        "description": "Claim a task for an agent (prevents double-claiming)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "agent_id": {"type": "string"},
            },
            "required": ["slug", "agent_id"],
        },
    },
    {
        "name": "frai_task_unclaim",
        "description": "Release task claim",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_session_current",
        "description": "Get current active session",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "frai_session_list",
        "description": "List recent sessions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results (default 10)"},
            },
        },
    },
    {
        "name": "frai_session_start",
        "description": "Start a new work session",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "frai_session_end",
        "description": "End the current session with optional summary",
        "inputSchema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Session summary"},
            },
        },
    },
    {
        "name": "frai_session_handoff",
        "description": "Save handoff data for session continuity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "handoff": {"type": "object", "description": "Handoff data (what was done, next steps, blockers)"},
            },
            "required": ["handoff"],
        },
    },
    {
        "name": "frai_session_last_handoff",
        "description": "Get last session's handoff data",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # === Hierarchy: epic, story, roadmap ===
    {
        "name": "frai_epic_add",
        "description": "Create a new epic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["slug", "title"],
        },
    },
    {
        "name": "frai_epic_list",
        "description": "List all epics",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "frai_epic_done",
        "description": "Mark epic as done",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_epic_delete",
        "description": "Delete an epic (cascades to stories and tasks)",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_story_done",
        "description": "Mark story as done",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_story_delete",
        "description": "Delete a story (cascades to tasks)",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "frai_story_add",
        "description": "Create a new story in an epic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "epic_slug": {"type": "string"},
                "slug": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["epic_slug", "slug", "title"],
        },
    },
    {
        "name": "frai_story_list",
        "description": "List stories, optionally filtered by epic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "epic_slug": {"type": "string", "description": "Filter by epic slug"},
            },
        },
    },
    {
        "name": "frai_roadmap",
        "description": "Full project roadmap: epics → stories → tasks tree",
        "inputSchema": {
            "type": "object",
            "properties": {
                "include_done": {"type": "boolean", "description": "Include done items"},
            },
        },
    },
    # === Knowledge: memory, decisions, search ===
    {
        "name": "frai_memory_add",
        "description": "Save project memory (pattern, gotcha, convention, context)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["pattern", "gotcha", "convention", "context"]},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "task_slug": {"type": "string"},
            },
            "required": ["type", "title", "content"],
        },
    },
    {
        "name": "frai_memory_search",
        "description": "Search project memory via FTS5",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "frai_memory_list",
        "description": "List project memories, optionally filtered by type",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["pattern", "gotcha", "convention", "context"]},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "frai_memory_show",
        "description": "Show a specific memory by ID",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    },
    {
        "name": "frai_memory_delete",
        "description": "Delete a memory by ID",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    },
    # === Graph Memory ===
    {
        "name": "frai_memory_link",
        "description": "Create a graph edge between two memory/decision nodes (Graphiti-inspired). Relations: supersedes, caused_by, relates_to, contradicts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_type": {"type": "string", "enum": ["memory", "decision"]},
                "source_id": {"type": "integer"},
                "target_type": {"type": "string", "enum": ["memory", "decision"]},
                "target_id": {"type": "integer"},
                "relation": {"type": "string", "enum": ["supersedes", "caused_by", "relates_to", "contradicts"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1, "default": 1.0},
                "created_by": {"type": "string"},
            },
            "required": ["source_type", "source_id", "target_type", "target_id", "relation"],
        },
    },
    {
        "name": "frai_memory_unlink",
        "description": "Soft-invalidate a graph edge (never deletes — Graphiti approach)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "edge_id": {"type": "integer"},
                "replacement_id": {"type": "integer"},
            },
            "required": ["edge_id"],
        },
    },
    {
        "name": "frai_memory_related",
        "description": "Find related nodes via graph traversal (1-3 hops)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_type": {"type": "string", "enum": ["memory", "decision"]},
                "node_id": {"type": "integer"},
                "max_hops": {"type": "integer", "minimum": 1, "maximum": 3, "default": 2},
                "include_invalid": {"type": "boolean", "default": False},
            },
            "required": ["node_type", "node_id"],
        },
    },
    {
        "name": "frai_memory_graph",
        "description": "List graph edges with optional filters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_type": {"type": "string", "enum": ["memory", "decision"]},
                "node_id": {"type": "integer"},
                "relation": {"type": "string", "enum": ["supersedes", "caused_by", "relates_to", "contradicts"]},
                "include_invalid": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "frai_decide",
        "description": "Record an architectural decision with rationale",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision": {"type": "string"},
                "rationale": {"type": "string"},
                "task_slug": {"type": "string"},
            },
            "required": ["decision"],
        },
    },
    {
        "name": "frai_decisions_list",
        "description": "List recent decisions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
        },
    },
    {
        "name": "frai_task_quick",
        "description": "Quick-create a task with auto-generated slug",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "goal": {"type": "string"},
                "role": {"type": "string"},
                "stack": {"type": "string"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "frai_task_next",
        "description": "Pick next available planning task. With agent_id, auto-claim and start it",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent ID to auto-claim the task"},
            },
        },
    },
    {
        "name": "frai_team",
        "description": "Team status — tasks grouped by agent",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "frai_search",
        "description": "Full-text search across all project data (tasks, memory, decisions)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "scope": {"type": "string", "enum": ["all", "tasks", "memory", "decisions"]},
            },
            "required": ["query"],
        },
    },
    {
        "name": "frai_metrics",
        "description": "Project metrics: completion %, velocity, session hours",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "frai_events",
        "description": "Audit event log — who changed what when",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_type": {"type": "string"},
                "entity_id": {"type": "string"},
                "limit": {"type": "integer"},
            },
        },
    },
]
