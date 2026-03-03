"""Link issues tool — create relationships between Jira issues."""

from typing import Any
from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
import json


LINK_ISSUES_TOOL = Tool(
    name="link_issues",
    description="""Create a link between two Jira issues.

Use this to express relationships such as "blocks", "is blocked by",
"duplicates", "relates to", "clones", etc.

Common link types (the name is case-sensitive and must match your Jira config):
- Blocks      — outward "blocks" / inward "is blocked by"
- Cloners     — outward "clones" / inward "is cloned by"
- Duplicate   — outward "duplicates" / inward "is duplicated by"
- Relates     — outward "relates to" / inward "relates to"

The *outward* issue is the "from" side (e.g. the one that blocks),
and the *inward* issue is the "to" side (e.g. the one that is blocked).

Example: to say PROJ-1 blocks PROJ-2, set outward_issue=PROJ-1 and
inward_issue=PROJ-2 with link_type="Blocks".""",
    inputSchema={
        "type": "object",
        "properties": {
            "inward_issue": {
                "type": "string",
                "description": "Issue key for the inward (target) side of the link (e.g. 'PROJ-2')",
            },
            "outward_issue": {
                "type": "string",
                "description": "Issue key for the outward (source) side of the link (e.g. 'PROJ-1')",
            },
            "link_type": {
                "type": "string",
                "description": "Name of the link type (e.g. 'Blocks', 'Duplicate', 'Relates'). Default: 'Relates'",
                "default": "Relates",
            },
            "comment": {
                "type": "string",
                "description": "Optional comment added to the outward (from) issue when creating the link",
            },
        },
        "required": ["inward_issue", "outward_issue"],
    },
)


async def handle_link_issues(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle link_issues tool call."""
    inward_issue = arguments["inward_issue"]
    outward_issue = arguments["outward_issue"]
    link_type = arguments.get("link_type", "Relates")
    comment = arguments.get("comment")

    await jira_client.link_issues(
        inward_issue=inward_issue,
        outward_issue=outward_issue,
        link_type=link_type,
        comment=comment,
    )

    response = {
        "success": True,
        "link_type": link_type,
        "outward_issue": outward_issue,
        "inward_issue": inward_issue,
        "message": f"{outward_issue} now '{link_type}' {inward_issue}",
    }

    if comment:
        response["comment"] = comment

    return [TextContent(type="text", text=json.dumps(response, indent=2))]
