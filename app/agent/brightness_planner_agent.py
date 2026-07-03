"""Brightness planner module.

This module defines the LumanSense Brightness Planner, which plans future street-lighting
brightness levels using zone transition probabilities.
"""

import os
from typing import Any

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

from app.analytics.stats_engine import predict_distribution_n_steps

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


class BrightnessPlannerInput(BaseModel):
    current_zone: str = Field(description="The starting zone name (e.g., 'A')")
    n_steps: int = Field(description="Number of transition hops/intervals to forecast")


class ZonePlan(BaseModel):
    zone: str = Field(description="The zone name")
    prob_dist: float = Field(
        alias="prob dist", description="The probability distribution for this zone"
    )
    brightness: int = Field(
        description="The planned street-lighting brightness level percentage (e.g. 50 or 90)"
    )


class BrightnessPlannerOutput(BaseModel):
    plans: list[ZonePlan] = Field(
        description="A list of planned parameters for each zone"
    )


def discover_brightness_plan(
    current_zone: str = "A",
    n_steps: int = 3,
) -> list[dict[str, Any]]:
    """Calculates and returns the planned future street-lighting levels for municipal zones.

    Args:
        current_zone: The starting zone name (e.g. "A").
        n_steps: Number of transition hops/intervals to forecast.

    Returns:
        A list of dictionaries containing zone names, forecasted probabilities, and target brightness levels.
    """
    return plan_brightness_for_steps(current_zone=current_zone, n_steps=n_steps)


def plan_brightness_for_steps(
    current_zone: str,
    n_steps: int,
) -> list[dict[str, Any]]:
    """Predicts the expected lighting brightness for the next n steps based on zone transition probabilities.

    Args:
        current_zone: The starting zone name (e.g. "A").
        n_steps: Number of transition hops/intervals to forecast.

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
    You are the LumanSense Brightness Planner.
    Your goal is to plan future street-lighting brightness levels across zones.
    You forecast pedestrian traffic transition probabilities using the discover_brightness_plan function.
    Optimize lighting levels to balance municipal energy conservation and public safety.
    """,
    tools=[discover_brightness_plan],
    input_schema=BrightnessPlannerInput,
    output_schema=BrightnessPlannerOutput,
)

if __name__ == "__main__":
    discover_brightness_plan()
