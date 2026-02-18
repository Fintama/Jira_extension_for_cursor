# Jira MCP Setup Guide

Step-by-step instructions to get the Jira integration working in Cursor. Pick the section that matches your setup.

---

## Before you start

You need two things:

1. **Python 3.11 or higher** installed and on your PATH.
2. **A Jira API token.** Go to https://id.atlassian.com/manage-profile/security/api-tokens, click "Create API token", give it a name like "Cursor MCP", and copy the token. Keep it somewhere safe — you'll need it in a moment.

---

## Option A: Cursor on Windows (no WSL)

Use this if you run Cursor as a normal Windows app and do **not** use WSL.

### A1. Install the package

Open **PowerShell** or **Command Prompt** and run:

```
pip install jira-mcp-cursor
```

Verify it worked:

```
jira-mcp --version
```

You should see a version number. If you get "command not found", Python's Scripts folder is not on your PATH. See [Troubleshooting](#troubleshooting) at the bottom.

### A2. Create the config file

Open File Explorer and navigate to:

```
C:\Users\<YourUsername>\.cursor\
```

> **Can't see the `.cursor` folder?** In File Explorer, click **View > Show > Hidden items**. Or press `Win+R`, type `%USERPROFILE%\.cursor` and hit Enter.

If there is already a file called `mcp.json`, open it. Otherwise create a new file called `mcp.json`.

Paste this into the file, replacing the four placeholder values:

```json
{
  "mcpServers": {
    "jira": {
      "command": "jira-mcp",
      "args": ["serve"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "you@example.com",
        "JIRA_API_TOKEN": "paste-your-api-token-here",
        "JIRA_PROJECT_KEY": "SP"
      }
    }
  }
}
```

> **Already have other MCP servers in this file?** Just add the `"jira": { ... }` block inside the existing `"mcpServers"` object. Don't create a second `"mcpServers"` key.

Save the file.

### A3. Reload Cursor

Press `Ctrl+Shift+P`, type **Reload Window**, and hit Enter.

### A4. Verify

1. Open **Cursor Settings** (gear icon or `Ctrl+,`)
2. Go to **Tools & MCP**
3. You should see **"jira"** with a green toggle and **14 tools**

