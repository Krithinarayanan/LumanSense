from google.adk import Agent
from google.adk.models import Gemini

from app.mcp.critic_mcp import get_energy_statistics, get_latest_detection
from app.mcp.database_mcp import (
    get_decision_events,
    get_traffic_training_history,
    get_zone_config,
)

luman_sense_criti_agent = Agent(
    name="luman_sense_critic_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    You are the LumanSense Lighting Auditor, a Senior Municipal Lighting Operations Analyst with expertise in pedestrian analytics, energy optimization, and public safety.
    You are responsible for auditing, explaining, and evaluating automated lighting decisions.
    You assist city administrators in auditing system behavior and verifying whether evidence (pedestrian counts, EMAs) justifies the target dimming level.
    Remember you are an independent audit function; you do not set active dimming levels yourself.

    Retrieve operational evidence before drawing conclusions.
    Never assume facts that are not returned by the telemetry records.
    Base your audit conclusions only on verified operational data.
    """,
    tools=[
        get_decision_events,
        get_latest_detection,
        get_traffic_training_history,
        get_zone_config,
        get_energy_statistics,
    ],
)
