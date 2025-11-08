# Jira MCP - API Reference

Complete reference for all 7 MCP tools provided by Jira MCP for Cursor.

---

## Tool Overview

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `list_my_tickets` | List assigned tickets | status, project, max_results |
| `get_ticket` | Get ticket details | ticket_key, include_comments |
| `get_highest_priority_ticket` | Find top priority | exclude_status, project |
| `analyze_ticket` | Extract requirements | ticket_key |
| `update_ticket_status` | Change status | ticket_key, status, comment |
| `update_ticket_description` | Update description | ticket_key, description, append |
| `add_ticket_comment` | Add comment | ticket_key, comment |

---

## 1. list_my_tickets

List all tickets assigned to the current user with optional filters.

### Input Schema

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

### Output Schema

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

### Examples

**Basic usage:**
```
User: "Show me my Jira tickets"
AI calls: list_my_tickets({})
```

**With filters:**
```
User: "List my In Progress tickets in project BACKEND"
AI calls: list_my_tickets({"status": "In Progress", "project": "BACKEND"})
```

**Limited results:**
```
User: "Show me my top 10 tickets"
AI calls: list_my_tickets({"max_results": 10})
```

---

## 2. get_ticket

Get detailed information about a specific ticket including description, comments, and metadata.

### Input Schema

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
    }
  },
  "required": ["ticket_key"]
}
```

### Output Schema

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

### Examples

**Get ticket details:**
```
User: "Show me ticket PROJ-123"
AI calls: get_ticket({"ticket_key": "PROJ-123"})
```

**Without comments:**
```
User: "Get PROJ-456 without comments"
AI calls: get_ticket({"ticket_key": "PROJ-456", "include_comments": false})
```

---

## 3. get_highest_priority_ticket

Find and return the highest priority ticket assigned to you.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "exclude_status": {
      "type": "array",
      "items": {"type": "string"},
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

### Output Schema

Same as `get_ticket` - returns full ticket details.

### Examples

**Find highest priority:**
```
User: "What's my highest priority ticket?"
AI calls: get_highest_priority_ticket({})
```

**In specific project:**
```
User: "What's my top priority in project BACKEND?"
AI calls: get_highest_priority_ticket({"project": "BACKEND"})
```

**Include specific statuses:**
```
User: "What's my highest priority To Do ticket?"
AI calls: get_highest_priority_ticket({"exclude_status": ["In Progress", "Done", "Closed"]})
```

---

## 4. analyze_ticket

Analyze ticket description and extract structured implementation details.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "ticket_key": {
      "type": "string",
      "description": "Jira ticket key",
      "required": true
    }
  },
  "required": ["ticket_key"]
}
```

### Output Schema

```json
{
  "ticket": {
    "key": "PROJ-123",
    "summary": "Implement user authentication"
  },
  "analysis": {
    "type": "Feature",
    "complexity": "High",
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
    "dependencies": ["AUTH-100", "DB-50"]
  }
}
```

### Examples

**Analyze for implementation:**
```
User: "Analyze ticket PROJ-123 and extract requirements"
AI calls: analyze_ticket({"ticket_key": "PROJ-123"})
```

**Extract acceptance criteria:**
```
User: "What are the acceptance criteria for PROJ-456?"
AI calls: analyze_ticket({"ticket_key": "PROJ-456"})
Response: Extracts AC section from description
```

---

## 5. update_ticket_status

Transition a ticket to a new status (e.g., To Do → In Progress → Done).

### Input Schema

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
  },
  "required": ["ticket_key", "status"]
}
```

### Output Schema

```json
{
  "success": true,
  "ticket_key": "PROJ-123",
  "old_status": "To Do",
  "new_status": "In Progress"
}
```

### Examples

**Move to In Progress:**
```
User: "Move PROJ-123 to In Progress"
AI calls: update_ticket_status({"ticket_key": "PROJ-123", "status": "In Progress"})
```

**With comment:**
```
User: "Mark PROJ-456 as Done and add comment that it's completed"
AI calls: update_ticket_status({
  "ticket_key": "PROJ-456",
  "status": "Done",
  "comment": "Implementation completed and tested"
})
```

### Error Handling

If the target status is not available, the tool returns an error with available transitions:

```json
{
  "error": "Cannot transition to 'Closed'. Available: To Do, In Progress, Done"
}
```

---

## 6. update_ticket_description

Update a ticket's description, either replacing it entirely or appending to it.

### Input Schema

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
  },
  "required": ["ticket_key", "description"]
}
```

### Output Schema

```json
{
  "success": true,
  "ticket_key": "PROJ-123"
}
```

### Examples

**Replace description:**
```
User: "Update PROJ-123 description to: New requirements based on review"
AI calls: update_ticket_description({
  "ticket_key": "PROJ-123",
  "description": "New requirements based on review",
  "append": false
})
```

