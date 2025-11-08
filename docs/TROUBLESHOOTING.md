# Troubleshooting Guide

Common issues and solutions for Jira MCP for Cursor.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Connection Issues](#connection-issues)
4. [Cursor Integration Issues](#cursor-integration-issues)
5. [Runtime Issues](#runtime-issues)
6. [Performance Issues](#performance-issues)

---

## Installation Issues

### "Command not found: jira-mcp"

**Problem:** After `pip install`, the command isn't available.

**Solutions:**

1. **Verify installation:**
   ```bash
   pip show jira-mcp-cursor
   ```

2. **Check PATH:**
   ```bash
   which jira-mcp  # Unix
   where jira-mcp  # Windows
   ```

3. **Reinstall with user flag:**
   ```bash
   pip install --user jira-mcp-cursor
   ```

4. **Use python -m:**
   ```bash
   python -m jira_mcp_cursor.cli --help
   ```

### "Python version not supported"

**Problem:** Python version is too old.

**Solution:**
```bash
# Check Python version
python --version

# Upgrade Python to 3.11+
# See: https://www.python.org/downloads/
```

---

## Configuration Issues

### "Authentication failed"

**Problem:** Cannot connect to Jira with provided credentials.

**Solutions:**

1. **Verify API token:**
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Check if token is still active
   - Generate a new token if needed

2. **Check email address:**
   - Must match your Atlassian account email
   - Cannot use SSO login email if different

3. **Verify Jira URL:**
   ```bash
   # Correct formats:
   https://your-domain.atlassian.net  ✅
   https://jira.your-company.com      ✅

   # Incorrect:
   your-domain.atlassian.net          ❌ (missing https://)
   https://atlassian.net              ❌ (wrong domain)
   ```

4. **Test manually:**
   ```bash
   jira-mcp config test
   ```

### "Configuration file corrupted"

**Problem:** Cannot load configuration.

**Solution:**

1. **Reset and reconfigure:**
   ```bash
   jira-mcp config reset
   jira-mcp configure
   ```

2. **Check file permissions:**
   ```bash
   ls -la ~/.jira-mcp/
   # Should show: -rw------- (600 permissions)
   ```

3. **If all else fails:**
   ```bash
   rm -rf ~/.jira-mcp
   jira-mcp configure
   ```

### "No configuration found"

**Problem:** Trying to use commands before configuring.

**Solution:**
```bash
# Configure first
jira-mcp configure

# Then install
jira-mcp install
```

---

## Connection Issues

### "Connection timeout"

**Problem:** Requests to Jira time out.

**Solutions:**

1. **Increase timeout:**
   ```bash
   # In .env or environment
   JIRA_TIMEOUT=60
   ```

2. **Check network:**
   - Verify internet connection
   - Check if Jira is accessible: `curl https://your-domain.atlassian.net`
   - Check firewall/proxy settings

3. **VPN issues:**
   - If using corporate VPN, ensure Jira is accessible
   - Try connecting with VPN off/on

### "SSL Certificate Error"

**Problem:** SSL/TLS certificate validation fails.

**Solutions:**

1. **Update certificates:**
   ```bash
   pip install --upgrade certifi
   ```

2. **Check system time:**
   - Incorrect system time can cause SSL errors
   - Ensure system clock is accurate

### "Rate limit exceeded"

**Problem:** Too many requests to Jira API.

**Solutions:**

1. **Wait and retry** - Automatic retry with backoff is built-in

2. **Check your plan:**
   - Jira Standard: 10 requests/second
   - Jira Premium: 25 requests/second

3. **Reduce request frequency:**
   ```bash
   # Increase retry delay
   JIRA_MAX_RETRIES=5  # More retries, longer backoff
   ```

---

## Cursor Integration Issues

### "Cursor doesn't recognize Jira MCP"

**Problem:** After installation, Cursor doesn't have Jira integration.

**Solutions:**

1. **Verify installation:**
   ```bash
   jira-mcp config show  # Check config exists
   ```

2. **Check Cursor settings:**
   - Open Cursor settings
   - Look for MCP settings file
   - Verify "jira" entry exists

3. **Reinstall:**
   ```bash
   jira-mcp uninstall
   jira-mcp install
   ```

4. **Restart Cursor:**
   - Completely quit Cursor
   - Reopen Cursor
   - Try using Jira commands

### "MCP settings not found"

**Problem:** Cursor config location not detected.

**Solutions:**

1. **Check Cursor installation:**
   ```bash
   # macOS
   ls ~/.cursor/

   # Linux
   ls ~/.config/Cursor/

   # Windows
   dir %APPDATA%\Cursor\
   ```

2. **Manual installation:**
   - Find your Cursor MCP settings file
   - Add this entry manually:

   ```json
   {
     "mcpServers": {
       "jira": {
         "command": "jira-mcp",
         "args": ["serve", "--config", "~/.jira-mcp/config.json"]
       }
     }
   }
   ```

---

## Runtime Issues

### "Ticket not found"

**Problem:** AI says ticket doesn't exist.

**Solutions:**

1. **Verify ticket key:**
   - Format: PROJECT-NUMBER (e.g., "BACKEND-123")
   - Must be uppercase
   - Number must be valid

2. **Check permissions:**
   - Ensure you have permission to view the ticket
   - Ticket may be in a restricted project

3. **Verify instance:**
   - Confirm you're connected to the correct Jira instance
   - Run: `jira-mcp config show`

### "Cannot transition ticket"

**Problem:** Cannot change ticket status.

**Solutions:**

1. **Check workflow:**
   - Not all status transitions are allowed
   - Jira workflows define valid transitions

2. **Use available transitions:**
   ```
   You: "What statuses can PROJ-123 move to?"
   AI: [Checks available transitions]
   ```

3. **Check permissions:**
   - You may not have permission to transition
   - Some transitions require specific roles

### "Tool not responding"

**Problem:** MCP tool calls hang or timeout.

**Solutions:**

1. **Check Cursor logs:**
   - Help → Show Logs
   - Look for MCP-related errors

2. **Restart MCP server:**
   - Restart Cursor IDE
   - This restarts the MCP server

3. **Check Jira status:**
   ```bash
   jira-mcp config test
   ```

4. **Increase timeout:**
   ```bash
   JIRA_TIMEOUT=60
   ```

---

## Performance Issues

### "Slow response times"

**Problem:** Tools take too long to respond.

**Solutions:**

1. **Check Jira performance:**
   - Jira instance may be slow
   - Test directly: visit Jira in browser

2. **Reduce result size:**
   ```
   Instead of: "Show all my tickets"
   Use: "Show my top 10 tickets"
   ```

3. **Use filters:**
   ```
   Faster: "Show In Progress tickets in BACKEND project"
   Slower: "Show all my tickets across all projects"
   ```

### "High memory usage"

**Problem:** Python process using lots of memory.

**Solutions:**

1. **Restart Cursor** - Restarts MCP server

2. **Reduce max_results:**
   ```bash
   JIRA_MAX_RESULTS=25  # Instead of 50
   ```

---

## Common Error Messages

### "Invalid credentials"

**Cause:** API token expired or incorrect

**Fix:**
```bash
jira-mcp configure  # Reconfigure with new token
```

### "Field required: jira_url"

**Cause:** Incomplete configuration

**Fix:**
```bash
jira-mcp configure  # Complete configuration
```

### "Permission denied: ~/.jira-mcp/config.json"

**Cause:** File permission issue

**Fix:**
```bash
chmod 600 ~/.jira-mcp/config.json
chmod 600 ~/.jira-mcp/.key
```

---

## Debugging

### Enable Debug Logging

```bash
# Set log level to DEBUG
LOG_LEVEL=DEBUG jira-mcp serve
```

### Check Configuration

```bash
# Show config (tokens masked)
jira-mcp config show

# Test connection
jira-mcp config test
```

### Verify Installation

```bash
# Check if installed in Cursor
cat ~/.cursor/mcp_settings.json  # macOS/Linux
type %APPDATA%\Cursor\User\mcp_settings.json  # Windows
```

### Test Tools Manually

```bash
# Start server in terminal
jira-mcp serve

# In another terminal, test with Cursor
# Or check logs for errors
```

---

## Getting Additional Help

### Check Documentation

- **[API Reference](API_REFERENCE.md)** - Complete tool documentation
- **[README](../README.md)** - Overview and quick start
- **[.env.example](../.env.example)** - Configuration reference

### Report an Issue

If you've tried everything and still have problems:

1. **Collect information:**
   - Error messages
   - Logs from Cursor
   - Output of `jira-mcp config show`
   - Python and Cursor versions

2. **Create GitHub issue:**
   - https://github.com/yourusername/jira-mcp-cursor/issues
   - Use bug report template
   - Include all collected information

3. **Community support:**
   - GitHub Discussions
   - Stack Overflow (tag: jira-mcp-cursor)

---

## FAQ

**Q: Does this work with Jira Server/Data Center?**
A: Yes! Use username/password instead of email/token in configuration.

**Q: Can I use multiple Jira instances?**
A: Not simultaneously. Reconfigure to switch between instances.

**Q: Is my API token secure?**
A: Yes! Encrypted with Fernet, 600 file permissions, never in plaintext or logs.

**Q: Can I use this with other IDEs?**
A: It's built for Cursor but could work with any MCP-compatible editor.

**Q: Does it work offline?**
A: No, requires internet connection to reach Jira API.

**Q: What data is stored locally?**
A: Only encrypted credentials in `~/.jira-mcp/config.json`

---

**Still need help? Open an issue on GitHub!**

