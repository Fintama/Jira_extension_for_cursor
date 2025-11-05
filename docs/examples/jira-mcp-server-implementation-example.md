# Jira MCP Server - Implementation Example

## Quick Start Implementation

This document provides a concrete implementation example for the Jira MCP Server design.

---

## 1. Project Setup

### Create Project Structure
```bash
mkdir jira-mcp-server
cd jira-mcp-server

# Create directory structure
mkdir -p src/jira_mcp_server/tools
mkdir -p src/jira_mcp_server/utils
mkdir -p tests/fixtures
```

### pyproject.toml
```toml
[project]
name = "jira-mcp-server"
version = "0.1.0"
description = "MCP server for Jira integration"
requires-python = ">=3.11"
dependencies = [
    "mcp>=0.1.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 100
target-version = "py311"
```

---

## 2. Configuration Module

### src/jira_mcp_server/config.py
```python
"""Configuration management for Jira MCP Server."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Jira Connection
    jira_url: str
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_username: Optional[str] = None
    jira_password: Optional[str] = None
    
    # Optional Configuration
    jira_project_key: Optional[str] = None
    jira_max_results: int = 50
    jira_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def is_cloud(self) -> bool:
        """Determine if using Jira Cloud or Server."""
        return self.jira_email is not None and self.jira_api_token is not None
    
    def get_auth(self) -> tuple[str, str]:
        """Get authentication credentials."""
        if self.is_cloud:
            if not self.jira_email or not self.jira_api_token:
                raise ValueError("Jira Cloud requires email and API token")
            return (self.jira_email, self.jira_api_token)
        else:
            if not self.jira_username or not self.jira_password:
                raise ValueError("Jira Server requires username and password")
            return (self.jira_username, self.jira_password)


# Global settings instance
settings = Settings()
```

---

## 3. Jira API Client

### src/jira_mcp_server/jira_client.py
```python
"""Jira API client for interacting with Jira REST API."""
import httpx
from typing import Any, Optional
import logging
from .config import settings

logger = logging.getLogger(__name__)


class JiraClient:
    """Async client for Jira REST API."""
    
    def __init__(self):
        self.base_url = settings.jira_url.rstrip("/")
        self.auth = settings.get_auth()
        self.timeout = settings.jira_timeout
        
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make authenticated request to Jira API."""
        url = f"{self.base_url}/rest/api/2{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response.json() if response.content else {}
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise JiraAPIError(
                    f"Jira API error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    details=e.response.text,
                )
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise JiraAPIError(f"Request failed: {str(e)}")
    
    async def search_issues(
        self,
        jql: str,
        fields: Optional[list[str]] = None,
        max_results: Optional[int] = None,
    ) -> dict[str, Any]:
        """Search for issues using JQL."""
        params = {
            "jql": jql,
            "maxResults": max_results or settings.jira_max_results,
        }
        if fields:
            params["fields"] = ",".join(fields)
        
        logger.info(f"Searching issues with JQL: {jql}")
        return await self._request("GET", "/search", params=params)
    
    async def get_issue(
        self,
        issue_key: str,
        fields: Optional[list[str]] = None,
        expand: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Get a single issue by key."""
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)
        
        logger.info(f"Fetching issue: {issue_key}")
        return await self._request("GET", f"/issue/{issue_key}", params=params)
    
    async def update_issue(
        self,
        issue_key: str,
        fields: dict[str, Any],
    ) -> None:
        """Update issue fields."""
        logger.info(f"Updating issue: {issue_key}")
        await self._request(
            "PUT",
            f"/issue/{issue_key}",
            json={"fields": fields},
        )
    
    async def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        """Get available transitions for an issue."""
        result = await self._request("GET", f"/issue/{issue_key}/transitions")
        return result.get("transitions", [])
    
    async def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        comment: Optional[str] = None,
    ) -> None:
        """Transition issue to new status."""
        payload: dict[str, Any] = {
            "transition": {"id": transition_id}
        }
        if comment:
            payload["update"] = {
                "comment": [{"add": {"body": comment}}]
            }
        
        logger.info(f"Transitioning issue {issue_key} to transition {transition_id}")
        await self._request("POST", f"/issue/{issue_key}/transitions", json=payload)
    
    async def add_comment(
        self,
        issue_key: str,
        comment: str,
    ) -> dict[str, Any]:
        """Add comment to an issue."""
        logger.info(f"Adding comment to issue: {issue_key}")
        return await self._request(
            "POST",
            f"/issue/{issue_key}/comment",
            json={"body": comment},
        )


class JiraAPIError(Exception):
    """Custom exception for Jira API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details
```

