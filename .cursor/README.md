# ⚠️ SECURITY NOTICE

## Credentials in This Directory

The `.cursor/mcp.json` file in this directory contains **sensitive credentials**:
- Jira URL
- Email address
- API tokens

## 🔐 Protection

✅ **This directory is gitignored** (see `.gitignore` line 39: `.cursor/`)

✅ **Your credentials will NOT be committed to git**

✅ **Safe to use locally**

## 📋 Setup Instructions

1. Copy the example file:
   ```bash
   cp .cursor/mcp.json.example .cursor/mcp.json
   ```

2. Edit `.cursor/mcp.json` with your credentials

3. **Never** commit `mcp.json` to git (already protected by .gitignore)

## ✅ Verification

Check that mcp.json is ignored:
```bash
git check-ignore .cursor/mcp.json
# Should output: .cursor/mcp.json
```

---

**Questions?** See [docs/MCP_SETUP_GUIDE.md](../docs/MCP_SETUP_GUIDE.md)

