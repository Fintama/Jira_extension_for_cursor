# Jira MCP Server - Complete Setup Guide

## 📋 Table of Contents

- [What is MCP?](#what-is-mcp)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Cursor Configuration](#cursor-configuration)
- [Verification](#verification)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)

---

## 🤔 What is MCP?

**MCP (Model Context Protocol)** is a standardized protocol that allows AI assistants to interact with external tools and data sources.

### **What Our Jira MCP Server Provides:**

- **11 Tools** - Functions the AI can execute (create tickets, update status, etc.)
- **Direct Jira Integration** - AI can interact with your Jira instance
- **Secure Communication** - STDIO-based, no network exposure

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CURSOR IDE                              │
│                                                             │
│  Reads: .cursor/mcp.json                                   │
│  Spawns: Python process when needed                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ STDIN/STDOUT (JSON-RPC)
                      │ No HTTP, no network ports!
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              JIRA MCP SERVER (Python Process)               │
│                                                             │
│  • Runs as: python -m jira_mcp_cursor.cli serve           │
│  • Receives tool calls via STDIN                           │
│  • Executes Python code (11 tools)                        │
│  • Calls Jira REST API                                     │
│  • Returns results via STDOUT                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTPS REST API
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  JIRA CLOUD / SERVER                        │
│            (your-domain.atlassian.net)                      │
└─────────────────────────────────────────────────────────────┘
```

### **Communication Protocol:**

```
User: "Show me my Jira tickets"
  ↓
Cursor AI: Decides to use list_my_tickets tool
  ↓
Cursor → Python Process (STDIN):
  {"method":"tools/call","params":{"name":"list_my_tickets"}}
  ↓
Python Process: Calls Jira API
  ↓
Python Process → Cursor (STDOUT):
  {"result":{"tickets":[...]}}
  ↓
Cursor AI: Formats and presents results to user
```

---

## ✅ Prerequisites

### 1. **Python 3.11+**
```bash
python --version  # or python3 --version
# Should show: Python 3.11.x or higher
```

### 2. **Cursor IDE**
- Download from [cursor.sh](https://cursor.sh)
- Version with MCP support (2024+)

### 3. **Jira Account**
You need:
- Jira instance URL (e.g., `https://your-domain.atlassian.net`)
- Email address
- API Token - [Generate here](https://id.atlassian.com/manage-profile/security/api-tokens)

---

## 📦 Installation

### Step 1: Install the Package

```bash
# Clone or download the repository
cd /path/to/jira-mcp-cursor

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install the package
pip install -e .
```

### Step 2: Configure Jira Credentials

Run the interactive configuration wizard:

```bash
jira-mcp configure
```

This will:
1. Open a web browser with a setup wizard
2. Prompt for your Jira URL, email, and API token
3. Test the connection
4. Save encrypted credentials to `~/.jira-mcp/config.json`

**Manual Configuration (Alternative):**

Create `~/.jira-mcp/config.json`:
```json
{
  "jira_url": "https://your-domain.atlassian.net",
  "jira_email": "your-email@example.com",
  "jira_api_token": "your-api-token-here",
  "default_project": "PROJ"
}
```

### Step 3: Test the Installation

```bash
# Test connection
jira-mcp config test

# Should show:
# ✅ Connected! User: Your Name
```

---

## 🎯 Cursor Configuration

### Method 1: Automatic Installation (Recommended)

```bash
jira-mcp install
```

This automatically:
- Detects your Cursor configuration directory
- Creates `.cursor/mcp.json` in your project
- Configures the server with correct paths

**Then restart Cursor!**

---

### Method 2: Manual Configuration

#### Step 1: Create MCP Configuration File

In your project root, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": [
        "-m",
        "jira_mcp_cursor.cli",
        "serve"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/jira-mcp-cursor",
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-jira-api-token-here",
        "JIRA_PROJECT_KEY": "SWI"
      }
    }
  }
}
```

**Important:**
- Replace `/absolute/path/to/venv/bin/python` with your actual venv Python path
- Replace `/absolute/path/to/jira-mcp-cursor` with your project path
- Replace Jira credentials with your actual values
- Set `JIRA_PROJECT_KEY` to your default project (e.g., "SWI")

⚠️ **SECURITY WARNING:**
- `.cursor/mcp.json` contains **sensitive credentials** (API tokens)
- This file is **gitignored** and will NOT be committed
- **Never** commit this file to version control
- Use `.cursor/mcp.json.example` as a template for others

**Why credentials in mcp.json?**
- ✅ **Single configuration file** - Everything in one place
- ✅ **Environment variables** - Server loads from env vars automatically
- ✅ **Per-project configuration** - Different projects can use different Jira accounts
- ✅ **Easy to edit** - Can edit directly in Cursor's MCP settings UI

**Find your Python path:**
```bash
which python  # Linux/Mac
where python  # Windows
```

#### Step 2: Verify Configuration File Location

**Cursor looks for MCP config in:**
```
<project-root>/.cursor/mcp.json
```

**NOT** in:
- `~/.config/Cursor/User/mcp_settings.json` ❌
- Global Cursor settings ❌

---

### Method 3: Using Cursor UI

1. Open Cursor Settings: `Ctrl+Shift+P` → "Cursor Settings"
2. Navigate to **"Tools & MCP"** section
3. Click **"Add Custom MCP"** or **"New MCP Server"**
4. If `.cursor/mcp.json` exists, it should auto-detect
5. Toggle the server **ON** (green switch)

---

## ✅ Verification

### Step 1: Check MCP Server is Detected

1. Open Cursor Settings (`Ctrl+,` or `Cmd+,`)
2. Go to **"Tools & MCP"**
3. You should see:
   ```
   Installed MCP Servers

   jira                          [ON]
   11 tools
   ```

If it shows **"No tools, prompts, or resources"**, see [Troubleshooting](#troubleshooting).

### Step 2: Check Process is Running

```bash
ps aux | grep "jira_mcp_cursor"
```

Should show:
```
python -m jira_mcp_cursor.cli serve --config ...
```

### Step 3: Test with AI

Open a chat in Cursor and ask:
```
Show me my Jira tickets
```

The AI should use the MCP tool to fetch and display your actual Jira tickets!

---

## 🎯 Default Project Context

**Recommended:** Set a default project to scope ticket operations.

### Why Use Default Project?

When working on a specific project (e.g., "SWI"), you typically want:
- **All ticket operations** scoped to your project
- **New tickets created** in that project by default
- **Simpler commands** without repeating project name

### Configuration

Set in `.cursor/mcp.json`:

```json
{
  "env": {
    "JIRA_PROJECT_KEY": "SWI"
  }
}
```

### How It Works

**`JIRA_PROJECT_KEY` (Project Context):**
- ✅ `list_my_tickets` → Only shows tickets in SWI project
- ✅ `get_highest_priority_ticket` → Only searches SWI project
- ✅ `create_issue` → Creates in SWI if no project specified
- ✅ `list_tickets_by_creator` → Scoped to SWI by default
- ✅ You can still **override** by specifying a different project

**Examples:**
```
Without default project:
  "List my tickets in project SWI"
  "Create story in project SWI: Implement auth"

