# How Jira MCP Server Works - Complete Flow

## 🎯 What Happens When You Type "Show Me My Jira Tickets"

### The Complete Journey:

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: You Type in Cursor Chat                                │
│ "Show me my Jira tickets"                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Cursor AI (Me) Analyzes Your Request                   │
│                                                                 │
│ AI thinks:                                                      │
│ - "User wants to see Jira tickets"                            │
│ - "I have access to MCP tools from jira server"              │
│ - "I see a tool called 'list_my_tickets'"                    │
│ - "This tool's description matches what user wants"          │
│ - "I should call this tool with max_results parameter"       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Cursor Prepares Tool Call                              │
│                                                                 │
│ Creates JSON-RPC message:                                      │
│ {                                                              │
│   "jsonrpc": "2.0",                                           │
│   "id": 42,                                                   │
│   "method": "tools/call",                                     │
│   "params": {                                                 │
│     "name": "list_my_tickets",                               │
│     "arguments": {                                           │
│       "max_results": 10                                      │
│     }                                                         │
│   }                                                           │
│ }                                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Writes to STDIN
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Python MCP Server Process                              │
│ Process ID: 149683                                              │
│ Command: python -m jira_mcp_cursor.cli serve                   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 4.1: Receives JSON from STDIN                           │   │
│ │      Parses the JSON-RPC message                        │   │
│ └─────────────────────────────────────────────────────────┘   │
│                         │                                      │
│                         ↓                                      │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 4.2: Routes to Handler                                  │   │
│ │      Calls: handle_list_my_tickets(arguments, client)   │   │
│ └─────────────────────────────────────────────────────────┘   │
│                         │                                      │
│                         ↓                                      │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 4.3: JiraClient Executes                                │   │
│ │      • Loads config from ~/.jira-mcp/config.json       │   │
│ │      • Decrypts credentials                             │   │
│ │      • Creates HTTP request to Jira                     │   │
│ └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS REST API
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Jira Cloud API                                         │
│ https://fintama.atlassian.net/rest/api/2/search               │
│                                                                 │
│ Request:                                                       │
│ GET /rest/api/2/search?jql=assignee=currentUser()            │
│ Authorization: Basic base64(email:token)                      │
│                                                                 │
│ Response:                                                      │
│ {                                                              │
│   "issues": [                                                 │
│     {                                                         │
│       "key": "SWI-123",                                      │
│       "fields": {                                            │
│         "summary": "Implement feature X",                   │
│         "status": {"name": "In Progress"},                  │
│         ...                                                  │
│       }                                                       │
│     },                                                        │
│     ...                                                       │
│   ]                                                           │
│ }                                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Returns HTTP 200 + JSON
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Python Server Processes Response                       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 6.1: Parses Jira API response                           │   │
│ │      Extracts relevant fields                           │   │
│ └─────────────────────────────────────────────────────────┘   │
│                         │                                      │
│                         ↓                                      │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 6.2: Formats for MCP                                    │   │
│ │      Creates structured response                        │   │
│ │      {                                                  │   │
│ │        "tickets": [                                     │   │
│ │          {"key": "SWI-123", "summary": "...", ...}     │   │
│ │        ],                                               │   │
│ │        "total": 5                                       │   │
│ │      }                                                  │   │
│ └─────────────────────────────────────────────────────────┘   │
│                         │                                      │
│                         ↓                                      │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 6.3: Wraps in JSON-RPC Response                         │   │
│ │      {                                                  │   │
│ │        "jsonrpc": "2.0",                               │   │
│ │        "id": 42,                                       │   │
│ │        "result": {                                     │   │
│ │          "content": [                                  │   │
│ │            {                                           │   │
│ │              "type": "text",                          │   │
│ │              "text": "{\"tickets\":[...]}"           │   │
│ │            }                                           │   │
│ │          ]                                             │   │
│ │        }                                               │   │
│ │      }                                                 │   │
│ └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Writes to STDOUT
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Cursor Receives Response                               │
│                                                                 │
│ Reads from Python process STDOUT                               │
│ Parses JSON-RPC response                                       │
│ Extracts ticket data                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: AI (Me) Receives the Data                              │
│                                                                 │
│ I get:                                                         │
│ {                                                              │
│   "tickets": [                                                │
│     {"key": "SWI-123", "summary": "Implement feature X", ...},│
│     {"key": "SWI-124", "summary": "Fix bug Y", ...}          │
│   ],                                                          │
│   "total": 5                                                  │
│ }                                                             │
│                                                                 │
│ I format this nicely for you                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9: You See the Results                                    │
│                                                                 │
│ "Here are your 5 Jira tickets:                                │
│                                                                 │
│  1. SWI-123: Implement feature X                              │
│     Status: In Progress | Priority: High                      │
│                                                                 │
│  2. SWI-124: Fix bug Y                                        │
│     Status: To Do | Priority: Medium                          │
│                                                                 │
│  ..."                                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 The Complete Roundtrip

