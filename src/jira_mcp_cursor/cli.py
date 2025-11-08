"""Command Line Interface for Jira MCP."""

import click
import asyncio
from . import __version__
from .config.storage import SecureConfig
from .config.wizard import ConfigWizard
from .config.cursor_installer import CursorInstaller


@click.group()
@click.version_option(version=__version__)
def cli():
    """Jira MCP for Cursor - Seamless Jira integration"""
    pass


@cli.command()
def configure():
    """Launch configuration wizard"""
    wizard = ConfigWizard()
    wizard.run()


@cli.command()
@click.option("--config", default=None, help="Path to config file (optional, can use env vars)")
def serve(config):
    """Start MCP server (used by Cursor)

    The server loads credentials from environment variables (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN).
    These can be set in .cursor/mcp.json or via --config file.
    """
    import asyncio
    import os
    from .server import run
    from .config import SecureConfig

    click.echo("Starting Jira MCP Server...")

    # If config file provided, load and set env vars
    if config and os.path.exists(config):
        storage = SecureConfig()
        jira_config = storage.load()

        # Set environment variables from config
        os.environ["JIRA_URL"] = jira_config.get("jira_url", "")
        os.environ["JIRA_EMAIL"] = jira_config.get("email", "")
        os.environ["JIRA_API_TOKEN"] = jira_config.get("api_token", "")
        if jira_config.get("default_project"):
            os.environ["JIRA_PROJECT_KEY"] = jira_config["default_project"]

    # Otherwise, env vars should already be set by Cursor from mcp.json
    asyncio.run(run())


@cli.command()
def install():
    """Install to Cursor"""
    click.echo("📦 Installing Jira MCP to Cursor...")

    # Check if config exists
    storage = SecureConfig()
    if not storage.exists():
        click.echo("❌ No configuration found. Please run 'jira-mcp configure' first.")
        return

    installer = CursorInstaller()

    if installer.install():
        click.echo("✅ Successfully installed to Cursor!")
        click.echo("\n📝 Please restart Cursor to activate the integration.")
    else:
        click.echo("❌ Installation failed. See errors above.")


@cli.command()
def uninstall():
    """Remove from Cursor"""
    click.echo("🗑️  Removing Jira MCP from Cursor...")

    installer = CursorInstaller()

    if installer.uninstall():
        click.echo("✅ Successfully removed from Cursor")
    else:
        click.echo("❌ Uninstall failed")


@cli.group(name="config")
def config_group():
    """Manage configuration"""
    pass


@config_group.command(name="show")
def config_show():
    """Show current configuration (sanitized)"""
    storage = SecureConfig()

    if not storage.exists():
        click.echo("❌ No configuration found.")
        click.echo("Run 'jira-mcp configure' to set up.")
        return

    config = storage.load()

    click.echo("\n📋 Current Configuration:")
    click.echo(f"   Jira URL: {config.get('jira_url', 'Not set')}")
    click.echo(f"   Email: {config.get('email', 'Not set')}")

    # Mask API token
    api_token = config.get("api_token", "")
    if api_token:
        click.echo(f"   API Token: {'*' * min(len(api_token), 20)}")
    else:
        click.echo("   API Token: Not set")

    click.echo()


@config_group.command(name="test")
def config_test():
    """Test current configuration"""
    click.echo("🔍 Testing connection to Jira...")

    storage = SecureConfig()

    if not storage.exists():
        click.echo("❌ No configuration found.")
        return

    config = storage.load()

    # Use test_connection function
    result = asyncio.run(
        test_connection(
            config.get("jira_url", ""),
            config.get("email", ""),
            config.get("api_token", ""),
        )
    )

    if result["success"]:
        click.echo(f"✅ Connected! User: {result.get('user', 'Unknown')}")
    else:
        click.echo(f"❌ Connection failed: {result.get('error', 'Unknown error')}")


@config_group.command(name="reset")
@click.confirmation_option(prompt="Are you sure you want to reset configuration?")
def config_reset():
    """Reset configuration"""
    storage = SecureConfig()
    storage.delete()
    click.echo("✅ Configuration reset")


async def test_connection(jira_url: str, email: str, api_token: str) -> dict:
    """Test connection to Jira (helper for CLI).

    Args:
        jira_url: Jira instance URL
        email: User email
        api_token: API token

    Returns:
        Dict with success status and user info or error
    """
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{jira_url.rstrip('/')}/rest/api/2/myself",
                auth=(email, api_token),
                timeout=10,
            )

            if response.status_code == 200:
                user_data = response.json()
                return {"success": True, "user": user_data.get("displayName", email)}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    cli()