With default project (SWI):
  "List my tickets"              ← Auto-scoped to SWI
  "Create story: Implement auth" ← Auto-created in SWI
```

### Finding Users

**User search works best with names:**
- ✅ "Find user andrea" → Finds Andrea Panzitta
- ✅ "Show users named fahed" → Finds Fahed Ben Tej
- ✅ "List all users" → Shows all accessible users
- ❌ Domain search (@company.com) doesn't work well in Jira API

---

## 🔧 How It Works

### Available Tools (14 Total)

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `list_my_tickets` | List all tickets assigned to you | "Show me my Jira tickets" |
| `list_tickets_by_creator` | List tickets created by a user | "Show tickets created by john@..." |
| `get_ticket` | Get detailed ticket information | "Get details for SWI-123" |
| `get_highest_priority_ticket` | Find your highest priority ticket | "What's my top priority?" |
| `get_subtasks` | View all subtasks of a ticket | "Show subtasks of SWI-500" |
| `list_users` | Search for Jira users | "Find user named John" |
| `analyze_ticket` | Extract requirements and acceptance criteria | "Analyze ticket SWI-456" |
| `create_issue` | Create new stories, tasks, or bugs | "Create a story: Implement auth" |
| `create_subtask` | Create subtasks under a parent | "Break SWI-500 into subtasks" |
| `update_ticket_status` | Change ticket status | "Move SWI-123 to In Progress" |
| `update_ticket_description` | Update ticket description | "Update description of SWI-123" |
| `add_ticket_comment` | Add comments to tickets | "Comment on SWI-123: Done" |
| `assign_issue` | Assign tickets to users | "Assign SWI-123 to john@..." |
| `delete_issue` | Delete tickets permanently | "Delete SWI-123" ⚠️ |

### MCP Protocol Flow

```
1. INITIALIZATION (When Cursor Starts)
   Cursor → Server: {"method": "initialize"}
   Server → Cursor: {"capabilities": {"tools": true}}

