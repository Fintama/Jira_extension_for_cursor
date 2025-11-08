# 🔧 Jira MCP for Cursor

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-109%20passing-brightgreen.svg)](tests/)
[![MCP Tools](https://img.shields.io/badge/MCP%20tools-14-blue.svg)](docs/API_REFERENCE.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Seamless Jira integration for Cursor IDE through the Model Context Protocol (MCP). Create, read, and update Jira tickets directly from your AI coding assistant with complete workflow support.

---

## ✨ Features

- 🎯 **List & Search** - View tickets by assignee, creator, project, or status
- 📖 **Read Details** - Get complete ticket information including comments and subtasks
- 👥 **User Management** - List and search Jira users for assignment
- 🔍 **Smart Analysis** - Extract requirements and acceptance criteria automatically
- ⚡ **Quick Access** - Find your highest priority ticket instantly
- ✨ **Create Workflows** - Create stories, subtasks, and complete feature breakdowns
- ✏️ **Update Tickets** - Change status, update descriptions, add comments, assign users
- 🗑️ **Manage Lifecycle** - Delete test tickets and clean up your workspace
- 🔐 **Secure** - One-time encrypted configuration, credentials never in plaintext
- 🎨 **Beautiful Setup** - Web-based wizard with guided configuration
- 🚀 **Auto-Install** - Automatically integrates with Cursor IDE

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Cursor IDE
- Jira account with API token ([Get one here](https://id.atlassian.com/manage-profile/security/api-tokens))

### Installation (3 Steps)

#### 1. Install the Package

```bash
# Clone the repository
git clone https://github.com/Fintama/Jira_extension_for_cursor.git
cd jira-mcp-cursor

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

#### 2. Configure Jira Credentials

```bash
# Launch setup wizard (opens in browser)
jira-mcp configure
```

The wizard will guide you through:
1. Enter your Jira URL (e.g., `https://your-domain.atlassian.net`)
2. Enter your email
3. Enter your API token
4. Test connection ✅
5. Save encrypted configuration to `~/.jira-mcp/config.json`

#### 3. Add to Cursor

```bash
# Automatically create .cursor/mcp.json in your project
jira-mcp install
```

⚠️ **Security Note:** The `.cursor/mcp.json` file contains your API token and is **automatically gitignored**. Never commit this file!

This creates `.cursor/mcp.json` with your credentials and default project:
```json
{
  "mcpServers": {
    "jira": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "jira_mcp_cursor.cli", "serve"],
      "env": {
        "PYTHONPATH": "/path/to/project",
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token",
        "JIRA_PROJECT_KEY": "SWI"
      }
    }
  }
}
```

**💡 Default Project Context:**

**`JIRA_PROJECT_KEY`** - Scopes ticket operations to your project:
- List tickets → Only shows SWI tickets
- Create issues → Defaults to SWI project
- Simplifies: "Create a story" (auto-creates in SWI)

**User Search Tip:**
Search by name (e.g., "andrea", "john") to find teammates. Leave empty to list all available users.

#### 4. Restart Cursor

- **Reload Window:** `Ctrl+Shift+P` → "Reload Window"
- Or restart Cursor completely

#### 5. Verify Installation

1. Open Cursor Settings → **Tools & MCP**
2. You should see **"jira"** server with **"14 tools"**
3. Toggle should be **ON** (green)

### Start Using

Open Cursor chat and try:
- "Show me my assigned Jira tickets"
- "Get details for ticket PROJ-123"
- "What's my highest priority ticket?"
- "Analyze ticket PROJ-456 and extract requirements"
- "Create a story in project SWI: Implement user authentication"
- "Break down SWI-500 into 3 subtasks for backend, frontend, and testing"
- "Move PROJ-123 to In Progress"
- "Add a comment to PROJ-789: Implementation completed"

---

## 📋 Available Tools

### 1. `list_my_tickets`
List all tickets assigned to you with optional filters.

**Usage:** "Show me my Jira tickets" or "List my tickets in project PROJ"

**Parameters:**
- `status` (optional) - Filter by status (e.g., "In Progress", "To Do")
- `project` (optional) - Filter by project key
- `max_results` (optional) - Maximum number of results (default: 50)

### 2. `get_ticket`
Get detailed information about a specific ticket.

**Usage:** "Get details for ticket PROJ-123" or "Show me PROJ-456"

**Parameters:**
- `ticket_key` (required) - Jira ticket key (e.g., "PROJ-123")
- `include_comments` (optional) - Include comments (default: true)

### 3. `get_highest_priority_ticket`
Find your highest priority ticket.

**Usage:** "What's my highest priority ticket?" or "Show me the most important work"

**Parameters:**
- `exclude_status` (optional) - Statuses to exclude (default: ["Closed", "Done"])
- `project` (optional) - Filter by project key

### 4. `analyze_ticket`
Analyze ticket and extract structured implementation details.

**Usage:** "Analyze ticket PROJ-123" or "Extract requirements from PROJ-456"

**Parameters:**
- `ticket_key` (required) - Jira ticket key

**Returns:**
- Requirements list
- Acceptance criteria
- Technical notes
- Dependencies
- Complexity estimate

### 5. `update_ticket_status`
Transition ticket to a new status.

**Usage:** "Move PROJ-123 to In Progress" or "Mark PROJ-456 as Done"

**Parameters:**
- `ticket_key` (required) - Jira ticket key
- `status` (required) - Target status name
- `comment` (optional) - Add comment with status change

### 6. `update_ticket_description`
Update ticket description.

**Usage:** "Update PROJ-123 description to..." or "Append notes to PROJ-456"

**Parameters:**
- `ticket_key` (required) - Jira ticket key
- `description` (required) - New description text
- `append` (optional) - Append instead of replace (default: false)

### 7. `add_ticket_comment`
Add a comment to a ticket.

**Usage:** "Add comment to PROJ-123: Implementation complete"

**Parameters:**
- `ticket_key` (required) - Jira ticket key
- `comment` (required) - Comment text

### 8. `create_issue`
Create a new Jira issue (Story, Task, Bug, etc.).

**Usage:** "Create a story in project SWI: Implement authentication" or "Create a task in PROJ for bug fixes"

**Parameters:**
- `project_key` (required) - Project key (e.g., "SWI", "PROJ")
- `summary` (required) - Issue title/summary
- `description` (required) - Detailed description
- `issue_type` (optional) - Type: Task, Story, Bug, Epic (default: Task)
- `priority` (optional) - Priority: Highest, High, Medium, Low, Lowest
- `assignee` (optional) - Account ID or email of assignee
- `labels` (optional) - List of labels
- `parent_key` (optional) - Parent issue key for stories under epics

### 9. `create_subtask`
Create a subtask under a parent issue.

**Usage:** "Break down SWI-500 into subtasks" or "Create subtask under PROJ-123 for database schema"

**Parameters:**
- `parent_key` (required) - Parent issue key (e.g., "SWI-501")
- `summary` (required) - Subtask title
- `description` (required) - Detailed description
- `assignee` (optional) - Account ID or email of assignee
- `priority` (optional) - Priority

### 10. `get_subtasks`
Get all subtasks of a parent issue.

**Usage:** "Show me subtasks of SWI-500" or "List all subtasks for PROJ-123"

**Parameters:**
- `issue_key` (required) - Parent issue key

### 11. `assign_issue`
Assign an issue to a user.

**Usage:** "Assign SWI-500 to john@example.com" or "Unassign PROJ-123"

**Parameters:**
- `issue_key` (required) - Issue key
- `assignee` (required) - Account ID or email (use "null" for unassigned, "-1" for automatic)

### 12. `list_users`
List and search for Jira users.

**Usage:** "Show me all Jira users" or "Find user named John"

**Parameters:**
- `query` (optional) - Search by name, email, or username
- `max_results` (optional) - Maximum number of results (default: 50)

### 13. `list_tickets_by_creator`
List tickets created by a specific user.

**Usage:** "Show me tickets created by john@example.com" or "List all tickets I created"

**Parameters:**
- `creator` (required) - Creator email, username, or "currentUser()"
- `project` (optional) - Filter by project (uses default if not specified)
- `status` (optional) - Filter by status
- `max_results` (optional) - Maximum number of results (default: 50)

### 14. `delete_issue`
Delete a Jira issue permanently.

**Usage:** "Delete ticket SWI-123" or "Remove SWI-456 and all its subtasks"

**Parameters:**
- `issue_key` (required) - Issue key to delete
- `delete_subtasks` (optional) - Whether to delete subtasks (default: false)

⚠️ **Warning:** This action cannot be undone!

---

## 🔐 Security

- **Encrypted Storage** - Credentials encrypted with Fernet (AES-128)
- **File Permissions** - Config files set to 600 (owner-only access)
- **No Plaintext** - API tokens never stored in plaintext
- **Machine-Bound** - Encryption keys are machine-specific
- **Secure Transport** - All Jira communication over HTTPS

---

## 🛠️ Configuration

### Using the Wizard (Recommended)

```bash
jira-mcp configure
```

### Manual Configuration

Create `.env` file or set environment variables:

```bash
# Required
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Optional
JIRA_PROJECT_KEY=PROJ
JIRA_MAX_RESULTS=50
JIRA_TIMEOUT=30
JIRA_MAX_RETRIES=3
LOG_LEVEL=INFO
```

### Configuration Commands

```bash
# Show current config (sanitized)
jira-mcp config show

# Test connection
jira-mcp config test

# Reset configuration
jira-mcp config reset
```

---

## 📦 CLI Commands

```bash
# Configuration
jira-mcp configure          # Launch setup wizard
jira-mcp config show        # Display current config
jira-mcp config test        # Test Jira connection
jira-mcp config reset       # Delete configuration

# Installation
jira-mcp install            # Add to Cursor
jira-mcp uninstall          # Remove from Cursor

# Server
jira-mcp serve              # Start MCP server (used by Cursor)

# Help
jira-mcp --help             # Show all commands
jira-mcp --version          # Show version
```

---

## 🔧 Troubleshooting

### "Authentication failed"
- Verify API token is correct and not expired
- Check email address matches your Jira account
- Generate new token at https://id.atlassian.com/manage-profile/security/api-tokens

### "Ticket not found"
- Verify ticket key format (e.g., PROJ-123)
- Check you have permission to view the ticket
- Ensure you're connected to the correct Jira instance

### "Cannot transition ticket"
- Use `get_transitions()` to see available transitions
- Check workflow allows this status change
- Verify you have permission for this transition

### "Rate limit exceeded"
- Wait a few seconds and retry (automatic with backoff)
- Reduce request frequency
- Consider caching frequently accessed data

For more detailed troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         AI Assistant (Cursor)           │
└──────────────┬──────────────────────────┘
               │ MCP Protocol (stdio/JSON-RPC)
┌──────────────▼──────────────────────────┐
│         Jira MCP Server                 │
│  ┌───────────────────────────────────┐  │
│  │  14 MCP Tools                     │  │
│  │  - Read: List, Get, Users        │  │
│  │  - Create: Issues, Subtasks      │  │
│  │  - Update: Status, Desc, Assign  │  │
│  │  - Delete: Remove Issues         │  │
│  │  - Analyze: Requirements         │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Jira API Client                 │  │
│  │  - Retry Logic (exponential)     │  │
│  │  - Error Handling                │  │
│  │  - Connection Pooling            │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │ HTTPS/REST
┌──────────────▼──────────────────────────┐
│         Jira Cloud/Server               │
└─────────────────────────────────────────┘
```

## 🔄 Workflow Example

**Feature Development Flow:**

```
1. PO creates Feature → "SWI-500: User Authentication"

2. AI breaks down feature:
   You: "Break down SWI-500 into implementation stories"
   AI: Creates 3 stories:
       - SWI-501: Backend Auth Service
       - SWI-502: Frontend Login UI
       - SWI-503: Integration Testing

3. Work on a story:
   You: "Let's work on SWI-501"
   You: "Break it into subtasks"
   AI: Creates:
       - SWI-501-1: Database schema
       - SWI-501-2: API endpoints
       - SWI-501-3: Unit tests

4. Implementation:
   You: "Start with SWI-501-1"
   AI: Updates status to "In Progress"
   AI: Adds comments as work progresses
   AI: Marks complete when done
```

**All tracked in Jira - no separate markdown files needed!**

---

## 💻 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Fintama/Jira_extension_for_cursor.git
cd jira-mcp-cursor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your Jira credentials
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/jira_mcp_cursor

# Run specific test file
pytest tests/test_tools.py -v

# Run CI-critical tests only
pytest tests/ -v -m ci_critical
```

### Code Quality

```bash
# Format code
black src/jira_mcp_cursor tests/

# Lint
ruff check src/jira_mcp_cursor tests/

# Type check
mypy src/jira_mcp_cursor/
```

---

## 📚 Documentation

### Getting Started
- **[MCP Setup Guide](docs/MCP_SETUP_GUIDE.md)** - ⭐ Complete MCP integration setup
- **[How It Works](docs/HOW_IT_WORKS.md)** - 🔍 Architecture and flow explained
- **[User Guide](docs/USER_GUIDE.md)** - Detailed setup and usage

### Reference
- **[API Reference](docs/API_REFERENCE.md)** - Complete tool documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Contributing
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [Cursor IDE](https://cursor.com/)
- Integrates with [Jira Cloud](https://www.atlassian.com/software/jira)

---

## 🔗 Links

- **Repository:** https://github.com/Fintama/Jira_extension_for_cursor
- **Issues:** https://github.com/Fintama/Jira_extension_for_cursor/issues
- **PyPI:** https://pypi.org/project/jira-mcp-cursor/
- **Jira API Docs:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/

---

**Made with ❤️ for developers who want to stay in their flow**
