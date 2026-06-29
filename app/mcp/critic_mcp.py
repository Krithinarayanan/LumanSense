from app.mcp.database_mcp import get_zone_config
from app.mcp.database_mcp import get_detection_events_by_zone
from app.mcp.database_mcp import get_decision_events_by_zone
from app.mcp.database_mcp import get_traffic_training_history as _get_traffic_training_history
import sqlite3

# FIX: FastMCP imported lazily — only when MCP server process starts,
# not at import time. This prevents ModuleNotFoundError in Streamlit/agent.
_mcp_instance = None

def _get_mcp():
    global _mcp_instance
    if _mcp_instance is None:
        from mcp.server.fastmcp import FastMCP
        _mcp_instance = FastMCP("CriticMCP")
    return _mcp_instance


def get_latest_decisions(zone: str):
    return get_decision_events_by_zone(zone, limit=10)


def get_latest_detection(zone: str):
    return get_detection_events_by_zone(zone, limit=80)


def get_footfall_prediction(zone: str):
    return get_zone_config(zone)


def get_traffic_training_history(zone: str):
    return _get_traffic_training_history(zone)


def get_energy_statistics(zone: str):
    # placeholder — implement as needed
    return {}


# ── MCP server entrypoint ──────────────────────────────────────────────────────
# Run with:  uv run python -m app.mcp.critic_mcp
if __name__ == "__main__":
    mcp = _get_mcp()

    mcp.tool()(get_latest_decisions)
    mcp.tool()(get_latest_detection)
    mcp.tool()(get_footfall_prediction)
    mcp.tool()(get_traffic_training_history)
    mcp.tool()(get_energy_statistics)

    mcp.run()