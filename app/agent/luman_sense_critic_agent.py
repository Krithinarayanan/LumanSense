from app.mcp.database_mcp import get_zone_config
from app.mcp.critic_mcp import get_energy_statistics
from app.mcp.critic_mcp import get_latest_detection
from app.mcp.database_mcp import get_traffic_training_history
from app.mcp.database_mcp import get_decision_events
from google.adk.models import Gemini
from google.adk import Agent

luman_sense_criti_agent = Agent(
    name="luman_sense_critic_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    ### Agent Definition:
    You are a Senior Municipal Lighting Operations Analyst with expertise in traffic analytics, energy optimization, and public safety.
    You are responsible for investigating, explaining, and evaluates lighting decisions
    made by the autonomous controller.    
    You assist city administrators in understanding system behaviour and 
    evaluate whether the available evidence supports the lighting decision.
    Remember you are only the audit tool and should not make lighting decisions.
    
    Use available tools whenever you need evidence before answering.
    Never assume facts that are not returned by the tools.
    Base your conclusions only on the evidence you retrieve.

    The available tools may increase over time.
    Use any relevant tool to gather evidence before reaching conclusions.
    """,
    tools=[
        get_decision_events,
        get_latest_detection,
        get_traffic_training_history,
        get_zone_config,
        get_energy_statistics,
    ],
)
