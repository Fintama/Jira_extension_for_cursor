"""MCP server implementation."""

# Lazy imports to avoid circular dependency
__all__ = ["app", "run"]


def __getattr__(name):
    """Lazy import to avoid circular dependency."""
    if name == "app":
        from .server import app

        return app
    elif name == "run":
        from .server import run

        return run
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
