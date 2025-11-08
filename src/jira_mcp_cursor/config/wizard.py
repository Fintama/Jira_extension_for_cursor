"""Setup wizard for Jira MCP configuration."""

import asyncio
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from typing import Any
import logging
import httpx
from urllib.parse import urlparse
import threading

from .storage import SecureConfig

logger = logging.getLogger(__name__)


class SetupWizard:
    """Web-based setup wizard for Jira MCP configuration.

    Launches a local HTTP server on port 8080 with a web UI for
    configuring Jira credentials. Auto-opens browser and saves
    encrypted configuration.
    """

    def __init__(self, port: int = 8080):
        self.port = port
        self.server: HTTPServer | None = None
        self.config_saved = False

    def validate_url(self, url: str) -> bool:
        """Validate Jira URL format.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    async def test_connection(self, jira_url: str, email: str, api_token: str) -> dict[str, Any]:
        """Test connection to Jira with provided credentials.

        Args:
            jira_url: Jira instance URL
            email: User email
            api_token: API token

        Returns:
            Dict with success status and user info or error message
        """
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
                    return {
                        "success": False,
                        "error": f"Authentication failed (HTTP {response.status_code})",
                    }

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {"success": False, "error": str(e)}

    async def save_config(self, config_data: dict[str, str]) -> dict[str, Any]:
        """Save configuration to encrypted storage.

        Args:
            config_data: Dict with jira_url, email, api_token

        Returns:
            Dict with success status
        """
        try:
            storage = SecureConfig()
            storage.save(config_data)
            self.config_saved = True

            logger.info("Configuration saved successfully")
            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return {"success": False, "error": str(e)}

    def _create_request_handler(self):
        """Create request handler class with closure over wizard instance."""
        wizard = self

        class WizardRequestHandler(BaseHTTPRequestHandler):
            """HTTP request handler for setup wizard."""

            def log_message(self, format, *args):
                """Suppress default HTTP logging."""
                pass

            def do_GET(self):
                """Handle GET requests."""
                if self.path == "/" or self.path == "/index.html":
                    # Serve wizard UI
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    # Load HTML from package
                    html_path = Path(__file__).parent / "wizard_ui.html"
                    html_content = html_path.read_text()
                    self.wfile.write(html_content.encode())

                elif self.path == "/success":
                    # Already handled by JS - just return 200
                    self.send_response(200)
                    self.end_headers()

                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                """Handle POST requests."""
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())

                if self.path == "/api/test":
                    # Test connection
                    result = asyncio.run(
                        wizard.test_connection(
                            data.get("jira_url", ""),
                            data.get("email", ""),
                            data.get("api_token", ""),
                        )
                    )

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())

                elif self.path == "/api/save":
                    # Save configuration
                    result = asyncio.run(wizard.save_config(data))

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())

                else:
                    self.send_response(404)
                    self.end_headers()

        return WizardRequestHandler

    def start(self) -> None:
        """Start the wizard HTTP server.

        Launches server on configured port.
        """
        handler_class = self._create_request_handler()
        self.server = HTTPServer(("localhost", self.port), handler_class)
        logger.info(f"Setup wizard server started on http://localhost:{self.port}")

    def stop(self) -> None:
        """Stop the wizard HTTP server.

        Note: This method closes the server socket but doesn't block.
        If server is running in a thread, it will stop serving new requests.
        """
        if self.server:
            # Use server_close() instead of shutdown() to avoid blocking
            self.server.server_close()
            logger.info("Setup wizard server stopped")
            self.server = None

    def run(self) -> None:
        """Run the setup wizard.

        Starts server, opens browser, and waits for configuration.
        """
        print("🚀 Starting Jira MCP Setup Wizard...")
        print(f"🌐 Opening http://localhost:{self.port} in your browser...")

        try:
            # Start server in background thread
            self.start()

            def serve_forever():
                if self.server:
                    self.server.serve_forever()

            server_thread = threading.Thread(target=serve_forever, daemon=True)
            server_thread.start()

            # Open browser
            webbrowser.open(f"http://localhost:{self.port}")

            print("\n✨ Setup wizard is running!")
            print("   Complete the configuration in your browser.")
            print("   Press Ctrl+C to stop the server.\n")

            # Wait for config to be saved or user interruption
            try:
                while not self.config_saved:
                    import time

                    time.sleep(1)

                print("✅ Configuration saved successfully!")
                print("\nNext step: Run 'jira-mcp install' to add to Cursor")

            except KeyboardInterrupt:
                print("\n\n⚠️  Setup wizard stopped by user.")

        finally:
            self.stop()


class ConfigWizard(SetupWizard):
    """Alias for SetupWizard for backward compatibility."""

    pass
