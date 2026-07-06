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


@mcp.tool()
def calculate_co2_saved(
    energy_saved_watts: float,
    carbon_intensity: float,
    duration_hours: float = 1.0
) -> float:
    """Calculates CO2 saved in grams based on energy saved and carbon intensity.

    Args:
        energy_saved_watts: Energy saved in watts.
        carbon_intensity: Grid carbon intensity in gCO2eq/kWh.
        duration_hours: Time interval in hours (defaults to 1.0).

    Returns:
        The estimated CO2 saved in grams.
    """
    # energy_saved_kwh = (watts * hours) / 1000
    energy_saved_kwh = (energy_saved_watts * duration_hours) / 1000.0
    co2_saved_grams = energy_saved_kwh * carbon_intensity
    return round(co2_saved_grams, 3)


if __name__ == "__main__":
    mcp.run()
