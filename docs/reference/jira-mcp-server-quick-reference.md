# Jira MCP Server - Quick Reference

Quick reference guide for building and using the Jira MCP Server.

---

## 📋 Documents Overview

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **jira-mcp-server-design.md** | Complete design spec | Planning phase |
| **jira-mcp-server-implementation-example.md** | Code examples | Implementation phase |
| **jira-mcp-server-decision-guide.md** | Decision guidance | Architecture decisions |
| **jira-mcp-server-quick-reference.md** | This file! | Quick lookup |

---

## 🚀 Quick Start (5 Minutes)

### 1. Get Jira API Token

```bash
# Visit and create token:
https://id.atlassian.com/manage-profile/security/api-tokens

# Name it: "MCP Server"
# Copy the token (shown only once!)
```

### 2. Create Project

```bash
mkdir jira-mcp-server
cd jira-mcp-server

# Copy full implementation from jira-mcp-server-implementation-example.md
# Or start with skeleton and build incrementally
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install mcp httpx pydantic pydantic-settings python-dotenv
```

### 4. Configure

```bash
# Create .env file
cat > .env << EOF
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=PROJ
LOG_LEVEL=INFO
EOF
```

### 5. Test Connection

```python
# test_connection.py
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def test():
    auth = (os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
    url = f"{os.getenv('JIRA_URL')}/rest/api/2/myself"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, auth=auth)
        print(f"Status: {response.status_code}")
        print(f"User: {response.json()['displayName']}")

asyncio.run(test())
```

```bash
python test_connection.py
# Should print: Status: 200, User: Your Name
```

---

## 🛠️ MCP Tools Cheat Sheet

### Tool Signatures

```python
# 1. List tickets
list_my_tickets(
    status: Optional[str] = None,
    project: Optional[str] = None,
    max_results: int = 50
) -> List[Ticket]

# 2. Get ticket
get_ticket(
    ticket_key: str,
    include_comments: bool = True,
    include_attachments: bool = False
) -> TicketDetail

# 3. Get highest priority
get_highest_priority_ticket(
    exclude_status: List[str] = ["Closed", "Done"],
    project: Optional[str] = None
) -> TicketDetail

# 4. Update status
update_ticket_status(
    ticket_key: str,
    status: str,
    comment: Optional[str] = None
) -> UpdateResult

# 5. Update description
update_ticket_description(
    ticket_key: str,
    description: str,
    append: bool = False
) -> UpdateResult

# 6. Add comment
add_ticket_comment(
    ticket_key: str,
    comment: str,
    visibility: str = "public"
) -> CommentResult

# 7. Analyze ticket (optional)
analyze_ticket(
    ticket_key: str
) -> TicketAnalysis
```

---

## 📊 Jira API Endpoints Reference

### Core Endpoints

| Action | Method | Endpoint | Example |
|--------|--------|----------|---------|
| Search | GET | `/rest/api/2/search` | `?jql=assignee=currentUser()` |
| Get Issue | GET | `/rest/api/2/issue/{key}` | `/rest/api/2/issue/PROJ-123` |
| Update Issue | PUT | `/rest/api/2/issue/{key}` | Body: `{"fields": {...}}` |
| Get Transitions | GET | `/rest/api/2/issue/{key}/transitions` | Returns available transitions |
| Transition | POST | `/rest/api/2/issue/{key}/transitions` | Body: `{"transition": {"id": "11"}}` |
| Add Comment | POST | `/rest/api/2/issue/{key}/comment` | Body: `{"body": "text"}` |

### Common Fields

```python
COMMON_FIELDS = [
    "summary",          # Ticket title
    "description",      # Full description
    "status",          # Current status
    "priority",        # Priority level
    "assignee",        # Who it's assigned to
    "reporter",        # Who created it
    "created",         # Creation date
    "updated",         # Last update date
    "labels",          # Tags
    "components",      # Components
    "comment",         # Comments
    "attachment",      # Attachments
    "issuelinks",      # Linked issues
]
```

---

## 🔍 JQL Examples

### Common Queries

```jql
# My open tickets
assignee = currentUser() AND status != Closed

# My tickets in progress
assignee = currentUser() AND status = "In Progress"

# Highest priority
assignee = currentUser() AND status != Closed ORDER BY priority DESC

# Specific project
project = PROJ AND assignee = currentUser()

# Created recently
assignee = currentUser() AND created >= -7d

# Multiple statuses
assignee = currentUser() AND status IN ("To Do", "In Progress")

# By priority
assignee = currentUser() AND priority = High

# With label
assignee = currentUser() AND labels = "backend"

# Updated recently
assignee = currentUser() AND updated >= -1d ORDER BY updated DESC

# Complex query
project = PROJ 
  AND assignee = currentUser() 
  AND status != Closed 
  AND priority IN (High, Highest)
  ORDER BY priority DESC, created ASC
```