---

## 4. Utility Functions

### src/jira_mcp_server/utils/jql_builder.py
```python
"""JQL query builder utilities."""
from typing import Optional


def build_my_tickets_jql(
    status: Optional[str] = None,
    project: Optional[str] = None,
    exclude_statuses: Optional[list[str]] = None,
) -> str:
    """Build JQL query for user's assigned tickets."""
    parts = ["assignee = currentUser()"]
    
    if status:
        parts.append(f'status = "{status}"')
    
    if project:
        parts.append(f'project = "{project}"')
    
    if exclude_statuses:
        for status in exclude_statuses:
            parts.append(f'status != "{status}"')
    
    return " AND ".join(parts)


def build_highest_priority_jql(
    project: Optional[str] = None,
    exclude_statuses: Optional[list[str]] = None,
) -> str:
    """Build JQL query for highest priority ticket."""
    jql = build_my_tickets_jql(project=project, exclude_statuses=exclude_statuses)
    return f"{jql} ORDER BY priority DESC"
```

### src/jira_mcp_server/utils/ticket_parser.py
```python
"""Utilities for parsing Jira ticket data."""
from typing import Any
from datetime import datetime


def parse_ticket_summary(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse issue into summary format."""
    fields = issue.get("fields", {})
    
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "status": fields.get("status", {}).get("name"),
        "priority": fields.get("priority", {}).get("name"),
        "assignee": fields.get("assignee", {}).get("displayName"),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
    }


def parse_ticket_detail(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse issue into detailed format."""
    fields = issue.get("fields", {})
    
    # Parse comments
    comments = []
    comment_data = fields.get("comment", {})
    for comment in comment_data.get("comments", []):
        comments.append({
            "author": comment.get("author", {}).get("displayName"),
            "body": comment.get("body"),
            "created": comment.get("created"),
        })
    
    # Parse labels
    labels = fields.get("labels", [])
    
    # Parse components
    components = [c.get("name") for c in fields.get("components", [])]
    
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": fields.get("status", {}).get("name"),
        "priority": fields.get("priority", {}).get("name"),
        "assignee": fields.get("assignee", {}).get("displayName"),
        "reporter": fields.get("reporter", {}).get("displayName"),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "labels": labels,
        "components": components,
        "comments": comments,
    }
```

---

## 5. MCP Tools Implementation

### src/jira_mcp_server/tools/list_tickets.py
```python
"""List tickets tool."""
from mcp.types import Tool, TextContent
from ..jira_client import JiraClient
from ..utils.jql_builder import build_my_tickets_jql
from ..utils.ticket_parser import parse_ticket_summary
import json


async def handle_list_my_tickets(arguments: dict) -> list[TextContent]:
    """Handle list_my_tickets tool call."""
    client = JiraClient()
    
    # Build JQL query
    jql = build_my_tickets_jql(
        status=arguments.get("status"),
        project=arguments.get("project"),
    )
    
    # Search issues
    result = await client.search_issues(
        jql=jql,
        max_results=arguments.get("max_results", 50),
        fields=["summary", "status", "priority", "assignee", "created", "updated"],
    )
    
    # Parse results
    tickets = [parse_ticket_summary(issue) for issue in result.get("issues", [])]
    
    response = {
        "tickets": tickets,
        "total": result.get("total", 0),
    }
    
    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# Tool definition
LIST_MY_TICKETS_TOOL = Tool(
    name="list_my_tickets",
    description="List all tickets assigned to the current user",
    inputSchema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status (e.g., 'In Progress', 'To Do')",
            },
            "project": {
                "type": "string",
                "description": "Filter by project key",
            },
            "max_results": {
                "type": "number",
                "description": "Maximum number of results",
                "default": 50,
            },
        },
    },
)
```

