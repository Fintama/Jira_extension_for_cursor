# Jira MCP - Quick Reference Card

## 🚀 Setup in 5 Commands

```bash
# 1. Install
pip install -e .

# 2. Configure Jira
jira-mcp configure

# 3. Install to Cursor
jira-mcp install

# 4. Restart Cursor
# Ctrl+Shift+P → "Reload Window"

# 5. Verify
# Settings → Tools & MCP → Should show "jira" with "14 tools"
```

---

## 🔧 14 MCP Tools

| Category | Tool | Example |
|----------|------|---------|
| **Read** | `list_my_tickets` | "Show my tickets" |
| | `list_tickets_by_creator` | "Show tickets created by john@..." |
| | `get_ticket` | "Get SWI-123" |
| | `get_highest_priority_ticket` | "What's my top priority?" |
| | `get_subtasks` | "Show subtasks of SWI-500" |
| | `list_users` | "Find user named John" |
| **Analyze** | `analyze_ticket` | "Analyze SWI-456" |
| **Create** | `create_issue` | "Create story: Implement auth" |
| | `create_subtask` | "Break SWI-500 into subtasks" |
| **Update** | `update_ticket_status` | "Move SWI-123 to In Progress" |
| | `update_ticket_description` | "Update description of SWI-123" |
| | `add_ticket_comment` | "Comment on SWI-123" |
| | `assign_issue` | "Assign SWI-123 to john@..." |
| **Delete** | `delete_issue` | "Delete SWI-123" ⚠️ |

---

## 💬 Natural Language Examples

```
"Show me my Jira tickets"
"What's my highest priority ticket?"
"Get details for ticket SWI-156"
"Show me all subtasks of SWI-500"

"Create a story in project SWI: Implement authentication"
"Break down SWI-500 into 3 subtasks for backend, frontend, testing"

"Move SWI-123 to In Progress"
"Add comment to SWI-456: Implementation complete"
"Assign SWI-789 to alice@example.com"
```

---

## 🏗️ Architecture (Simple)

```
You → Cursor AI → MCP Server (Python) → Jira API
                     ↓
                (14 tools)
```

**Communication:** STDIN/STDOUT (not HTTP!)

---

## 📁 File Locations

| What | Where |
|------|-------|
| **MCP Config** | `<project>/.cursor/mcp.json` |
| **Jira Credentials** | `~/.jira-mcp/config.json` (encrypted) |
| **Encryption Key** | `~/.jira-mcp/.key` |
| **Python Package** | `<project>/venv/lib/python3.x/site-packages/` |

---

## 🔍 Debugging

```bash
# Check process
ps aux | grep jira_mcp_cursor

# Test connection
jira-mcp config test

# View config (sanitized)
jira-mcp config show

# Test server manually
python -m jira_mcp_cursor.cli serve
```

---

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] `jira-mcp --version` works
- [ ] `jira-mcp config test` shows ✅
- [ ] `.cursor/mcp.json` exists in project root
- [ ] Cursor reloaded after config
- [ ] Settings → Tools & MCP shows "jira" with "14 tools"
- [ ] `ps aux | grep jira_mcp` shows running process
- [ ] AI can list tickets when asked

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| "No tools" | Check `ToolsCapability` in server.py, reload Cursor |
| Command not found | Activate venv, reinstall package |
| Auth failed | Regenerate API token, reconfigure |
| Process not starting | Use absolute paths in .cursor/mcp.json |
| MCP server not in list | Create .cursor/mcp.json in project root, reload |

---

## 🔗 Links

- **Setup Guide:** [MCP_SETUP_GUIDE.md](MCP_SETUP_GUIDE.md)
- **How It Works:** [HOW_IT_WORKS.md](HOW_IT_WORKS.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Get API Token:** https://id.atlassian.com/manage-profile/security/api-tokens

---

**Need Help?** Check [MCP_SETUP_GUIDE.md](MCP_SETUP_GUIDE.md) for detailed explanations!




