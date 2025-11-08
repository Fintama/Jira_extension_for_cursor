# 🔧 Jira MCP for Cursor

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-109%20passing-brightgreen.svg)](tests/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Seamless Jira integration for Cursor IDE through the Model Context Protocol (MCP). Manage Jira tickets directly from your AI coding assistant with one-time secure configuration.

---

## ✨ Features

- 🎯 **List & Search** - View all your assigned tickets with filters
- 📖 **Read Details** - Get complete ticket information including comments
- 🔍 **Smart Analysis** - Extract requirements and acceptance criteria automatically
- ⚡ **Quick Access** - Find your highest priority ticket instantly
- ✏️ **Update Tickets** - Change status, update descriptions, add comments
- 🔐 **Secure** - One-time encrypted configuration, credentials never in plaintext
- 🎨 **Beautiful Setup** - Web-based wizard with guided configuration
- 🚀 **Auto-Install** - Automatically integrates with Cursor IDE

---

## 🚀 Quick Start

### Installation

```bash
# Install via pip
pip install jira-mcp-cursor
```

### Configuration

```bash
# Launch setup wizard (opens in browser)
jira-mcp configure
```

The wizard will guide you through:
1. Enter your Jira URL (e.g., `https://your-domain.atlassian.net`)
2. Enter your email
3. Enter your API token ([Get one here](https://id.atlassian.com/manage-profile/security/api-tokens))
4. Test connection
5. Save encrypted configuration

### Install to Cursor

```bash
# Automatically add to Cursor's MCP settings
jira-mcp install

# Restart Cursor IDE
```

### Start Using

Open Cursor and try:
- "Show me my assigned Jira tickets"
- "Get details for ticket PROJ-123"
- "What's my highest priority ticket?"
- "Analyze ticket PROJ-456 and extract requirements"
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
│  │  7 MCP Tools                      │  │
│  │  - List, Get, Analyze            │  │
│  │  - Update Status/Description     │  │
│  │  - Add Comments                  │  │
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

- **[User Guide](docs/USER_GUIDE.md)** - Detailed setup and usage
- **[API Reference](docs/API_REFERENCE.md)** - Complete tool documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
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
