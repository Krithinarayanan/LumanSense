"""Controller MCP service module.

This module exposes the ControllerMCP tool server for setting lamp brightness levels.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ControllerMCP")


@mcp.tool()
def set_lamp_brightness(percentage: int) -> str:
    """Sets the lamp brightness (0-100).

    Args:
        percentage: The target brightness level to set.

    Returns:
        A message confirmation of the set brightness level.
    """
    # Logic to send signal to hardware would go here
    return f"Successfully set lamp brightness to {percentage}%."


if __name__ == "__main__":
    mcp.run()
