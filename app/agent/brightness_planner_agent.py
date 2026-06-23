"""Brightness planner agent module.

This module defines the LumanSense Brightness Planner Agent, which plans future lamp
brightness levels using state transition probabilities.
"""

import os
from typing import Any

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.agent.stats_agent import predict_distribution_n_steps

load_dotenv()

# --- Configuration Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
TRAFFIC_MOVEMENT_HISTORY_PATH = os.path.abspath(
    os.path.join(current_dir, "../traffic_history.log")
)

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


def discover_brightness_plan():
    """Tool wrapper to plan and print future brightness levels for Zone A."""
    brightness_plan = plan_brightness_for_steps(current_zone="A", n_steps=3)
    print("Discovered plan_brightness_per_zone (3 steps) for Zone A:", brightness_plan)


def plan_brightness_for_steps(
    current_zone: str,
    n_steps: int,
) -> list[dict[str, Any]]:
    """Predicts the expected brightness for the next n steps based on state transitions.

    Args:
        current_zone: The current state name (e.g. "Z1").
        n_steps: Number of future transition steps/paths to plan for.

    Returns:
        A list of dictionaries mapping zone names to their planned parameters
        (zone, probability distribution, and target brightness).
    """
    brightess_plan_with_n_step_hop = []
    probability_distribution = predict_distribution_n_steps(
        current_state=current_zone, n_steps=n_steps
    )

    for zone, dist in probability_distribution.items():
        plan = {
            zone: {
                "zone": zone,
                "prob dist": dist,
                "brightness": 50 if dist <= 0.5 else 90,
            }
        }
        brightess_plan_with_n_step_hop.append(plan)
    return brightess_plan_with_n_step_hop


brightness_planner_agent = Agent(
    name="brightness_planner_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are the Luman-Sense Brightness Planner Agent.
    You plan future lamp brightness levels using transition probabilities of traffic states.
    Use the discover_brightness_plan tool to predict expected brightness.
    """,
    tools=[discover_brightness_plan],
)

if __name__ == "__main__":
    discover_brightness_plan()
