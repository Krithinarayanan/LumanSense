"""Ask luman Agent module.

This module defines the ask_luman_agent, which helps users query and analyze
smart lighting database statistics, run predictions, and audit decisions.
"""

import os
import sqlite3

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.agent.luman_sense_critic_agent import luman_sense_criti_agent
from app.analytics.stats_engine import predict_distribution_n_steps
from app.mcp.database_mcp import (
    get_average_pedestrians,
    get_decision_event,
    get_detection_event,
    get_total_energy_saved,
    get_zone_config,
)

load_dotenv()

# --- Configuration Setup ---
use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
if use_vertex:
    try:
        _, project_id = google.auth.default()
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "placeholder-project")
    os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get(
        "GOOGLE_CLOUD_LOCATION", "global"
    )


# Static whitelisted tables and default columns to secure database access
# (Used as fallback if database doesn't exist or is empty during initialization)
STATIC_WHITELISTED_COLUMNS = {
    "detection_events": ["id", "timestamp", "zone", "pedestrians", "ema", "trend_label", "zone_occupancy_forecast", "delta_occupancy", "cluster_label"],
    "decision_events": ["id", "timestamp", "zone", "state", "pred_brightness", "reactive_brightness", "brightness", "reason", "energy_saved_watts"],
    "zone_config": ["id", "zone", "forecast", "brightness"],
    "trained_cluster_data": ["id", "timestamp", "cluster_id", "zone", "pedestrians", "ema"],
    "zone_centroids_data": ["id", "cluster_index", "zone", "pedestrians", "ema"],
    "footfall_predictions": ["id", "zone", "probability", "brightness"]
}


