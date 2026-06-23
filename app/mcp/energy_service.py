"""Energy MCP service module.

This module exposes the EnergyMCP tool server for calculating energy savings.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("EnergyMCP")


@mcp.tool()
def calculate_energy_saved(
    brightness: int,
    baseline_brightness: int = 90,
) -> int:
    """Calculates the energy saved based on the brightness percentage.

    Args:
        brightness: Current set brightness percentage (0-100).
        baseline_brightness: Baseline brightness percentage for comparison (defaults to 90).

    Returns:
        Estimated energy saved in watts (the difference between baseline and target).
    """
    # Logic to calculate energy saved based on the brightness percentage
    energy_saved = baseline_brightness - brightness
    return energy_saved


if __name__ == "__main__":
    mcp.run()
