"""Ask Lumen Agent module.

This module defines the ask_lumen_agent, which helps users query and analyze
smart lighting database statistics, run predictions, and audit decisions.
"""

import os
import sqlite3
import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.mcp.database_mcp import (
    get_detection_event,
    get_decision_event,
    get_average_pedestrians,
    get_total_energy_saved,
    get_zone_config,
)
from app.analytics.stats_engine import predict_distribution_n_steps
from app.agent.luman_sense_critic_agent import luman_sense_criti_agent

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


def query_database(sql_query: str) -> dict:
    """Executes a read-only SELECT SQL query on the smart lighting database.

    Args:
        sql_query: The SQL SELECT query string to execute. Must be a SELECT query.

    Returns:
        A dictionary containing the query results (list of row dicts) or error details.
    """
    cleaned_query = sql_query.strip()
    if not cleaned_query.lower().startswith("select"):
        return {
            "status": "error",
            "message": "Only read-only SELECT queries are allowed for security reasons.",
        }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_dir, "../../luman_sense.db"))
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(cleaned_query)
        rows = cursor.fetchall()
        conn.close()
        return {
            "status": "success",
            "results": [dict(row) for row in rows],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database execution error: {str(e)}",
        }


ask_lumen_agent = Agent(
    name="ask_lumen_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are the LumenSense Assistant, a helpful AI assistant built on the Google Agent Development Kit (ADK).
    Your purpose is to answer questions about the LumanSense smart lighting system, its traffic sensor data, and lighting control decisions.
    
    You have tools to query the system's database and predict future state distributions:
    - Use query_database to run custom SELECT SQL queries on the tables (e.g. detection_events, decision_events, zone_config, trained_cluster_data, zone_centroids_data).
    - Use get_detection_event and get_decision_event to fetch recent event logs.
    - Use get_average_pedestrians and get_total_energy_saved to retrieve global metrics.
    - Use get_zone_config to see zone configurations.
    - Use predict_distribution_n_steps to predict traffic distributions over future steps.
    
    If asked to audit, evaluate, or investigate specific decisions or system operation in detail, you can delegate to the luman_sense_critic_agent.
    
    Guidelines:
    - Answer user questions clearly and concisely.
    - Use tools to gather precise statistics rather than making them up.
    - When presenting tables, format them using markdown.
    - Give details about optimization, pedestrian activity, and energy savings when asked.
    """,
    tools=[
        query_database,
        get_detection_event,
        get_decision_event,
        get_average_pedestrians,
        get_total_energy_saved,
        get_zone_config,
        predict_distribution_n_steps,
    ],
    sub_agents=[luman_sense_criti_agent],
)