**Time breakdown:**
1. You type (0ms) → AI analyzes (100ms) → Tool call prepared (10ms)
2. JSON-RPC sent to Python process (1ms)
3. Python executes → Jira API call (200-500ms)
4. Response processed (10ms) → Sent back (1ms)
5. AI formats (100ms) → You see results

**Total: ~500-1000ms** from your question to seeing results!

---

## 💡 Why This Architecture?

### No HTTP Server Needed

**Traditional Approach:**
```
Cursor → HTTP → localhost:3000 → Python Server
           │
           └─ Need to manage ports
           └─ Security concerns
           └─ Process management complex
```

**MCP Approach (What We Built):**
```
Cursor → STDIN/STDOUT → Python Process
           │
           └─ No ports needed
           └─ Cursor manages process
           └─ Secure by default
```

### Process Lifecycle

```
CURSOR STARTS
  ↓
Reads .cursor/mcp.json
  ↓
FIRST AI REQUEST
  ↓
Spawns: python -m jira_mcp_cursor.cli serve
  ↓
Process starts and waits on STDIN
  ↓
USER ASKS QUESTIONS
  ↓
Cursor sends JSON-RPC messages to STDIN
Server responds on STDOUT
(Process keeps running)
  ↓
CURSOR CLOSES or TIMEOUT
  ↓
Process terminated
```

---

## 🎓 Key Concepts Explained

### 1. **STDIO Communication**

**What is STDIO?**
- **STDIN** = Standard Input (keyboard input to a program)
- **STDOUT** = Standard Output (program's normal output)
- **STDERR** = Standard Error (program's error messages)

**Our Usage:**
```python
# In our server code (server.py):
async with stdio_server() as (read_stream, write_stream):
    # read_stream  = STDIN  (Cursor writes here)
    # write_stream = STDOUT (We write responses here)
    await app.run(read_stream, write_stream, init_options)
```

**Why this works:**
- Cursor launches our Python script
- Cursor can write JSON to the script's STDIN
- Cursor can read JSON from the script's STDOUT
- No network, no ports, just pipes!

### 2. **JSON-RPC Protocol**

**What is JSON-RPC?**
Remote Procedure Call protocol using JSON format.

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_issue",
    "arguments": {
      "project_key": "SWI",
      "summary": "New feature",
      "description": "Details here"
    }
  }
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"success\": true, \"issue_key\": \"SWI-835\"}"
    }]
  }
}
```

### 3. **Process vs Server**

**It's a Process, Not a Server:**
- ✅ Python script running (`ps aux` shows it)
- ✅ Communicates via STDIN/STDOUT
- ❌ NOT listening on a network port
- ❌ NO HTTP endpoints
- ❌ NOT a Docker container
- ❌ NOT accessible from outside

**Comparison:**

| Traditional Web Server | MCP Server (STDIO) |
|------------------------|-------------------|
| `flask run --port 5000` | `python -m jira_mcp_cursor.cli serve` |
| Listens on network port | Listens on STDIN |
| HTTP requests | JSON-RPC messages |
| Multiple clients can connect | Only Cursor connects |
| `curl http://localhost:5000` | Cursor writes to STDIN |
| Need to manage ports | No ports needed |

---

## 🛠️ What We Built

### Components:

**1. Server (`server.py`)**
```python
app = Server("jira-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [11 tool definitions]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # Route to appropriate handler
    # Execute Python code
    # Return results
```

**2. Tools (`tools/*.py`)**
- Each tool has a **definition** (name, description, parameters)
- Each tool has a **handler** (Python function that executes)

**3. Jira Client (`jira_client.py`)**
- Makes HTTPS calls to Jira REST API
- Handles authentication
- Retry logic, error handling

**4. CLI (`cli.py`)**
- `jira-mcp configure` - Setup wizard
- `jira-mcp install` - Create .cursor/mcp.json
- `jira-mcp serve` - Start MCP server (called by Cursor)

---

## 🔐 Security Model

### Where Credentials are Stored

**1. Encrypted Config File:**
```
~/.jira-mcp/config.json  (encrypted with Fernet)
~/.jira-mcp/.key         (encryption key, permissions: 600)
```

**2. In Memory (When Running):**
```
Python Process (PID 149683)
  ↓
Decrypts credentials
  ↓
Uses for Jira API calls
  ↓
Credentials NEVER written to disk unencrypted
```

### Why This is Secure

