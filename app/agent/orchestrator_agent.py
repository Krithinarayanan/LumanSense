"""Orchestrator module.

This module defines the LumanSense Environmental Coordinator, which coordinates
lighting efficiency and routes events to specialized controller components.
"""

import os

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini

from .controller_agent import controller_agent

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

# Initialize Environmental Coordinator
orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    You are the LumanSense Environmental Coordinator.
    Your goal is to maximize lighting efficiency and public safety by delegating operational tasks based on the context.

    ### Routing Rules:
    1. **Real-time Operations:** For all ongoing sensor inputs, pedestrian detections, and flicker-prevention decisions, delegate to the automated dimmer controller.
    2. **Constraints:**
       - Never attempt to perform direct actuation logic yourself; always delegate to the controller.
       - If you receive ambiguous telemetry inputs, prioritize street-lighting stability and consult the automated dimmer controller.

    ### Workflow:
    - Receive sensor event -> Analyze activity level -> Coordinate with the appropriate controller component -> Return actuation response.
    """,
    sub_agents=[controller_agent],
)

app = App(
    root_agent=orchestrator_agent,
    name="app",
)