def load_whitelisted_columns() -> dict:
    """Dynamically queries the SQLite database schema to build table column whitelists.

    This ensures that when columns are added or removed (e.g., carbon_saved),
    the whitelist updates automatically at runtime without code modifications.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_dir, "../../luman_sense.db"))

    # If the database doesn't exist yet, return the static fallback
    if not os.path.exists(db_path):
        return STATIC_WHITELISTED_COLUMNS

    db_uri = f"file:{db_path}?mode=ro"
    schema = {}
    try:
        conn = sqlite3.connect(db_uri, uri=True)
        cursor = conn.conn.cursor() if hasattr(conn, "conn") else conn.cursor()
        for table in STATIC_WHITELISTED_COLUMNS.keys():
            # Query column names dynamically from SQLite system metadata
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            if columns:
                schema[table] = columns
            else:
                schema[table] = STATIC_WHITELISTED_COLUMNS[table]
        conn.close()
        return schema
    except Exception:
        # Fallback to static columns if anything goes wrong
        return STATIC_WHITELISTED_COLUMNS


def query_table_records(
    table_name: str,
    columns: list[str] = None,
    filters: dict = None,
    limit: int = 50
) -> dict:
    """Safely queries records from the municipal database without executing raw SQL query strings.

    Args:
        table_name: The table to query (must be one of: 'detection_events', 'decision_events', 'zone_config', 'trained_cluster_data', 'zone_centroids_data', 'footfall_predictions').
        columns: The list of specific columns to retrieve. Defaults to all whitelisted columns.
        filters: A key-value dictionary of filter conditions (e.g. {"zone": "A"}). All values are parameterized.
        limit: The maximum number of records to return (defaults to 50, maximum 100).

    Returns:
        A dictionary containing status ('success' or 'error') and the query results (list of row dicts).
    """
    whitelists = load_whitelisted_columns()
    if table_name not in whitelists:
        return {
            "status": "error",
            "message": f"Unauthorized or invalid table: '{table_name}'.",
        }

    valid_columns = whitelists[table_name]

    if columns:
        # Filter out columns that are not whitelisted
        sanitized_columns = [col for col in columns if col in valid_columns]
        if not sanitized_columns:
            sanitized_columns = valid_columns
    else:
        sanitized_columns = valid_columns

    col_str = ", ".join(sanitized_columns)
    query = f"SELECT {col_str} FROM {table_name}"
    params = []

    if filters:
        conditions = []
        for col, val in filters.items():
            if col in valid_columns:
                conditions.append(f"{col} = ?")
                params.append(val)
            else:
                return {
                    "status": "error",
                    "message": f"Unauthorized or invalid filter column: '{col}' in table '{table_name}'.",
                }
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    # Enforce hard upper limit
    safe_limit = min(max(1, limit), 100)
    query += " LIMIT ?"
    params.append(safe_limit)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_dir, "../../luman_sense.db"))
    db_uri = f"file:{db_path}?mode=ro"

    try:
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return {
            "status": "success",
            "results": [dict(row) for row in rows],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database execution error: {e!s}",
        }


def query_aggregation(
    operation: str,
    column: str,
    table_name: str,
    group_by: str = None
) -> dict:
    """Executes safe, predefined math aggregations (AVG, SUM, COUNT, MIN, MAX) over whitelisted tables.

    Args:
        operation: The aggregation function to apply (must be one of: 'avg', 'sum', 'count', 'min', 'max').
        column: The column to aggregate.
        table_name: Whitelisted table to query.
        group_by: Optional column name to group results by (e.g. 'zone').

    Returns:
        A dictionary containing status ('success' or 'error') and aggregation results.
    """
    operation_upper = operation.upper()
    if operation_upper not in ("AVG", "SUM", "COUNT", "MIN", "MAX"):
        return {
            "status": "error",
            "message": f"Unauthorized or invalid aggregation operation: '{operation}'. Allowed: AVG, SUM, COUNT, MIN, MAX.",
        }

    whitelists = load_whitelisted_columns()
    if table_name not in whitelists:
        return {
            "status": "error",
            "message": f"Unauthorized or invalid table: '{table_name}'.",
        }

    valid_columns = whitelists[table_name]

    if column not in valid_columns and column != "*":
        return {
            "status": "error",
            "message": f"Unauthorized or invalid column: '{column}' for table '{table_name}'.",
        }

    if group_by and group_by not in valid_columns:
        return {
            "status": "error",
            "message": f"Unauthorized or invalid group-by column: '{group_by}' for table '{table_name}'.",
        }

    # Count can use * or a specific column. Other aggregations need a specific column.
    if operation_upper != "COUNT" and column == "*":
        return {
            "status": "error",
            "message": "Wildcard '*' is only supported with COUNT operations.",
        }

    if group_by:
        query = f"SELECT {group_by}, {operation_upper}({column}) as result FROM {table_name} GROUP BY {group_by}"
    else:
        query = f"SELECT {operation_upper}({column}) as result FROM {table_name}"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_dir, "../../luman_sense.db"))
    db_uri = f"file:{db_path}?mode=ro"

    try:
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return {
            "status": "success",
            "results": [dict(row) for row in rows],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database aggregation error: {e!s}",
        }


ask_luman_agent = Agent(
    name="ask_luman_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are the lumanSense Smart Lighting Analyst.
    Your purpose is to analyze and answer queries about the LumanSense smart lighting system, its pedestrian traffic sensor telemetry, and automated dimming decisions.

    You have functions to query the municipal database and predict future occupancy distributions:
    - Use query_table_records to safely fetch data rows from whitelisted tables (e.g., detection_events, decision_events, zone_config, trained_cluster_data, zone_centroids_data).
    - Use query_aggregation to calculate totals, counts, or averages of metrics (e.g. sum of energy_saved_watts, avg of pedestrians).
    - Use get_detection_event and get_decision_event to fetch recent historical event logs.
    - Use get_average_pedestrians and get_total_energy_saved to retrieve system performance metrics.
    - Use get_zone_config to retrieve zone parameters.
    - Use predict_distribution_n_steps to forecast pedestrian traffic flow over future intervals.

    If requested to audit, evaluate, or investigate specific lighting decisions or operational safety, delegate to the lighting auditor.

    Guidelines:
    - Answer queries clearly, professionally, and concisely.
    - Use data from the functions to provide accurate metrics.
    - Format comparative tables in clear Markdown.
    - Explain municipal energy savings, pedestrian patterns, and optimization outcomes when asked.
    - Never attempt to write raw SQL commands or execute raw database queries.
    """,
    tools=[
        query_table_records,
        query_aggregation,
        get_detection_event,
        get_decision_event,
        get_average_pedestrians,
        get_total_energy_saved,
        get_zone_config,
        predict_distribution_n_steps,
    ],
    sub_agents=[luman_sense_criti_agent],
)
