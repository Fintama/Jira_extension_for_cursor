# Jira MCP Server Design

## Overview

A custom Model Context Protocol (MCP) server for Jira integration that enables AI assistants to interact with Jira issues, facilitating seamless ticket management and implementation workflows.

## Use Cases

1. **Show Assigned Tickets** - Retrieve and display tickets assigned to the current user
2. **Read & Analyze Tickets** - Fetch specific tickets (e.g., "PROJ-123") or highest priority tickets
3. **Analyze Tickets** - Extract and analyze ticket details for implementation planning
4. **Update Tickets** - Modify ticket status, description, and add comments

---

## Architecture

### Technology Stack

**Recommended:** Python (using `mcp` library)
- Pros: Rich ecosystem for API integration, async support, easy to maintain
- Alternative: TypeScript/Node.js (using `@modelcontextprotocol/sdk`)

### Components

```
┌─────────────────────────────────────────┐
│         AI Assistant (Cursor)           │
└──────────────┬──────────────────────────┘
               │ MCP Protocol
               │
┌──────────────▼──────────────────────────┐
│         Jira MCP Server                 │
│  ┌───────────────────────────────────┐  │
│  │  MCP Tools                        │  │
│  │  - list_my_tickets               │  │
│  │  - get_ticket                    │  │
│  │  - get_highest_priority_ticket   │  │
│  │  - analyze_ticket                │  │
│  │  - update_ticket_status          │  │
│  │  - update_ticket_description     │  │
│  │  - add_ticket_comment            │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌───────────────────────────────────┐  │
│  │  Jira API Client                 │  │
│  │  - Authentication                │  │
│  │  - HTTP Request Handler          │  │
│  │  - Response Parsing              │  │
│  │  - Error Handling                │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │ HTTPS/REST
               │
┌──────────────▼──────────────────────────┐
│         Jira Cloud/Server               │
│         REST API v2/v3                  │
└─────────────────────────────────────────┘
```

---

## Jira API Integration

### Authentication

**For Jira Cloud:**
- **API Token** (Recommended): Use email + API token
  - Generate at: https://id.atlassian.com/manage-profile/security/api-tokens
  - Format: Basic Auth with `email:api_token` base64 encoded
  
**For Jira Server/Data Center:**
- **Basic Auth**: Username + Password
- **Personal Access Token** (Jira 8.14+): Bearer token authentication

### API Endpoints

#### 1. Search for Issues (JQL)
```
GET /rest/api/2/search
Query Parameters:
  - jql: JQL query string
  - fields: Comma-separated list of fields
  - maxResults: Maximum results (default: 50)
  - startAt: Pagination offset
```

#### 2. Get Single Issue
```
GET /rest/api/2/issue/{issueIdOrKey}
Query Parameters:
  - fields: Comma-separated list of fields
  - expand: Additional data (comments, changelog, etc.)
```

#### 3. Update Issue
```
PUT /rest/api/2/issue/{issueIdOrKey}
Body: JSON with fields to update
```

#### 4. Transition Issue (Status Change)
```
POST /rest/api/2/issue/{issueIdOrKey}/transitions
Body: { "transition": { "id": "transition_id" } }

GET /rest/api/2/issue/{issueIdOrKey}/transitions
Returns available transitions for the issue
```

#### 5. Add Comment
```
POST /rest/api/2/issue/{issueIdOrKey}/comment
Body: { "body": "comment text" }
```

### JQL Queries (Jira Query Language)

```jql
# My assigned tickets
assignee = currentUser() AND status != Closed

# Highest priority ticket
assignee = currentUser() AND status != Closed ORDER BY priority DESC

# Specific project tickets
project = PROJ AND assignee = currentUser()

# By status
assignee = currentUser() AND status = "In Progress"
```

---

## MCP Server Design

