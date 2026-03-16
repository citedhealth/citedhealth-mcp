"""CITED Health MCP Server — query supplement evidence from AI assistants."""

__version__ = "0.2.0"


def main() -> None:
    """Entry point for `citedhealth-mcp` CLI."""
    from citedhealth_mcp.server import mcp

    mcp.run()
