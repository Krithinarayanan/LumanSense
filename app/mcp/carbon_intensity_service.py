"""Carbon Intensity MCP service.

This module exposes the CarbonIntensityMCP tool to fetch real-time grid carbon intensity
(gCO2eq/kWh) from the ElectricityMaps API or default to a global baseline.
"""

import os
import requests
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("luman_sense")

mcp = FastMCP("CarbonIntensityMCP")


@mcp.tool()
def get_grid_carbon_intensity(region: str = "US-CA") -> dict:
    """Fetches real-time grid carbon intensity (gCO2eq/kWh).

    Args:
        region: The geographical region identifier (e.g., 'US-CA', 'IN-WE').

    Returns:
        A dictionary containing the carbon intensity in gCO2eq/kWh and the data source.
    """
    api_key = os.environ.get("ELECTRICITY_MAPS_API_KEY")
    if not api_key:
        # Default to 320 gCO2eq/kWh as a globally representative baseline
        # (reflecting the global average grid carbon intensity under transitional energy mixes)
        return {
            "carbon_intensity": 320.0,
            "source": "default_global_baseline",
            "message": "API key missing. Defaulting to standard global average."
        }

    try:
        # ElectricityMaps API v3 endpoint
        url = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={region}"
        headers = {"auth-token": api_key}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return {
                "carbon_intensity": float(data.get("carbonIntensity", 320.0)),
                "source": "electricitymaps"
            }
        else:
            logger.warning("ElectricityMaps API returned status %d. Using fallback.", res.status_code)
            return {
                "carbon_intensity": 320.0,
                "source": "fallback_global_baseline"
            }
    except Exception as e:
        logger.error("Error fetching carbon intensity from API: %s", e)
        return {
            "carbon_intensity": 320.0,
            "source": "fallback_global_baseline"
        }


if __name__ == "__main__":
    mcp.run()