### Configuration Schema

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["-m", "jira_mcp_server"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token",
        "JIRA_PROJECT_KEY": "PROJ"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `JIRA_URL` | Jira instance URL | Yes | `https://company.atlassian.net` |
| `JIRA_EMAIL` | User email (Cloud) | Yes* | `dev@company.com` |
| `JIRA_API_TOKEN` | API token (Cloud) | Yes* | `ATATT3xFf...` |
| `JIRA_USERNAME` | Username (Server) | Yes* | `jdoe` |
| `JIRA_PASSWORD` | Password (Server) | Yes* | `password123` |
| `JIRA_PROJECT_KEY` | Default project | No | `PROJ` |
| `JIRA_MAX_RESULTS` | Max search results | No | `50` (default) |

*Choose Cloud or Server auth method

---

## MCP Tools Specification

### 1. `list_my_tickets`

**Description:** List all tickets assigned to the current user

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "Filter by status (e.g., 'In Progress', 'To Do')",
      "optional": true
    },
    "project": {
      "type": "string",
      "description": "Filter by project key",
      "optional": true
    },
    "max_results": {
      "type": "number",
      "description": "Maximum number of results",
      "default": 50
    }
  }
}
```

**Output:**
```json
{
  "tickets": [
    {
      "key": "PROJ-123",
      "summary": "Implement user authentication",
      "status": "In Progress",
      "priority": "High",
      "assignee": "John Doe",
      "created": "2025-11-01T10:00:00Z",
      "updated": "2025-11-05T14:30:00Z"
    }
  ],
  "total": 5
}
```

### 2. `get_ticket`

**Description:** Get detailed information about a specific ticket

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_key": {
      "type": "string",
      "description": "Jira ticket key (e.g., 'PROJ-123')",
      "required": true
    },
    "include_comments": {
      "type": "boolean",
      "description": "Include comments in response",
      "default": true
    },
    "include_attachments": {
      "type": "boolean",
      "description": "Include attachment metadata",
      "default": false
    }
  }
}
```

**Output:**
```json
{
  "key": "PROJ-123",
  "summary": "Implement user authentication",
  "description": "Full description text...",
  "status": "In Progress",
  "priority": "High",
  "assignee": "John Doe",
  "reporter": "Jane Smith",
  "created": "2025-11-01T10:00:00Z",
  "updated": "2025-11-05T14:30:00Z",
  "labels": ["backend", "security"],
  "components": ["API"],
  "comments": [
    {
      "author": "Jane Smith",
      "body": "Please use OAuth2",
      "created": "2025-11-02T09:00:00Z"
    }
  ]
}
```

### 3. `get_highest_priority_ticket`

**Description:** Get the highest priority ticket assigned to the current user

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "exclude_status": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Statuses to exclude",
      "default": ["Closed", "Done"]
    },
    "project": {
      "type": "string",
      "description": "Filter by project key",
      "optional": true
    }
  }
}
```

**Output:** Same as `get_ticket`

### 4. `analyze_ticket`

**Description:** Analyze ticket and extract structured implementation details

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_key": {
      "type": "string",
      "description": "Jira ticket key",
      "required": true
    }
  }
}
```

**Output:**
```json
{
  "ticket": {
    "key": "PROJ-123",
    "summary": "Implement user authentication"
  },
  "analysis": {
    "type": "Feature",
    "complexity": "High",
    "estimated_effort": "5 days",
    "requirements": [
      "OAuth2 implementation",
      "JWT token generation",
      "User session management"
    ],
    "acceptance_criteria": [
      "Users can login with email/password",
      "JWT tokens expire after 24 hours"
    ],
    "technical_notes": "Use bcrypt for password hashing",
    "dependencies": [],
    "risks": ["Session security"]
  }
}
```

### 5. `update_ticket_status`

**Description:** Transition ticket to a new status

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_key": {
      "type": "string",
      "description": "Jira ticket key",
      "required": true
    },
    "status": {
      "type": "string",
      "description": "Target status name",
      "required": true
    },
    "comment": {
      "type": "string",
      "description": "Optional comment to add",
      "optional": true
    }
  }
}
```

**Output:**
```json
{
  "success": true,
  "ticket_key": "PROJ-123",
  "old_status": "To Do",
  "new_status": "In Progress"
}
```

### 6. `update_ticket_description`

**Description:** Update ticket description

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_key": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "string",
      "required": true
    },
    "append": {
      "type": "boolean",
      "description": "Append to existing description",
      "default": false
    }
  }
}
```

**Output:**
```json
{
  "success": true,
  "ticket_key": "PROJ-123"
}
```

### 7. `add_ticket_comment`