### src/jira_mcp_server/tools/get_ticket.py
```python
"""Get ticket tool."""
from mcp.types import Tool, TextContent
from ..jira_client import JiraClient
from ..utils.ticket_parser import parse_ticket_detail
import json


async def handle_get_ticket(arguments: dict) -> list[TextContent]:
    """Handle get_ticket tool call."""
    client = JiraClient()
    ticket_key = arguments["ticket_key"]
    
    # Determine fields to expand
    expand = []
    if arguments.get("include_comments", True):
        expand.append("renderedFields")
    
    # Fetch issue
    issue = await client.get_issue(
        issue_key=ticket_key,
        expand=expand if expand else None,
    )
    
    # Parse ticket
    ticket = parse_ticket_detail(issue)
    
    return [TextContent(type="text", text=json.dumps(ticket, indent=2))]


# Tool definition
GET_TICKET_TOOL = Tool(
    name="get_ticket",
    description="Get detailed information about a specific ticket",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key (e.g., 'PROJ-123')",
            },
            "include_comments": {
                "type": "boolean",
                "description": "Include comments in response",
                "default": True,
            },
        },
        "required": ["ticket_key"],
    },
)
```

### src/jira_mcp_server/tools/update_ticket.py
```python
"""Update ticket tools."""
from mcp.types import Tool, TextContent
from ..jira_client import JiraClient, JiraAPIError
import json


async def handle_update_ticket_status(arguments: dict) -> list[TextContent]:
    """Handle update_ticket_status tool call."""
    client = JiraClient()
    ticket_key = arguments["ticket_key"]
    target_status = arguments["status"]
    
    # Get current issue to find old status
    issue = await client.get_issue(ticket_key, fields=["status"])
    old_status = issue["fields"]["status"]["name"]
    
    # Get available transitions
    transitions = await client.get_transitions(ticket_key)
    
    # Find transition ID for target status
    transition_id = None
    for transition in transitions:
        if transition["to"]["name"].lower() == target_status.lower():
            transition_id = transition["id"]
            break
    
    if not transition_id:
        available = [t["to"]["name"] for t in transitions]
        raise JiraAPIError(
            f"Cannot transition to '{target_status}'. Available: {', '.join(available)}"
        )
    
    # Perform transition
    await client.transition_issue(
        ticket_key,
        transition_id,
        comment=arguments.get("comment"),
    )
    
    response = {
        "success": True,
        "ticket_key": ticket_key,
        "old_status": old_status,
        "new_status": target_status,
    }
    
    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_add_ticket_comment(arguments: dict) -> list[TextContent]:
    """Handle add_ticket_comment tool call."""
    client = JiraClient()
    
    result = await client.add_comment(
        arguments["ticket_key"],
        arguments["comment"],
    )
    
    response = {
        "success": True,
        "ticket_key": arguments["ticket_key"],
        "comment_id": result.get("id"),
    }
    
    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# Tool definitions
UPDATE_TICKET_STATUS_TOOL = Tool(
    name="update_ticket_status",
    description="Transition ticket to a new status",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key",
            },
            "status": {
                "type": "string",
                "description": "Target status name",
            },
            "comment": {
                "type": "string",
                "description": "Optional comment to add",
            },
        },
        "required": ["ticket_key", "status"],
    },
)

ADD_TICKET_COMMENT_TOOL = Tool(
    name="add_ticket_comment",
    description="Add a comment to a ticket",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key",
            },
            "comment": {
                "type": "string",
                "description": "Comment text",
            },
        },
        "required": ["ticket_key", "comment"],
    },
)
```

---

## 6. Main Server Implementation

### src/jira_mcp_server/server.py
```python
"""Main MCP server implementation."""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import logging

from .tools.list_tickets import LIST_MY_TICKETS_TOOL, handle_list_my_tickets
from .tools.get_ticket import GET_TICKET_TOOL, handle_get_ticket
from .tools.update_ticket import (
    UPDATE_TICKET_STATUS_TOOL,
    ADD_TICKET_COMMENT_TOOL,
    handle_update_ticket_status,
    handle_add_ticket_comment,
)
from .config import settings

logger = logging.getLogger(__name__)


# Create server instance
app = Server("jira-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        LIST_MY_TICKETS_TOOL,
        GET_TICKET_TOOL,
        UPDATE_TICKET_STATUS_TOOL,
        ADD_TICKET_COMMENT_TOOL,
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "list_my_tickets":
            return await handle_list_my_tickets(arguments)
        elif name == "get_ticket":
            return await handle_get_ticket(arguments)
        elif name == "update_ticket_status":
            return await handle_update_ticket_status(arguments)
        elif name == "add_ticket_comment":
            return await handle_add_ticket_comment(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        error_response = {
            "success": False,
            "error": {
                "message": str(e),
                "tool": name,
            }
        }
        import json
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def run():
    """Run the MCP server."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    logger.info(f"Starting Jira MCP Server")
    logger.info(f"Jira URL: {settings.jira_url}")
    logger.info(f"Auth mode: {'Cloud' if settings.is_cloud else 'Server'}")
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)
```