If the toggle is red, click it to see the error message. Jump to [Troubleshooting](#troubleshooting).

---

## Option B: Cursor connected to WSL

Use this if Cursor is running on Windows but connected to a WSL distro (you see `WSL: Ubuntu` or similar in the bottom-left corner of Cursor).

> **Important:** When Cursor is in WSL mode, it runs MCP server commands **inside WSL**, not on Windows. So we install everything inside your Linux distro.

### B1. Install the package (inside WSL)

Open a **WSL terminal** (or use the integrated terminal in Cursor, which is already in WSL) and run:

```bash
pip install jira-mcp-cursor
```

Verify it worked:

```bash
jira-mcp --version
```

If `pip` is not found, you may need `pip3` instead, or install pip first:

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install jira-mcp-cursor
```

### B2. Create the config file

The config file goes in your **Linux home directory** inside WSL, not on the Windows side.

In your WSL terminal:

```bash
mkdir -p ~/.cursor
nano ~/.cursor/mcp.json
```

Paste this, replacing the four placeholder values:

```json
{
  "mcpServers": {
    "jira": {
      "command": "jira-mcp",
      "args": ["serve"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "you@example.com",
        "JIRA_API_TOKEN": "paste-your-api-token-here",
        "JIRA_PROJECT_KEY": "SP"
      }
    }
  }
}
```

Save and exit (`Ctrl+O`, Enter, `Ctrl+X` in nano).

> **Already have other MCP servers in this file?** Just add the `"jira": { ... }` block inside the existing `"mcpServers"` object.

> **Alternative: project-level config.** Instead of the global `~/.cursor/mcp.json`, you can put the file at `<your-project>/.cursor/mcp.json`. This scopes it to that project only.

### B3. Reload Cursor

Press `Ctrl+Shift+P`, type **Reload Window**, and hit Enter.

### B4. Verify

1. Open **Cursor Settings** (gear icon or `Ctrl+,`)
2. Go to **Tools & MCP**
3. You should see **"jira"** with a green toggle and **14 tools**

If the toggle is red, click it to see the error message. Jump to [Troubleshooting](#troubleshooting).

---

## Option C: Cursor on macOS or Linux (native)

### C1. Install the package

Open a terminal and run:

```bash
pip install jira-mcp-cursor
```

Or with `pip3`:

```bash
pip3 install jira-mcp-cursor
```

Verify:

```bash
jira-mcp --version
```

### C2. Create the config file

```bash
mkdir -p ~/.cursor
nano ~/.cursor/mcp.json
```

Paste this, replacing the four placeholder values:

```json
{
  "mcpServers": {
    "jira": {
      "command": "jira-mcp",
      "args": ["serve"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "you@example.com",
        "JIRA_API_TOKEN": "paste-your-api-token-here",
        "JIRA_PROJECT_KEY": "SP"
      }
    }
  }
}
```

Save and exit.

### C3. Reload Cursor

Press `Cmd+Shift+P`, type **Reload Window**, and hit Enter.

### C4. Verify

1. Open **Cursor Settings** (gear icon or `Cmd+,`)
2. Go to **Tools & MCP**
3. You should see **"jira"** with a green toggle and **14 tools**

---

## What to put in the config

| Field | What to enter | Example |
|---|---|---|
| `JIRA_URL` | Your Jira instance URL | `https://fintama.atlassian.net` |
| `JIRA_EMAIL` | The email you log into Jira with | `heiko@fintama.com` |
| `JIRA_API_TOKEN` | The API token you created earlier (not your password) | `ATATT3xFfGF0...` |
| `JIRA_PROJECT_KEY` | Your default Jira project key (optional but recommended) | `SP` |

The `JIRA_PROJECT_KEY` is the short prefix you see on tickets (e.g. if your tickets are `SP-123`, the key is `SP`). Setting this means you can say "show my tickets" without specifying the project every time.

---

## Test it

Open Cursor chat (Agent mode) and try any of these:

- "Show me my Jira tickets"
- "What's my highest priority ticket?"
- "Get details for SP-123"
- "Create a task: Set up CI pipeline"

If the AI responds with ticket data from your Jira, everything is working.

---

## Troubleshooting

### "jira-mcp: command not found"

The `pip install` succeeded but the command isn't on your PATH.

**Windows fix:** Run `python -m site --user-site` to find where pip installs scripts. Add that `Scripts` folder to your PATH. Or use the full path in `mcp.json`:

```json
"command": "python",
"args": ["-m", "jira_mcp_cursor.cli", "serve"],
```

**Linux/WSL fix:** Try `pip3 install jira-mcp-cursor` or `python3 -m pip install jira-mcp-cursor`. If installed with `--user`, make sure `~/.local/bin` is on your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Then verify: `which jira-mcp`

### Toggle is red in Cursor settings

Click the red toggle to see the error. Common causes:

- **"spawn jira-mcp ENOENT"** — Cursor can't find the command. See "command not found" above.
- **"Authentication failed"** — Your API token is wrong or expired. Generate a new one at https://id.atlassian.com/manage-profile/security/api-tokens
- **"Connection refused"** — Your `JIRA_URL` is wrong. Make sure it's the full URL including `https://`.

### I edited mcp.json but nothing changed

Cursor only reads `mcp.json` on startup. You must reload: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) > **Reload Window**.

### I have multiple mcp.json files — which one wins?

Cursor reads both global (`~/.cursor/mcp.json`) and project-level (`<project>/.cursor/mcp.json`). If the same server name exists in both, the project-level one takes priority.

### I'm on WSL but the Jira server isn't connecting

Make sure you installed `jira-mcp-cursor` **inside WSL**, not on Windows. Open a WSL terminal and run `which jira-mcp` — it should return a Linux path like `/home/you/.local/bin/jira-mcp` or `/usr/local/bin/jira-mcp`.

If you installed it on Windows instead, it won't be available inside WSL.

---

## Updating

When a new version is released:

```bash
pip install --upgrade jira-mcp-cursor
```

Then reload Cursor.