- ✅ **Credentials encrypted at rest** (AES-128 via Fernet)
- ✅ **File permissions 600** (only you can read)
- ✅ **No network exposure** (STDIO, not HTTP)
- ✅ **Process isolation** (each project gets own process)
- ✅ **Machine-bound keys** (can't copy config to another machine)
- ✅ **HTTPS to Jira** (encrypted in transit)

---

## 🎯 Use Cases

### 1. **View Your Work**
```
You: "Show me my Jira tickets"
AI: Uses list_my_tickets tool
Result: List of all your assigned tickets
```

### 2. **Plan Features**
```
You: "Let's implement SWI-500"
AI: "Let me get the details" → Uses get_ticket tool
AI: "I see it's about authentication. Let me break this down:"
AI: Uses create_issue tool to create 3 stories:
    - SWI-501: Backend implementation
    - SWI-502: Frontend implementation
    - SWI-503: Testing
```

### 3. **Break Down Stories**
```
You: "Break down SWI-501 into subtasks"
AI: Uses create_subtask tool to create:
    - SWI-501-1: Database schema
    - SWI-501-2: API endpoints
    - SWI-501-3: Unit tests
```

### 4. **Track Progress**
```
You: "Mark SWI-501-1 as done"
AI: Uses update_ticket_status tool
Result: Ticket moved to "Done" in Jira
```

### 5. **Collaborate**
```
You: "Add a comment to SWI-501: Backend complete"
AI: Uses add_ticket_comment tool
Result: Comment added to Jira ticket
```

---

## 📊 Process Lifecycle Details

### When Cursor Starts

```bash
# Cursor reads .cursor/mcp.json
# Finds jira server definition:
{
  "mcpServers": {
    "jira": {
      "command": "/path/to/python",
      "args": ["-m", "jira_mcp_cursor.cli", "serve", ...]
    }
  }
}

# Cursor spawns the process:
$ /path/to/python -m jira_mcp_cursor.cli serve --config ~/.jira-mcp/config.json

# Process starts:
Starting Jira MCP Server...
INFO - Starting Jira MCP Server
INFO - Jira URL: https://fintama.atlassian.net
INFO - Auth mode: Cloud

# Process waits on STDIN for commands
# (Does NOT exit, keeps running)
```

### Active State

```
Process: RUNNING ✅
PID: 149683
Memory: ~58MB
CPU: 0% (idle, waiting for requests)

STDIN:  Waiting for JSON-RPC messages from Cursor
STDOUT: Ready to send responses
STDERR: Logging output
```

### When Tool is Called

```
STDIN receives:
{"method":"tools/call","params":{"name":"list_my_tickets"}}
  ↓
CPU spikes to 5-10% for ~500ms
  ↓
Makes HTTPS call to Jira
  ↓
Processes response
  ↓
STDOUT sends:
{"result":{"tickets":[...]}}
  ↓
Back to idle state (CPU 0%)
```

### When Cursor Closes

```
Cursor sends shutdown signal
  ↓
Process receives SIGTERM
  ↓
Cleanup (close HTTP connections)
  ↓
Process exits
  ↓
No more process in ps aux
```

---

## 🚀 Advanced Configuration

### Environment Variables

You can add environment variables to the MCP configuration:

```json
{
  "mcpServers": {
    "jira": {
      "command": "/path/to/python",
      "args": ["-m", "jira_mcp_cursor.cli", "serve"],
      "env": {
        "LOG_LEVEL": "DEBUG",
        "JIRA_TIMEOUT": "60",
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

### Multiple Projects

Each project can have its own `.cursor/mcp.json`:

```
project-a/.cursor/mcp.json  → Uses project A's Jira
project-b/.cursor/mcp.json  → Uses project B's Jira
```

Cursor spawns a separate process for each project!

---

## 🔍 Monitoring

### Check Process Status

```bash
# See if MCP server is running
ps aux | grep jira_mcp_cursor

# See process details
ps -p <PID> -o pid,vsz,rss,cmd

# Monitor in real-time
watch -n 1 'ps aux | grep jira_mcp_cursor'
```

### Check Logs

```bash
# Server logs to STDERR when running
# To see logs when testing manually:
python -m jira_mcp_cursor.cli serve 2>&1 | tee server.log
```

---

## 📝 Summary

### What You Need to Know:

1. **MCP Server = Python Process**
   - Real process running on your system
   - Not a web server, not a container
   - Communicates via STDIN/STDOUT

2. **Cursor Manages Everything**
   - Reads `.cursor/mcp.json`
   - Spawns the Python process
   - Sends JSON-RPC messages
   - Receives responses
   - Kills process when done

3. **Tools = Functions AI Can Call**
   - 11 tools for Jira operations
   - AI decides when to use them
   - Results returned to AI
   - AI presents to you

4. **Secure by Design**
   - Encrypted credentials
   - No network exposure
   - Process isolation
   - HTTPS to Jira

5. **Simple Setup**
   - Install package
   - Configure credentials
   - Create `.cursor/mcp.json`
   - Restart Cursor
   - Done!

---

**Questions?** Check the [Troubleshooting](TROUBLESHOOTING.md) guide or open an issue!