### src/jira_mcp_server/__main__.py
```python
"""Entry point for Jira MCP Server."""
import asyncio
from .server import run


if __name__ == "__main__":
    asyncio.run(run())
```

### src/jira_mcp_server/__init__.py
```python
"""Jira MCP Server - MCP server for Jira integration."""
__version__ = "0.1.0"
```

---

## 7. Configuration Files

### .env.example
```bash
# Jira Configuration

# Jira Instance URL (required)
JIRA_URL=https://your-domain.atlassian.net

# For Jira Cloud (use email + API token)
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here

# For Jira Server/Data Center (use username + password)
# JIRA_USERNAME=your-username
# JIRA_PASSWORD=your-password

# Optional Configuration
JIRA_PROJECT_KEY=PROJ
JIRA_MAX_RESULTS=50
JIRA_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
```

### README.md
```markdown
# Jira MCP Server

Model Context Protocol (MCP) server for Jira integration.

## Features

- List assigned tickets
- Get ticket details
- Update ticket status
- Add comments to tickets

## Installation

```bash
# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your Jira credentials:
   - For Jira Cloud: Use `JIRA_EMAIL` and `JIRA_API_TOKEN`
   - For Jira Server: Use `JIRA_USERNAME` and `JIRA_PASSWORD`

3. Get your Jira API token:
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Create new token
   - Copy token to `.env`

## Usage

### Run Server
```bash
python -m jira_mcp_server
```

### Configure in Cursor

Add to your MCP settings:

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["-m", "jira_mcp_server"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Available Tools

- `list_my_tickets` - List tickets assigned to you
- `get_ticket` - Get detailed ticket information
- `update_ticket_status` - Change ticket status
- `add_ticket_comment` - Add comment to ticket

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

## License

MIT
```

---

## 8. Testing

### tests/test_jira_client.py
```python
"""Tests for Jira client."""
import pytest
from unittest.mock import AsyncMock, patch
from jira_mcp_server.jira_client import JiraClient


@pytest.mark.asyncio
async def test_search_issues():
    """Test searching for issues."""
    client = JiraClient()
    
    mock_response = {
        "issues": [
            {
                "key": "TEST-123",
                "fields": {
                    "summary": "Test ticket",
                    "status": {"name": "To Do"},
                }
            }
        ],
        "total": 1,
    }
    
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.search_issues("assignee = currentUser()")
        
        assert result["total"] == 1
        assert len(result["issues"]) == 1
        assert result["issues"][0]["key"] == "TEST-123"


@pytest.mark.asyncio
async def test_get_issue():
    """Test getting single issue."""
    client = JiraClient()
    
    mock_response = {
        "key": "TEST-123",
        "fields": {
            "summary": "Test ticket",
            "description": "Test description",
        }
    }
    
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_issue("TEST-123")
        
        assert result["key"] == "TEST-123"
        assert result["fields"]["summary"] == "Test ticket"
```

### tests/conftest.py
```python
"""Pytest configuration."""
import pytest
import os


@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables for tests."""
    os.environ["JIRA_URL"] = "https://test.atlassian.net"
    os.environ["JIRA_EMAIL"] = "test@example.com"
    os.environ["JIRA_API_TOKEN"] = "test-token"
```

---

## 9. Installation & Running

### Install
```bash
cd jira-mcp-server
pip install -e .
```

### Configure
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Run
```bash
python -m jira_mcp_server
```

### Test
```bash
pytest tests/
```

---

## Summary

This implementation provides:

✅ **Complete MCP server** with tool definitions
✅ **Async Jira client** with error handling
✅ **Configuration management** via environment variables
✅ **Utility functions** for JQL building and parsing
✅ **Comprehensive error handling**
✅ **Type hints** throughout
✅ **Testing setup** with pytest
✅ **Production-ready** structure

The server is ready to be integrated with Cursor and will enable AI assistants to interact with Jira seamlessly!