**Description:** Add a comment to a ticket

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "ticket_key": {
      "type": "string",
      "required": true
    },
    "comment": {
      "type": "string",
      "required": true
    },
    "visibility": {
      "type": "string",
      "description": "Visibility restriction",
      "enum": ["public", "internal"],
      "default": "public"
    }
  }
}
```

**Output:**
```json
{
  "success": true,
  "ticket_key": "PROJ-123",
  "comment_id": "10042"
}
```

---

## Implementation Structure

### Directory Layout

```
jira-mcp-server/
├── pyproject.toml           # Python project config
├── README.md                # Setup instructions
├── requirements.txt         # Dependencies
├── .env.example            # Example environment variables
├── src/
│   └── jira_mcp_server/
│       ├── __init__.py
│       ├── __main__.py     # Entry point
│       ├── server.py       # MCP server setup
│       ├── config.py       # Configuration management
│       ├── jira_client.py  # Jira API client
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── list_tickets.py
│       │   ├── get_ticket.py
│       │   ├── analyze_ticket.py
│       │   └── update_ticket.py
│       └── utils/
│           ├── __init__.py
│           ├── jql_builder.py
│           └── ticket_parser.py
└── tests/
    ├── test_jira_client.py
    ├── test_tools.py
    └── fixtures/
        └── sample_responses.json
```

### Key Dependencies

```txt
# MCP
mcp>=0.1.0

# HTTP Client
httpx>=0.25.0
aiohttp>=3.9.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
mypy>=1.5.0
```

---

## Error Handling

### Error Categories

1. **Authentication Errors**
   - Invalid credentials
   - Expired token
   - Insufficient permissions

2. **API Errors**
   - Rate limiting (429)
   - Not found (404)
   - Validation errors (400)
   - Server errors (500)

3. **Input Validation Errors**
   - Invalid ticket key format
   - Invalid JQL syntax
   - Missing required fields

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "TICKET_NOT_FOUND",
    "message": "Ticket PROJ-999 does not exist",
    "details": {
      "ticket_key": "PROJ-999"
    }
  }
}
```

---

## Security Considerations

1. **Credential Storage**
   - Never hardcode credentials
   - Use environment variables
   - Consider using secret management systems (AWS Secrets Manager, HashiCorp Vault)

2. **API Token Permissions**
   - Use principle of least privilege
   - Create dedicated service accounts for automation
   - Regularly rotate API tokens

3. **Data Privacy**
   - Be mindful of sensitive data in tickets
   - Implement logging without exposing credentials
   - Consider data retention policies

4. **Network Security**
   - Always use HTTPS
   - Validate SSL certificates
   - Consider IP whitelisting if available

---

## Rate Limiting & Performance

### Jira Cloud Rate Limits
- **Standard**: 10 requests/second per user
- **Premium**: 25 requests/second per user
- **Burst**: 100 requests/second (short bursts)

### Mitigation Strategies

1. **Caching**
   ```python
   # Cache ticket data for 5 minutes
   from functools import lru_cache
   from datetime import timedelta
   
   @lru_cache(maxsize=100)
   def get_ticket_cached(ticket_key: str):
       # Implementation
       pass
   ```

2. **Request Batching**
   - Use bulk operations where available
   - Batch multiple ticket fetches

3. **Retry Logic**
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10)
   )
   async def make_jira_request(...):
       # Implementation
       pass
   ```

---

## Testing Strategy

### Unit Tests
- Test each MCP tool independently
- Mock Jira API responses
- Test error handling

### Integration Tests
- Test against Jira sandbox environment
- Verify authentication flows
- Test real API interactions

### Test Data
```json
{
  "sample_ticket": {
    "key": "TEST-123",
    "fields": {
      "summary": "Sample ticket",
      "status": { "name": "To Do" },
      "priority": { "name": "High" }
    }
  }
}
```

---

## Deployment Options

### Option 1: Local Development
```bash
# Install
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python -m jira_mcp_server
```

### Option 2: Docker Container
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
CMD ["python", "-m", "jira_mcp_server"]
```

### Option 3: System Service
```ini
# /etc/systemd/system/jira-mcp.service
[Unit]
Description=Jira MCP Server
After=network.target

[Service]
Type=simple
User=mcp
EnvironmentFile=/etc/jira-mcp/.env
ExecStart=/usr/local/bin/python -m jira_mcp_server
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Usage Examples

### Example 1: Show My Tickets
```
User: "Show me my assigned Jira tickets"

AI uses: list_my_tickets()

Response: "You have 5 assigned tickets:
1. PROJ-123 (High) - Implement user authentication [In Progress]
2. PROJ-124 (Medium) - Fix login bug [To Do]
3. PROJ-125 (Low) - Update documentation [In Progress]
..."
```

### Example 2: Read and Implement
```
User: "Read ticket PROJ-123 and implement it"

AI uses: get_ticket(ticket_key="PROJ-123")

Response: "PROJ-123: Implement user authentication

Description: Add OAuth2 authentication to the API...

I'll now implement this feature. Based on the requirements:
1. Create auth endpoints
2. Implement JWT token generation
3. Add user session management
..."
```

### Example 3: Highest Priority
```
User: "Show me the highest priority ticket"