---

## 🔐 Authentication Examples

### Jira Cloud (API Token)

```python
import httpx
import base64

email = "user@example.com"
api_token = "your-api-token"

# Method 1: httpx basic auth
auth = (email, api_token)
async with httpx.AsyncClient() as client:
    response = await client.get(url, auth=auth)

# Method 2: Manual header
credentials = f"{email}:{api_token}"
encoded = base64.b64encode(credentials.encode()).decode()
headers = {"Authorization": f"Basic {encoded}"}
async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=headers)
```

### Jira Server (Basic Auth)

```python
username = "jdoe"
password = "password"

auth = (username, password)
async with httpx.AsyncClient() as client:
    response = await client.get(url, auth=auth)
```

### Jira Server (Personal Access Token)

```python
token = "your-personal-access-token"

headers = {"Authorization": f"Bearer {token}"}
async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=headers)
```

---

## 📝 Response Formats

### Ticket Summary

```json
{
  "key": "PROJ-123",
  "summary": "Implement user authentication",
  "status": "In Progress",
  "priority": "High",
  "assignee": "John Doe",
  "created": "2025-11-01T10:00:00Z",
  "updated": "2025-11-05T14:30:00Z"
}
```

### Ticket Detail

```json
{
  "key": "PROJ-123",
  "summary": "Implement user authentication",
  "description": "Add OAuth2 authentication to the API...",
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

### Ticket Analysis

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
      "JWT token generation"
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

---

## ⚠️ Common Issues & Solutions

### Issue: Authentication Failed (401)

```
Error: 401 Unauthorized
```

**Solutions:**
1. Verify API token is correct
2. Check email format (must match Jira account)
3. Ensure token hasn't expired
4. For Server: verify username/password
5. Check if account is active

### Issue: Ticket Not Found (404)

```
Error: 404 Not Found
```

**Solutions:**
1. Verify ticket key format: `PROJECT-123` (uppercase)
2. Check if ticket exists
3. Verify user has permission to view ticket
4. Check if ticket was deleted

### Issue: Cannot Transition (400)

```
Error: Cannot transition to status 'Done'
```

**Solutions:**
1. Get available transitions: `GET /issue/{key}/transitions`
2. Check workflow allows this transition
3. Verify required fields are set
4. Use correct transition ID, not status name

### Issue: Rate Limited (429)

```
Error: 429 Too Many Requests
```

**Solutions:**
1. Implement exponential backoff
2. Add caching to reduce API calls
3. Check rate limit headers
4. Upgrade Jira plan if needed

### Issue: Field Validation Error (400)

```
Error: Field 'description' is invalid
```

**Solutions:**
1. Check field format (some fields expect JSON)
2. Verify field exists on issue type
3. Check required fields are provided
4. Validate field values

---

## 🎯 Usage Examples

### Example 1: List My Tickets

**User Request:**
> "Show me my assigned Jira tickets"

**MCP Tool Call:**
```json
{
  "tool": "list_my_tickets",
  "arguments": {}
}
```

**AI Response:**
> "You have 5 assigned tickets:
> 1. PROJ-123 (High) - Implement user authentication [In Progress]
> 2. PROJ-124 (Medium) - Fix login bug [To Do]
> 3. PROJ-125 (Low) - Update documentation [In Progress]"

### Example 2: Get Specific Ticket

**User Request:**
> "Read ticket PROJ-123"

**MCP Tool Call:**
```json
{
  "tool": "get_ticket",
  "arguments": {
    "ticket_key": "PROJ-123",
    "include_comments": true
  }
}
```

**AI Response:**
> "PROJ-123: Implement user authentication
> 
> Description: Add OAuth2 authentication to the API. Should support login with email/password and return JWT tokens.
> 
> Status: In Progress
> Priority: High
> 
> Comments:
> - Jane Smith: Please use OAuth2 (2 days ago)"

### Example 3: Update Status

**User Request:**
> "Move PROJ-123 to Done"

**MCP Tool Call:**
```json
{
  "tool": "update_ticket_status",
  "arguments": {
    "ticket_key": "PROJ-123",
    "status": "Done",
    "comment": "Implementation completed and tested"
  }
}
```

**AI Response:**
> "✓ Updated PROJ-123 status from 'In Progress' to 'Done'"

### Example 4: Highest Priority

**User Request:**
> "What's my highest priority ticket?"

**MCP Tool Call:**
```json
{
  "tool": "get_highest_priority_ticket",
  "arguments": {
    "exclude_status": ["Closed", "Done"]
  }
}
```

**AI Response:**
> "Your highest priority ticket is:
> 
> PROJ-123 (Priority: High) - Implement user authentication
> Status: In Progress
> 
> Would you like me to continue working on this?"

---

## 📦 Project Structure

```
jira-mcp-server/
├── pyproject.toml              # Project config
├── requirements.txt            # Dependencies
├── README.md                   # Setup instructions
├── .env                        # Environment variables (not committed)
├── .env.example               # Example env vars
├── .gitignore                 # Git ignore patterns
│
├── src/
│   └── jira_mcp_server/
│       ├── __init__.py        # Package init
│       ├── __main__.py        # Entry point
│       ├── server.py          # MCP server setup
│       ├── config.py          # Configuration
│       ├── jira_client.py     # Jira API client
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── list_tickets.py
│       │   ├── get_ticket.py
│       │   ├── analyze_ticket.py
│       │   └── update_ticket.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── jql_builder.py
│           └── ticket_parser.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py            # Pytest config
    ├── test_jira_client.py
    ├── test_tools.py
    └── fixtures/
        └── sample_responses.json
