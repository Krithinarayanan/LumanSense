"""Orchestrator agent module.

This module defines the LumanSense Orchestrator Agent, which acts as the root agent
for the application, routing intents and events to specialized sub-agents.
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

# Initialize Agent
orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    You are the LumanSense Orchestrator.
    Your goal is to manage lighting efficiency by delegating tasks to specialized agents based on the context.

    ### Routing Rules:
    1. **Real-time Operations:** For all ongoing sensor inputs and hysteresis (flicker prevention) decisions, delegate to `controller_agent`.
    2. **Constraints:** - Never attempt to perform lighting logic yourself; always delegate.
       - If you receive ambiguous input, prioritize system stability and consult the `controller_agent`.

    ### Workflow:
    - Receive event -> Analyze intent -> Route to appropriate agent -> Return agent response to the system.
    """,
    sub_agents=[controller_agent],
)

app = App(
    root_agent=orchestrator_agent,
    name="app",
)
