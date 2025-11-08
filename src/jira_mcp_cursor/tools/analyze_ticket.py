"""Analyze ticket tool."""

from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
import json
import re
from typing import Any

# Regex patterns for extracting structured data from ticket descriptions
# Pattern: Match markdown headers (1-3 levels) for Requirements section
REQUIREMENTS_SECTION_PATTERN = re.compile(
    r"(?:^|\n)#{1,3}\s*(?:Requirements?|Required Features?)\s*\n(.*?)(?:\n#{1,3}|$)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# Pattern: Match markdown headers for Acceptance Criteria section
AC_SECTION_PATTERN = re.compile(
    r"(?:^|\n)#{1,3}\s*(?:Acceptance Criteria|AC|Definition of Done)\s*\n(.*?)(?:\n#{1,3}|$)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# Pattern: Match markdown headers for Technical Notes section
TECH_SECTION_PATTERN = re.compile(
    r"(?:^|\n)#{1,3}\s*(?:Technical Notes?|Implementation Notes?|Tech Details?)\s*\n(.*?)(?:\n#{1,3}|$)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# Pattern: Match markdown headers for Dependencies section
DEP_SECTION_PATTERN = re.compile(
    r"(?:^|\n)#{1,3}\s*(?:Dependencies?|Depends On|Related Tickets?)\s*\n(.*?)(?:\n#{1,3}|$)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# Pattern: Match Jira ticket keys (e.g., PROJ-123, ABC-456)
TICKET_KEY_PATTERN = re.compile(r"\b([A-Z]+-\d+)\b")

# Pattern: Match markdown bullet points (-, *, •)
BULLET_POINT_PATTERN = re.compile(r"(?:^|\n)\s*[-*•]\s*(.+)")

# Pattern: Match numbered list items (1., 2), 3.)
NUMBERED_LIST_PATTERN = re.compile(r"(?:^|\n)\s*\d+[\.)]\s*(.+)")

# Pattern: Match checkboxes (- [ ] or - [x])
CHECKBOX_PATTERN = re.compile(r"(?:^|\n)\s*-\s*\[\s*[x ]?\s*\]\s*(.+)", re.MULTILINE)

# Pattern: Match code blocks (```...```)
CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```")


def _extract_requirements(description: str) -> list[str]:
    """Extract requirements from ticket description.

    Looks for formal "Requirements" section or falls back to checkboxes.
    Uses markdown bullet points, numbered lists, and task checkboxes.

    Args:
        description: Ticket description text

    Returns:
        List of requirement strings (max 10 items)
    """
    if not description:
        return []

    requirements = []

    # Look for formal Requirements section
    req_section_match = REQUIREMENTS_SECTION_PATTERN.search(description)

    if req_section_match:
        section_text = req_section_match.group(1)
        # Extract bullet points
        items = BULLET_POINT_PATTERN.findall(section_text)
        requirements.extend([item.strip() for item in items])

        # Also check for numbered lists
        numbered = NUMBERED_LIST_PATTERN.findall(section_text)
        requirements.extend([item.strip() for item in numbered])

    # If no formal requirements section, extract from checkboxes
    if not requirements:
        checkboxes = CHECKBOX_PATTERN.findall(description)
        if checkboxes:
            requirements.extend([item.strip() for item in checkboxes])

    return requirements[:10]  # Limit to 10 requirements


def _extract_acceptance_criteria(description: str) -> list[str]:
    """Extract acceptance criteria from ticket description.

    Searches for "Acceptance Criteria", "AC", or "Definition of Done" sections.
    Extracts bullet points and checkboxes.

    Args:
        description: Ticket description text

    Returns:
        List of acceptance criteria strings (max 10 items)
    """
    if not description:
        return []

    criteria = []

    # Look for AC section using compiled pattern
    ac_section_match = AC_SECTION_PATTERN.search(description)

    if ac_section_match:
        section_text = ac_section_match.group(1)
        # Extract bullet points
        items = BULLET_POINT_PATTERN.findall(section_text)
        criteria.extend([item.strip() for item in items])

        # Extract checkboxes
        checkboxes = CHECKBOX_PATTERN.findall(section_text)
        criteria.extend([item.strip() for item in checkboxes])

    return criteria[:10]  # Limit to 10 criteria


def _extract_technical_notes(description: str) -> str:
    """Extract technical notes from ticket description.

    Searches for "Technical Notes", "Implementation Notes", or "Tech Details" sections.
    Falls back to extracting code blocks if no formal section found.

    Args:
        description: Ticket description text

    Returns:
        Technical notes text or empty string
    """
    if not description:
        return ""

    # Look for technical notes section using compiled pattern
    tech_section_match = TECH_SECTION_PATTERN.search(description)

    if tech_section_match:
        return tech_section_match.group(1).strip()

    # Look for code blocks as technical notes
    code_blocks = CODE_BLOCK_PATTERN.findall(description)
    if code_blocks:
        return "\n\n".join(code_blocks)

    return ""


def _extract_dependencies(description: str) -> list[str]:
    """Extract dependencies from ticket description.

    Searches for "Dependencies", "Depends On", or "Related Tickets" sections.
    Extracts Jira ticket keys (format: ABC-123). Falls back to searching
    entire description if no formal section found.

    Args:
        description: Ticket description text

    Returns:
        List of unique ticket keys (max 5 if from general search)
    """
    if not description:
        return []

    dependencies = []

    # Look for dependency section using compiled pattern
    dep_section_match = DEP_SECTION_PATTERN.search(description)

    if dep_section_match:
        section_text = dep_section_match.group(1)
        # Extract ticket keys using compiled pattern
        tickets = TICKET_KEY_PATTERN.findall(section_text)
        dependencies.extend(tickets)

    # Also look for ticket keys anywhere in description if none found
    if not dependencies:
        tickets = TICKET_KEY_PATTERN.findall(description)
        dependencies.extend(tickets[:5])  # Limit to 5

    return list(set(dependencies))  # Remove duplicates


def _estimate_complexity(description: str, summary: str) -> str:
    """Estimate complexity based on description length and content.

    Uses heuristics:
    - High: >1000 chars or contains complexity keywords
    - Medium: >300 chars
    - Low: <=300 chars

    Args:
        description: Ticket description text
        summary: Ticket summary text (not currently used)

    Returns:
        Complexity estimate: "High", "Medium", or "Low"
    """
    if not description:
        return "Low"

    desc_length = len(description)

    # Check for complexity indicators
    complex_keywords = ["complex", "multiple", "integration", "architecture", "refactor"]
    has_complex_keywords = any(keyword in description.lower() for keyword in complex_keywords)

    if desc_length > 1000 or has_complex_keywords:
        return "High"
    elif desc_length > 300:
        return "Medium"
    else:
        return "Low"


async def handle_analyze_ticket(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle analyze_ticket tool call."""
    ticket_key = arguments["ticket_key"]

    # Fetch ticket
    issue = await jira_client.get_issue(ticket_key)

    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    description = fields.get("description", "") or ""

    # Analyze ticket
    analysis: dict[str, Any] = {
        "type": fields.get("issuetype", {}).get("name", "Unknown"),
        "complexity": _estimate_complexity(description, summary),
        "requirements": _extract_requirements(description),
        "acceptance_criteria": _extract_acceptance_criteria(description),
        "technical_notes": _extract_technical_notes(description),
        "dependencies": _extract_dependencies(description),
    }

    response = {
        "ticket": {
            "key": issue.get("key"),
            "summary": summary,
        },
        "analysis": analysis,
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# Tool definition
ANALYZE_TICKET_TOOL = Tool(
    name="analyze_ticket",
    description="Analyze ticket and extract structured implementation details",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key",
            },
        },
        "required": ["ticket_key"],
    },
)