AI uses: get_highest_priority_ticket()

Response: "Your highest priority ticket is:

PROJ-123 (Priority: High) - Implement user authentication
Status: In Progress
Created: 2025-11-01

Description: Add OAuth2 authentication...
Would you like me to work on this ticket?"
```

### Example 4: Update Status
```
User: "Move PROJ-123 to Done and add a comment that it's completed"

AI uses: 
  - update_ticket_status(ticket_key="PROJ-123", status="Done")
  - add_ticket_comment(ticket_key="PROJ-123", comment="Implementation completed")

Response: "✓ Updated PROJ-123 status to 'Done'
✓ Added completion comment"
```

---

## Future Enhancements

### Phase 2 Features
1. **Advanced Search**
   - Custom JQL queries
   - Saved filters
   - Project-wide search

2. **Bulk Operations**
   - Update multiple tickets
   - Batch status changes

3. **Attachments**
   - Download attachments
   - Upload files to tickets

4. **Webhooks**
   - Real-time notifications
   - Ticket change events

5. **Analytics**
   - Ticket velocity metrics
   - Time tracking
   - Sprint burndown

### Phase 3 Features
1. **Board Integration**
   - View Scrum/Kanban boards
   - Move tickets across columns

2. **Sprint Management**
   - Create sprints
   - Add/remove tickets from sprints

3. **Relationship Management**
   - Link tickets
   - View dependencies
   - Epic/Story hierarchy

---

## Monitoring & Logging

### Logging Strategy
```python
import logging

logger = logging.getLogger("jira_mcp_server")
logger.setLevel(logging.INFO)

# Log important events
logger.info(f"Fetching ticket {ticket_key}")
logger.error(f"Failed to update ticket: {error}")
logger.warning(f"Rate limit approaching: {remaining_requests}")
```

### Metrics to Track
- API call count
- Response times
- Error rates
- Cache hit rates
- Rate limit proximity

---

## Troubleshooting Guide

### Common Issues

**Issue:** "Authentication failed"
- **Solution:** Verify API token is correct and not expired
- Check email/username format
- Ensure using correct auth method (Cloud vs Server)

**Issue:** "Ticket not found"
- **Solution:** Verify ticket key format (PROJECT-123)
- Check user has permission to view ticket
- Confirm ticket exists and is not deleted

**Issue:** "Cannot transition ticket"
- **Solution:** Check available transitions for current status
- Verify user has permission to perform transition
- Ensure workflow allows this transition

**Issue:** "Rate limit exceeded"
- **Solution:** Implement exponential backoff
- Use caching to reduce API calls
- Consider upgrading Jira plan

---

## References

### Jira API Documentation
- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Jira Server REST API](https://docs.atlassian.com/software/jira/docs/api/REST/latest/)
- [JQL Reference](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

### MCP Resources
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

### Authentication Guides
- [Jira Cloud API Tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [Basic Auth](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)

---

## Next Steps

1. **Setup Phase**
   - [ ] Choose implementation language (Python recommended)
   - [ ] Create project structure
   - [ ] Set up development environment

2. **Core Implementation**
   - [ ] Implement Jira API client
   - [ ] Create authentication handler
   - [ ] Build MCP server foundation

3. **Tool Development**
   - [ ] Implement `list_my_tickets`
   - [ ] Implement `get_ticket`
   - [ ] Implement `get_highest_priority_ticket`
   - [ ] Implement `analyze_ticket`
   - [ ] Implement update operations

4. **Testing**
   - [ ] Write unit tests
   - [ ] Set up integration tests
   - [ ] Test with real Jira instance

5. **Documentation**
   - [ ] Write setup guide
   - [ ] Create configuration examples
   - [ ] Document usage patterns

6. **Deployment**
   - [ ] Package for distribution
   - [ ] Create Docker image
   - [ ] Set up CI/CD pipeline

---

## Conclusion

This design provides a comprehensive foundation for building a Jira MCP server that integrates seamlessly with AI assistants. The server will enable efficient ticket management, analysis, and implementation workflows directly from your AI coding environment.

Key benefits:
- **Seamless Integration**: Work with Jira tickets without leaving your development environment
- **Enhanced Productivity**: AI can read, analyze, and update tickets automatically
- **Flexible Architecture**: Easy to extend with additional features
- **Production-Ready**: Includes error handling, rate limiting, and security best practices

The modular design allows for incremental development, starting with core features and expanding based on team needs.

