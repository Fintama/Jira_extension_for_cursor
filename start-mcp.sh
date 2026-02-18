#!/usr/bin/env bash
# Wrapper script to start Jira MCP server from its own directory,
# preventing it from reading the host project's .env file.
cd "$(dirname "$0")"
exec /home/heiko/projects/Jira_extension_for_cursor/venv/bin/python -m jira_mcp_cursor.cli serve
