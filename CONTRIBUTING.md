# Contributing to Jira MCP for Cursor

Thank you for your interest in contributing! This guide will help you get started.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A Jira Cloud or Server instance (for testing)

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/jira-mcp-cursor.git
cd jira-mcp-cursor

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install with development dependencies
pip install -e ".[dev]"

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your Jira test instance credentials

# 5. Run tests to verify setup
pytest tests/ -v
```

---

## 📋 Development Workflow

We follow a strict TDD (Test-Driven Development) workflow:

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming convention:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions
- `refactor/` - Code improvements

### 2. Write Tests First (TDD)

Before implementing any feature:

1. Write tests that fail
2. Run tests to verify they fail
3. Implement the feature
4. Run tests to verify they pass
5. Refactor and ensure tests still pass

Example:

```python
# tests/test_new_feature.py
@pytest.mark.asyncio
async def test_new_feature():
    """Test the new feature."""
    # Arrange
    client = JiraClient(...)

    # Act
    result = await client.new_method()

    # Assert
    assert result == expected_value
```

### 3. Code Quality Standards

**Before committing, ensure:**

```bash
# Format code
black src/jira_mcp_cursor tests/

# Lint
ruff check src/jira_mcp_cursor tests/

# Type check (if applicable)
mypy src/jira_mcp_cursor/

# Run tests
pytest tests/ -v
```

**All checks must pass!**

### 4. Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for custom JQL queries"
git commit -m "Fix: Handle empty ticket descriptions gracefully"

# Bad
git commit -m "update stuff"
git commit -m "fix bug"
```

### 5. Create Pull Request

1. Push your branch to GitHub
2. Create a Pull Request
3. Describe what you changed and why
4. Link any related issues
5. Wait for review

---

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_jira_client.py      # Jira API client tests
├── test_tools.py            # MCP tool handler tests
├── test_utils.py            # Utility function tests
├── test_error_handling.py   # Error handling tests
├── test_integration.py      # Integration workflow tests
├── test_config_storage.py   # Config storage tests
├── test_cursor_installer.py # Installer tests
├── test_wizard.py           # Setup wizard tests
├── test_cli.py              # CLI command tests
├── test_performance.py      # Performance benchmarks
└── test_e2e.py              # End-to-end tests
```

### Writing Good Tests

**Test naming:** Descriptive and clear
```python
# Good
def test_list_tickets_with_status_filter()
def test_handle_missing_ticket_gracefully()

# Bad
def test_1()
def test_stuff()
```

**Test structure:** Arrange, Act, Assert
```python
@pytest.mark.asyncio
async def test_example():
    # Arrange - Set up test data
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_data

    # Act - Perform the action
    result = await handle_get_ticket(arguments, mock_client)

    # Assert - Verify results
    assert result["key"] == "TEST-123"
```

**Coverage:** Aim for 90%+ coverage

```bash
pytest tests/ --cov=src/jira_mcp_cursor --cov-report=html
```

---

## 📝 Code Style

### Python Style Guide

- **Line length:** 100 characters (configured in `pyproject.toml`)
- **Formatter:** Black (enforced)
- **Linter:** Ruff (enforced)
- **Type hints:** Required for all public APIs
- **Docstrings:** Required for all public functions/classes

### Docstring Format

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of what the function does.

    Longer description if needed with more details about behavior,
    edge cases, or important notes.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When and why this exception is raised

    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify you're using the latest version
3. Test with minimal configuration

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what's wrong

**To Reproduce**
Steps to reproduce:
1. Configure with...
2. Run command...
3. See error

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment:**
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.11.5]
- Jira MCP version: [e.g., 0.1.0]
- Jira type: [Cloud/Server]

**Additional context**
Logs, screenshots, etc.
```

---

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if it's already requested in issues
2. Describe the use case and benefit
3. Provide examples of how it would work
4. Consider contributing an implementation

---

## 📖 Documentation

When adding features, please update:

- **README.md** - If adding user-facing features
- **docs/API_REFERENCE.md** - If adding/changing MCP tools
- **docs/USER_GUIDE.md** - If adding workflows
- **CHANGELOG.md** - All changes
- **Docstrings** - All new code

---

## 🔍 Code Review Checklist

Before submitting a PR, verify:

- [ ] All tests pass
- [ ] Code is formatted (Black)
- [ ] Linting passes (Ruff)
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No credentials in code
- [ ] No breaking changes (or documented)

---

## 🎯 Priority Areas for Contribution

We'd especially love help with:

1. **Testing** - More edge case coverage
2. **Documentation** - Examples, tutorials, guides
3. **Cross-platform** - Windows testing and fixes
4. **Performance** - Optimization opportunities
5. **Features** - See issues labeled `good-first-issue`

---

## 💬 Getting Help

- **Questions:** Open a discussion on GitHub
- **Bugs:** Open an issue
- **Chat:** Join our community (link TBD)

---

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy coding! 🚀**