```

---

## 🔧 Configuration Template

### .env
```bash
# Jira Instance
JIRA_URL=https://your-domain.atlassian.net

# Authentication (Cloud)
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Or Authentication (Server)
# JIRA_USERNAME=your-username
# JIRA_PASSWORD=your-password

# Optional
JIRA_PROJECT_KEY=PROJ
JIRA_MAX_RESULTS=50
JIRA_TIMEOUT=30
LOG_LEVEL=INFO
```

### MCP Settings (Cursor)

Add to your MCP configuration:

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

---

## 📚 Useful Links

### Jira API Documentation
- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Jira Server REST API v2](https://docs.atlassian.com/software/jira/docs/api/REST/latest/)
- [JQL Reference](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [API Rate Limits](https://developer.atlassian.com/cloud/jira/platform/rate-limiting/)

### Authentication
- [Create API Token](https://id.atlassian.com/manage-profile/security/api-tokens)
- [Basic Auth Guide](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)
- [Personal Access Tokens](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)

### MCP Resources
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

---

## ✅ Implementation Checklist

### Phase 1: MVP
- [ ] Create project structure
- [ ] Set up configuration management
- [ ] Implement Jira API client
- [ ] Create `list_my_tickets` tool
- [ ] Create `get_ticket` tool
- [ ] Test with real Jira instance
- [ ] Document setup process

### Phase 2: Core Features
- [ ] Add `update_ticket_status` tool
- [ ] Add `add_ticket_comment` tool
- [ ] Implement error handling
- [ ] Add input validation
- [ ] Write unit tests
- [ ] Add logging

### Phase 3: Enhanced Features
- [ ] Add `get_highest_priority_ticket` tool
- [ ] Implement ticket analysis
- [ ] Add caching layer
- [ ] Performance optimization
- [ ] Integration tests
- [ ] Documentation updates

### Phase 4: Production Ready
- [ ] Security review
- [ ] Add monitoring
- [ ] Create Docker image
- [ ] Set up CI/CD
- [ ] Load testing
- [ ] Team onboarding docs

---

## 🚦 Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jira_mcp_server

# Run specific test
pytest tests/test_jira_client.py::test_search_issues

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run and show print statements
pytest -s
```

---

## 🎓 Key Concepts

### MCP (Model Context Protocol)
- Protocol for AI assistants to access external tools
- Server exposes "tools" that AI can call
- Tools have defined input schemas and output formats

### JQL (Jira Query Language)
- SQL-like language for querying Jira
- Used in search endpoints
- Supports filtering, sorting, pagination

### Jira Transitions
- Workflows define allowed status changes
- Must use transition ID, not status name directly
- Different issue types may have different workflows

### Rate Limiting
- Jira Cloud: 10-25 requests/second
- Server: Configurable
- Use caching and batching to stay within limits

---

## 💡 Best Practices

1. **Always validate ticket keys** - Use regex: `^[A-Z]+-\d+$`
2. **Cache frequently accessed data** - Reduce API calls
3. **Use specific field lists** - Don't fetch unnecessary data
4. **Implement retry logic** - Handle transient failures
5. **Log sanitized data** - Never log credentials
6. **Use environment variables** - For all configuration
7. **Test with real Jira** - Use sandbox/test instance
8. **Document JQL queries** - They can be complex
9. **Handle workflow variations** - Different projects have different workflows
10. **Monitor API usage** - Stay within rate limits

---

## 🎯 Next Steps

1. **Choose Implementation Language** - Python recommended
2. **Set Up Development Environment** - Install dependencies
3. **Get Jira Credentials** - API token or credentials
4. **Build MVP** - Core tools first
5. **Test Thoroughly** - With real Jira instance
6. **Iterate Based on Usage** - Add features as needed
7. **Document Everything** - Setup, usage, troubleshooting
8. **Share with Team** - Get feedback early

---

**Need Help?**

- Design: See `jira-mcp-server-design.md`
- Code Examples: See `jira-mcp-server-implementation-example.md`
- Decisions: See `jira-mcp-server-decision-guide.md`
- Quick Ref: This file!

**Happy Building! 🚀**

