"""Jira MCP tool definitions."""

TOOLS = [
    # --- Health ---
    {
        "name": "jira_health",
        "description": "Health check — verify Jira connection.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },

    # --- Issues ---
    {
        "name": "jira_search",
        "description": "Search issues by JQL query.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "jql": {"type": "string", "description": "JQL query (e.g. 'project = HYS AND status = \"In Progress\"')"},
                "max_results": {"type": "integer", "description": "Max results (default: 50)"},
            },
            "required": ["jql"],
        },
    },
    {
        "name": "jira_get_issue",
        "description": "Get detailed info about a specific issue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Issue key (e.g. HYS-127)"},
            },
            "required": ["issue_key"],
        },
    },
    {
        "name": "jira_create_issue",
        "description": "Create a new Jira issue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "Project key (e.g. HYS)"},
                "summary": {"type": "string", "description": "Issue title"},
                "description": {"type": "string", "description": "Issue description"},
                "issue_type": {"type": "string", "description": "Issue type name (e.g. Задача, Bug, Story)"},
                "components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Component names",
                },
                "priority": {"type": "string", "description": "Priority name (e.g. High, Medium, Low)"},
                "estimate": {"type": "string", "description": "Original estimate (e.g. '2h', '1h 30m')"},
                "epic_link": {"type": "string", "description": "Epic issue key (e.g. HYS-95)"},
                "epic_name": {"type": "string", "description": "Epic Name (required when creating Epic issue type)"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels",
                },
                "fix_version": {"type": "string", "description": "Fix version name"},
                "additional_fields": {
                    "type": "object",
                    "description": "Any additional fields as key-value pairs",
                },
            },
            "required": ["project_key", "summary", "issue_type"],
        },
    },
    {
        "name": "jira_update_issue",
        "description": "Update fields of an existing issue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Issue key (e.g. HYS-127)"},
                "summary": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "additional_fields": {
                    "type": "object",
                    "description": "Any additional fields to update",
                },
            },
            "required": ["issue_key"],
        },
    },
    {
        "name": "jira_transition_issue",
        "description": "Transition an issue to a new status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Issue key (e.g. HYS-127)"},
                "transition_id": {"type": "string", "description": "Transition ID (use jira_get_transitions to find)"},
            },
            "required": ["issue_key", "transition_id"],
        },
    },
    {
        "name": "jira_get_transitions",
        "description": "Get available transitions for an issue (to find valid transition IDs).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Issue key (e.g. HYS-127)"},
            },
            "required": ["issue_key"],
        },
    },
    {
        "name": "jira_add_comment",
        "description": "Add a comment to an issue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Issue key (e.g. HYS-127)"},
                "body": {"type": "string", "description": "Comment body (Jira wiki markup)"},
            },
            "required": ["issue_key", "body"],
        },
    },
    {
        "name": "jira_add_worklog",
        "description": "Log time spent on an issue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Issue key (e.g. HYS-127)"},
                "time_spent": {"type": "string", "description": "Time spent (e.g. '1h', '30m', '1h 30m')"},
                "comment": {"type": "string", "description": "Work description"},
            },
            "required": ["issue_key", "time_spent"],
        },
    },

    # --- Sync with frai ---
    {
        "name": "jira_sync_push",
        "description": "Push all frai tasks to Jira (create or update). Maps frai status to Jira transitions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "Jira project key"},
                "issue_type": {"type": "string", "description": "Default issue type (default: Задача)"},
            },
            "required": ["project_key"],
        },
    },
    {
        "name": "jira_sync_push_task",
        "description": "Push a single frai task to Jira.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string", "description": "frai task slug"},
                "project_key": {"type": "string", "description": "Jira project key"},
                "issue_type": {"type": "string", "description": "Issue type (default: Задача)"},
            },
            "required": ["slug", "project_key"],
        },
    },
    {
        "name": "jira_sync_pull",
        "description": "Pull status updates from Jira into frai tasks.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "jira_sync_status",
        "description": "Show sync mapping between frai tasks and Jira issues.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]
