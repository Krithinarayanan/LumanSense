"""Lighting audit MCP service.

This module exposes operational data and telemetry records for auditing lighting decisions.
"""

from app.mcp.database_mcp import (
    get_connection,
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
    """Computes total energy footprint metrics for a zone.

    Args:
        zone: The zone identifier (e.g., 'A', 'B', 'C', 'D').

    Returns:
        A dictionary containing total energy saved, average brightness,
        number of decisions, and comparison details.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                SUM(energy_saved_watts) as total_saved,
                AVG(brightness) as avg_brightness,
                COUNT(id) as count_decisions,
                AVG(energy_saved_watts) as avg_saved,
                MAX(energy_saved_watts) as max_saved,
                AVG(pred_brightness) as avg_pred_brightness,
                AVG(reactive_brightness) as avg_reactive_brightness
            FROM decision_events
            WHERE zone = ?
            """,
            (zone,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row or row[2] == 0:
            return {
                "zone": zone,
                "total_energy_saved_watts": 0,
                "average_brightness_percent": 0.0,
                "total_decisions": 0,
                "average_energy_saved_watts": 0.0,
                "max_energy_saved_watts": 0,
                "average_pred_brightness": 0.0,
                "average_reactive_brightness": 0.0,
            }

        return {
            "zone": zone,
            "total_energy_saved_watts": int(row[0]) if row[0] is not None else 0,
            "average_brightness_percent": round(float(row[1]), 2) if row[1] is not None else 0.0,
            "total_decisions": int(row[2]),
            "average_energy_saved_watts": round(float(row[3]), 2) if row[3] is not None else 0.0,
            "max_energy_saved_watts": int(row[4]) if row[4] is not None else 0,
            "average_pred_brightness": round(float(row[5]), 2) if row[5] is not None else 0.0,
            "average_reactive_brightness": round(float(row[6]), 2) if row[6] is not None else 0.0,
        }
    except Exception as e:
        return {
            "zone": zone,
            "error": str(e),
            "total_energy_saved_watts": 0,
            "average_brightness_percent": 0.0,
            "total_decisions": 0,
        }


# Launch the audit service
if __name__ == "__main__":
    mcp = _get_mcp()

    mcp.tool()(get_latest_decisions)
    mcp.tool()(get_latest_detection)
    mcp.tool()(get_footfall_prediction)
    mcp.tool()(get_traffic_training_history)
    mcp.tool()(get_energy_statistics)

    mcp.run()
