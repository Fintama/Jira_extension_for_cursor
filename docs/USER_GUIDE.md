# Jira MCP - User Guide

Complete guide to installing, configuring, and using Jira MCP for Cursor.

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage Examples](#usage-examples)
4. [Common Workflows](#common-workflows)
5. [Tips & Best Practices](#tips--best-practices)

---

## Installation

### System Requirements

- **Python:** 3.11 or higher
- **Cursor IDE:** Latest version
- **Jira:** Cloud or Server instance
- **Operating System:** macOS, Linux, or Windows

### Install via pip

```bash
pip install jira-mcp-cursor
```

### Verify Installation

```bash
jira-mcp --version
```

Expected output: `jira-mcp-cursor, version 0.1.0`

---

## Configuration

### Step 1: Get Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Cursor MCP")
4. Copy the token (you won't see it again!)

### Step 2: Run Setup Wizard

```bash
jira-mcp configure
```

This will:
- Open a web browser with the setup wizard
- Prompt for your Jira URL, email, and API token
- Test the connection to verify credentials
- Save encrypted configuration

**The wizard looks like this:**
- Clean gradient interface
- Form validation
- Test connection before saving
- Success confirmation

### Step 3: Install to Cursor

```bash
jira-mcp install
```

This automatically:
- Detects your Cursor configuration location
- Creates a backup of existing settings
- Adds Jira MCP to Cursor's MCP servers
- Displays next steps

### Step 4: Restart Cursor

Close and reopen Cursor IDE to activate the integration.

---

## Usage Examples

### Example 1: Daily Stand-up Prep

**Goal:** Quickly review your current work

```
You: "Show me my In Progress tickets"

AI: [Uses list_my_tickets with status filter]
Returns: List of tickets you're actively working on
```

### Example 2: Start New Work

**Goal:** Find what to work on next

```
You: "What's my highest priority ticket?"

AI: [Uses get_highest_priority_ticket]
Returns: Your most important open ticket

You: "Move it to In Progress"

AI: [Uses update_ticket_status]
Updates the ticket status
```

### Example 3: Implement a Feature

**Goal:** Get requirements and implement

```
You: "Analyze ticket PROJ-456 and implement it"

AI: [Uses analyze_ticket to get requirements]
Extracts:
- Requirements list
- Acceptance criteria
- Technical notes
- Dependencies

Then implements based on extracted information
```

### Example 4: Complete Work

**Goal:** Update ticket when done

```
You: "I finished PROJ-123. Move it to Done and add a comment that it's tested"

AI: [Uses update_ticket_status + add_ticket_comment]
1. Transitions ticket to "Done"
2. Adds comment: "Implementation completed and tested"
```

### Example 5: Update Ticket Info

**Goal:** Add implementation notes

```
You: "Append implementation notes to PROJ-789: Used async/await pattern, added error handling"

AI: [Uses update_ticket_description with append=true]
Adds notes to existing description without losing original content
```

---

## Common Workflows

### Workflow 1: Bug Fix

```
1. "Show me bugs assigned to me"
   → Lists all bug tickets

2. "Get details for BUG-123"
   → Shows full description, steps to reproduce

3. [You fix the bug]

4. "Move BUG-123 to Done and comment: Fixed by correcting validation logic"
   → Updates status + adds comment
```

### Workflow 2: Feature Development

```
1. "What's my highest priority feature request?"
   → Shows top priority feature

2. "Analyze that ticket"
   → Extracts requirements, AC, tech notes

3. [You implement the feature]

4. "Update FEATURE-456 description with implementation details"
   → Documents what was built

5. "Move to Code Review"
   → Transitions ticket
```

### Workflow 3: Sprint Planning

```
1. "Show me my tickets in project SPRINT23"
   → Lists all tickets in that project

2. For each ticket:
   "Analyze SPRINT-XX"
   → Estimates complexity
   → Identifies dependencies

3. Prioritize based on analysis
```

---

## Tips & Best Practices

### 🎯 Effective Ticket Queries

**Be specific:**
```
❌ "Show tickets"
✅ "Show my In Progress tickets in project BACKEND"
```

**Use natural language:**
```
✅ "What's my highest priority bug?"
✅ "List my tickets due this week" (if date filters supported)
✅ "Show tickets I'm reviewing"
```

### 📝 Writing Clear Comments

When asking AI to add comments:

```
❌ "Comment on PROJ-123"
✅ "Add comment to PROJ-123: Blocked on external API dependency"
```

### 🔄 Status Transitions

**Check available transitions first:**
- Different workflows have different allowed transitions
- AI will suggest available statuses if transition invalid

**Common transitions:**
- To Do → In Progress
- In Progress → Code Review
- Code Review → Testing
- Testing → Done

### 🔍 Using Analyze Ticket

**Best for:**
- Complex tickets with structured descriptions
- Feature requests with detailed requirements
- Tickets with acceptance criteria sections

**Format your Jira tickets well:**
```markdown
# Requirements
- Requirement 1
- Requirement 2

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Technical Notes
Implementation details here...

Dependencies: PROJ-100, PROJ-200
```

---

## Advanced Configuration

### Multiple Jira Instances

Currently, Jira MCP supports one instance at a time. To switch:

```bash
jira-mcp config reset
jira-mcp configure
# Enter new instance credentials
```

### Custom Timeouts

For slow Jira instances:

```bash
# In .env or environment
JIRA_TIMEOUT=60  # 60 seconds
```

### Verbose Logging

For debugging:

```bash
LOG_LEVEL=DEBUG jira-mcp serve
```

---

## Uninstalling

### Remove from Cursor

```bash
jira-mcp uninstall
```

### Delete Configuration

```bash
jira-mcp config reset
```

### Uninstall Package

```bash
pip uninstall jira-mcp-cursor
```

---

## Getting Help

- **Documentation:** See [API Reference](API_REFERENCE.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issues:** https://github.com/yourusername/jira-mcp-cursor/issues
- **Discussions:** https://github.com/yourusername/jira-mcp-cursor/discussions

---

**Happy coding with seamless Jira integration! 🚀**

