# Jira MCP Development Roadmap

## ✅ Setup (DONE)
- [x] Create project folder
- [x] Initialize git
- [x] Create Python package structure
- [x] Copy design documentation
- [x] Initial commit

## 🚀 Next Steps

### 1. GitHub Setup (NOW)
- [ ] Create GitHub repository: `jira-mcp-cursor`
- [ ] Add remote: `git remote add origin <url>`
- [ ] Push: `git push -u origin master`

### 2. Development Environment (This Week)
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Install dependencies: `pip install -e ".[dev]"`
- [ ] Get Jira API token from: https://id.atlassian.com/manage-profile/security/api-tokens
- [ ] Test Jira connection (see docs/jira-mcp-server-quick-reference.md)

### 3. Core Implementation (Week 1-2)
- [ ] Implement `src/jira_mcp_cursor/config/storage.py` - Encrypted config
- [ ] Implement `src/jira_mcp_cursor/server/jira_client.py` - Jira API client
- [ ] Implement `src/jira_mcp_cursor/server/server.py` - MCP server
- [ ] Implement `src/jira_mcp_cursor/tools/list_tickets.py` - First tool
- [ ] Test with Cursor

### 4. Setup Wizard (Week 3-4)
- [ ] Implement `src/jira_mcp_cursor/config/wizard.py` - Web UI server
- [ ] Create setup wizard HTML/CSS/JS
- [ ] Implement `src/jira_mcp_cursor/cli.py` - CLI interface
- [ ] Auto-installer for Cursor

### 5. Polish & Launch (Week 5-6)
- [ ] Write tests
- [ ] Documentation
- [ ] Package for PyPI
- [ ] Launch!

## 📚 Reference
- See `docs/JIRA_MCP_INDEX.md` for documentation guide
- See `docs/jira-mcp-server-implementation-example.md` for code samples

