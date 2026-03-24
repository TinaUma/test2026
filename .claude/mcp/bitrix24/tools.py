"""Bitrix24 Scrum MCP tool definitions."""

TOOLS = [
    # --- Health ---
    {
        "name": "b24_health",
        "description": "Health check — verify Bitrix24 connection and Scrum group access.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },

    # --- Epics ---
    {
        "name": "b24_epic_list",
        "description": "List all Scrum epics in the project.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "b24_epic_add",
        "description": "Create a new Scrum epic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Epic name"},
                "description": {"type": "string", "description": "Epic description"},
                "color": {"type": "string", "description": "HEX color (default: #69dadb)"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "b24_epic_update",
        "description": "Update an existing Scrum epic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Bitrix24 epic ID"},
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["id"],
        },
    },

    # --- Tasks ---
    {
        "name": "b24_task_list",
        "description": "List tasks in the Scrum project. Optional filter by status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter: new, in_progress, completed, deferred, all (default: all)",
                },
                "limit": {"type": "integer", "description": "Max results (default: 50)"},
            },
        },
    },
    {
        "name": "b24_task_add",
        "description": "Create a task in Scrum backlog.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task description"},
                "epic_id": {"type": "integer", "description": "Attach to epic (Bitrix24 epic ID)"},
                "story_points": {"type": "integer", "description": "Story points (1,2,3,5,8,13)"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for the task",
                },
                "responsible_id": {"type": "integer", "description": "Responsible user ID in Bitrix24"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "b24_task_get",
        "description": "Get detailed info about a specific task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Bitrix24 task ID"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "b24_task_update",
        "description": "Update task fields (title, description, status, story points).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Bitrix24 task ID"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {
                    "type": "string",
                    "description": "new, in_progress, completed, deferred",
                },
                "story_points": {"type": "integer"},
                "epic_id": {"type": "integer", "description": "Attach to epic"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "b24_task_complete",
        "description": "Mark a task as completed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Bitrix24 task ID"},
            },
            "required": ["task_id"],
        },
    },

    # --- Sprints ---
    {
        "name": "b24_sprint_list",
        "description": "List all sprints (active, planned, completed).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "b24_sprint_add",
        "description": "Create a new sprint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Sprint name"},
                "date_start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "date_end": {"type": "string", "description": "End date (YYYY-MM-DD)"},
            },
            "required": ["name", "date_start", "date_end"],
        },
    },
    {
        "name": "b24_sprint_start",
        "description": "Start (activate) a planned sprint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {"type": "integer", "description": "Sprint ID"},
            },
            "required": ["sprint_id"],
        },
    },
    {
        "name": "b24_sprint_complete",
        "description": "Complete a sprint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {"type": "integer", "description": "Sprint ID"},
            },
            "required": ["sprint_id"],
        },
    },
    {
        "name": "b24_sprint_get",
        "description": "Get sprint details with tasks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {"type": "integer", "description": "Sprint ID"},
            },
            "required": ["sprint_id"],
        },
    },
    {
        "name": "b24_task_move_to_sprint",
        "description": "Move a task to a sprint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Bitrix24 task ID"},
                "sprint_id": {"type": "integer", "description": "Sprint ID"},
            },
            "required": ["task_id", "sprint_id"],
        },
    },

    # --- Backlog ---
    {
        "name": "b24_backlog",
        "description": "Get current Scrum backlog (unassigned to sprint).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },

    # --- Sync with frai ---
    {
        "name": "b24_sync_push",
        "description": "Push all frai epics and tasks to Bitrix24 Scrum backlog.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "b24_sync_push_task",
        "description": "Push a single frai task to Bitrix24.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string", "description": "frai task slug"},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "b24_sync_pull",
        "description": "Pull status updates from Bitrix24 into frai.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "b24_sync_status",
        "description": "Show sync mapping between frai and Bitrix24.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]