2. TOOL DISCOVERY
   Cursor → Server: {"method": "tools/list"}
   Server → Cursor: {"tools": [11 tool definitions]}

3. TOOL EXECUTION (When you ask AI)
   User: "Show me my tickets"
   AI: Decides to use list_my_tickets
   Cursor → Server: {"method": "tools/call", "params": {...}}
   Server: Executes Python code
   Server: Calls Jira REST API
   Server → Cursor: {"result": {...}}
   AI: Presents results to user
```

### What Happens When You Ask "Show Me My Tickets"

```
Step 1: You ask in chat
  ↓
Step 2: Cursor's AI analyzes request
  - Recognizes this is a Jira query
  - Checks available MCP tools
  - Finds: list_my_tickets tool
  ↓
Step 3: AI decides to call the tool
  - Constructs parameters: {"max_results": 10}
  ↓
Step 4: Cursor sends to MCP Server (via STDIN)
  {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "list_my_tickets",
      "arguments": {"max_results": 10}
    }
  }
  ↓
Step 5: Python process executes
  - Reads from ~/.jira-mcp/config.json
  - Creates JiraClient with credentials
  - Calls Jira API: GET /rest/api/2/search
  - Formats response
  ↓
Step 6: Returns result (via STDOUT)
  {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
      "tickets": [
        {"key": "SWI-123", "summary": "...", ...},
        ...
      ]
    }
  }
  ↓
Step 7: AI formats and presents to you
  "Here are your Jira tickets:
   - SWI-123: Feature implementation
   - SWI-124: Bug fix
   ..."
```

---

## 🐛 Troubleshooting

### Issue: "No tools, prompts, or resources"

**Cause:** Server started but didn't advertise capabilities correctly.

**Solution:**
1. Check that you have the latest code with `ToolsCapability`
2. Look for this in `src/jira_mcp_cursor/server/server.py`:
   ```python
   capabilities=ServerCapabilities(
       tools=ToolsCapability(listChanged=True),
   )
   ```
3. Reload Cursor: `Ctrl+Shift+P` → "Reload Window"

---

### Issue: MCP Server Not Appearing

**Cause:** `.cursor/mcp.json` not in the right location.

**Solution:**
1. Verify file location:
   ```bash
   ls -la .cursor/mcp.json  # Should exist in project root
   ```
2. File should be in: `<your-project>/.cursor/mcp.json`
3. NOT in: `~/.config/Cursor/User/`

---

### Issue: "Command not found: jira-mcp"

**Cause:** Package not installed or venv not activated.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall package
pip install -e .

# Verify installation
which jira-mcp
```

---

### Issue: "Authentication failed"

**Cause:** Invalid Jira credentials.

**Solution:**
1. Verify credentials:
   ```bash
   jira-mcp config test
   ```
2. Regenerate API token at: https://id.atlassian.com/manage-profile/security/api-tokens
3. Reconfigure:
   ```bash
   jira-mcp configure
   ```