**Append notes:**
```
User: "Add implementation notes to PROJ-456"
AI calls: update_ticket_description({
  "ticket_key": "PROJ-456",
  "description": "\n\n## Implementation Notes\nUsed async/await pattern",
  "append": true
})
```

---

## 7. add_ticket_comment

Add a comment to a ticket.

### Input Schema

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
    }
  },
  "required": ["ticket_key", "comment"]
}
```

### Output Schema

```json
{
  "success": true,
  "ticket_key": "PROJ-123",
  "comment_id": "10042"
}
```

### Examples

**Add comment:**
```
User: "Add comment to PROJ-123: Code review completed"
AI calls: add_ticket_comment({
  "ticket_key": "PROJ-123",
  "comment": "Code review completed. Ready to merge."
})
```

**Status update comment:**
```
User: "Comment on PROJ-456 that I'm blocked on AUTH-100"
AI calls: add_ticket_comment({
  "ticket_key": "PROJ-456",
  "comment": "Blocked: Waiting for AUTH-100 to be completed"
})
```

---

## Error Handling

All tools follow consistent error handling:

### Common Errors

**Authentication Error (401):**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Authentication failed. Check your credentials."
  }
}
```

**Ticket Not Found (404):**
```json
{
  "success": false,
  "error": {
    "code": "TICKET_NOT_FOUND",
    "message": "Ticket PROJ-999 not found or you don't have permission to view it."
  }
}
```

**Rate Limit (429):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT",
    "message": "Rate limit exceeded. Please try again later."
  }
}
```

**Note:** The client automatically retries rate limit errors with exponential backoff (1s, 2s, 4s).

---

## Rate Limiting

**Jira Cloud Limits:**
- Standard: 10 requests/second per user
- Premium: 25 requests/second per user

**Mitigation:**
- Automatic retry with exponential backoff
- Configurable via `JIRA_MAX_RETRIES` (default: 3)
- Client-side request throttling

---

## Performance

**Benchmarks** (with mocked API):
- `list_my_tickets`: < 2s for 50 tickets
- `get_ticket`: < 1s per ticket
- `analyze_ticket`: < 1s (parsing only)
- `update_ticket_status`: < 1.5s
- `add_ticket_comment`: < 1s

**Note:** Actual performance depends on Jira API response times.

---

## Advanced Usage

### Custom JQL Queries

The tools use JQL (Jira Query Language) internally. Examples of what's generated:

```jql
# list_my_tickets with status filter
assignee = currentUser() AND status = "In Progress"

# get_highest_priority_ticket
assignee = currentUser() AND status != "Done" AND status != "Closed" ORDER BY priority DESC

# With project filter
assignee = currentUser() AND project = "BACKEND" ORDER BY priority DESC
```

### Ticket Analysis Patterns

The `analyze_ticket` tool recognizes these markdown patterns:

**Requirements:**
```markdown
# Requirements
- OAuth2 implementation
- JWT token generation
```

**Acceptance Criteria:**
```markdown
## Acceptance Criteria
- [ ] Users can login
- [ ] Tokens expire after 24h
```

**Technical Notes:**
```markdown
### Technical Notes
```python
def authenticate(user):
    # Implementation
```

**Dependencies:**
```markdown
Dependencies: AUTH-123, DB-456
```

---

## Configuration

### Environment Variables

All tools respect these configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `JIRA_URL` | Jira instance URL | *Required* |
| `JIRA_EMAIL` | User email (Cloud) | *Required* |
| `JIRA_API_TOKEN` | API token (Cloud) | *Required* |
| `JIRA_MAX_RESULTS` | Max search results | 50 |
| `JIRA_TIMEOUT` | Request timeout (seconds) | 30 |
| `JIRA_MAX_RETRIES` | Max retry attempts | 3 |
| `LOG_LEVEL` | Logging level | INFO |

---

## Response Formats

### Success Response

```json
{
  "success": true,
  "ticket_key": "PROJ-123",
  ...additional data...
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context (optional)"
  }
}
```

---

## Best Practices

### 1. Always Handle Errors

```python
# Tools may raise exceptions
try:
    result = await handle_get_ticket({"ticket_key": "PROJ-123"}, client)
except TicketNotFoundError:
    # Handle missing ticket
except AuthenticationError:
    # Handle auth failure
```

### 2. Use Appropriate Filters

```python
# Good: Specific filter
list_my_tickets({"status": "In Progress", "max_results": 10})

# Less efficient: No filters with high max_results
list_my_tickets({"max_results": 500})  # May be slow
```

### 3. Test Connections First

Before using tools in production, test connectivity:

```bash
jira-mcp config test
```

---

## Limitations

- **Jira Cloud only** (Server support in beta)
- **Rate limits** apply per Jira plan
- **No attachment support** (coming in future release)
- **No bulk operations** (coming in future release)

---

## See Also

- [User Guide](USER_GUIDE.md) - Complete usage guide
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [README](../README.md) - Overview and installation

---

**For questions or issues, please see our [GitHub repository](https://github.com/yourusername/jira-mcp-cursor).**

