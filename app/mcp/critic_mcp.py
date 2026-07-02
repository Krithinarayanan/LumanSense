"""Lighting audit MCP service.

This module exposes operational data and telemetry records for auditing lighting decisions.
"""

from app.mcp.database_mcp import (
    get_decision_events_by_zone,
    get_detection_events_by_zone,
    get_zone_config,
)
from app.mcp.database_mcp import (
    get_traffic_training_history as _get_traffic_training_history,
)

_mcp_instance = None


def _get_mcp():
    """Initializes and returns the FastMCP server instance for lighting audits."""
    global _mcp_instance
    if _mcp_instance is None:
        from mcp.server.fastmcp import FastMCP

        _mcp_instance = FastMCP("CriticMCP")
    return _mcp_instance


def get_latest_decisions(zone: str):
    """Fetches the latest dimming actuation decisions for a zone."""
    return get_decision_events_by_zone(zone, limit=10)


def get_latest_detection(zone: str):
    """Fetches the latest pedestrian telemetry records for a zone."""
    return get_detection_events_by_zone(zone, limit=80)


def get_footfall_prediction(zone: str):
    """Fetches the predictive occupancy forecast parameters for a zone."""
    return get_zone_config(zone)


def get_traffic_training_history(zone: str):
    """Fetches the baseline historical traffic training clusters for a zone."""
    return _get_traffic_training_history(zone)


def get_energy_statistics(zone: str):
    """Computes total energy footprint metrics for a zone (to be implemented)."""
    return {}


# Launch the audit service
if __name__ == "__main__":
    mcp = _get_mcp()

    mcp.tool()(get_latest_decisions)
    mcp.tool()(get_latest_detection)
    mcp.tool()(get_footfall_prediction)
    mcp.tool()(get_traffic_training_history)
    mcp.tool()(get_energy_statistics)

    mcp.run()