---

### Issue: Python Process Not Starting

**Cause:** Incorrect paths in `.cursor/mcp.json`.

**Solution:**
1. Use absolute paths (not relative):
   ```json
   {
     "command": "/full/path/to/venv/bin/python",
     "env": {
       "PYTHONPATH": "/full/path/to/jira-mcp-cursor"
     }
   }
   ```
2. Test manually:
   ```bash
   /full/path/to/venv/bin/python -m jira_mcp_cursor.cli serve
   ```

---

### Debugging: View Server Logs

**Check if process is running:**
```bash
ps aux | grep jira_mcp_cursor
```

**Test server manually:**
```bash
source venv/bin/activate
python -m jira_mcp_cursor.cli serve --config ~/.jira-mcp/config.json
# Should start and wait for input
# Ctrl+C to exit
```

**Send test request:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \
  python -m jira_mcp_cursor.cli serve --config ~/.jira-mcp/config.json
```

---

## 🎯 Quick Start Checklist

- [ ] Python 3.11+ installed
- [ ] Cursor IDE installed
- [ ] Jira account with API token
- [ ] Package installed: `pip install -e .`
- [ ] Credentials configured: `jira-mcp configure`
- [ ] Connection tested: `jira-mcp config test`
- [ ] MCP config created: `.cursor/mcp.json` in project root
- [ ] Cursor restarted/reloaded
- [ ] Server visible in Tools & MCP settings
- [ ] Shows "11 tools" (not "No tools")
- [ ] Process running: `ps aux | grep jira_mcp`
- [ ] Tested with AI: "Show me my Jira tickets"

---

## 📚 Related Documentation

- [User Guide](USER_GUIDE.md) - How to use the tools
- [API Reference](API_REFERENCE.md) - Complete tool documentation
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [README](../README.md) - Project overview

---

## 🔗 Useful Links

- **MCP Specification:** https://modelcontextprotocol.io/
- **Jira REST API:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Cursor IDE:** https://cursor.sh
- **API Token:** https://id.atlassian.com/manage-profile/security/api-tokens

---

## 💡 Understanding MCP Concepts

### What are Tools?
**Tools** are executable functions that the AI can call. Each tool:
- Has a **name** (e.g., `create_issue`)
- Has a **description** (AI reads this to know when to use it)
- Has an **input schema** (defines parameters)
- Executes **Python code** on your behalf
- Returns **results** to the AI

### What are Prompts? (Not Implemented)
**Prompts** are reusable conversation templates that provide structured instructions.

**How they would work:**
```
User: "Generate my weekly standup"
  ↓
AI sees available prompt: "weekly_standup"
  ↓
AI invokes: get_prompt("weekly_standup", assignee="you")
  ↓
AI receives template:
  "Generate a standup report including:
   1. Completed tickets this week
   2. In-progress tickets
   3. Next week's priorities"
  ↓
AI follows the template structure
  ↓
AI uses Tools (list_my_tickets, etc.) to gather data
  ↓
AI formats response according to template
```

**Key Point:** Prompts are **NOT** added to the system prompt automatically. They're **invoked by name** when the AI recognizes a matching request or when you explicitly select them from a UI menu.

**Example Use Cases:**
- "Weekly standup" - Consistent report format
- "Feature breakdown" - Structured analysis process
- "Code review checklist" - Same steps each time

Our server focuses on **Tools** (executable actions) rather than Prompts (conversation templates) because your workflows are flexible and conversational.

### What are Resources? (Not Implemented)
**Resources** are data sources the AI can read:
- Read-only access to data
- Different from Tools (which execute actions)
- Examples: documentation, datasets, logs
- Optional - our server uses Tools only

### Why STDIO Instead of HTTP?
- **Security:** No network exposure, no ports to protect
- **Simplicity:** Cursor manages process lifecycle
- **Performance:** Direct IPC, no network overhead
- **Isolation:** Each project gets its own process

---

**Need help?** Open an issue on GitHub or check the troubleshooting guide!

