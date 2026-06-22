"""Statistics agent module.

This module defines the LumanSense Statistics Agent, which computes statistical
metrics, transition counts, probability matrices, and predicts future states.
"""

import os

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.camera_feed.traffic_pattern import build_probability_matrix
from app.camera_feed.traffic_pattern import (
    build_transition_matrix as _build_transition_matrix,
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


def build_transition_matrix(traffic_history_records_path: str | None = None) -> dict:
    """
    Reads the traffic history log file and builds a transition count matrix.
    Returns:
        A dictionary containing transition counts in nested and flat formats.
    """
    return _build_transition_matrix(traffic_history_records_path)


def get_transition_matrix(traffic_history_records_path: str | None = None) -> dict:
    """
    Returns the sorted states list and the transition probability matrix.
    Returns:
        A dictionary with "states" (list of sorted state names) and "matrix" (nested probability dictionary).
    """
    counts = build_transition_matrix(traffic_history_records_path)
    states, prob_matrix = build_probability_matrix(counts["nested_dict"])
    return {"states": states, "matrix": prob_matrix}


def get_state_vector(current_state: str, states: list[str]) -> list[float]:
    """
    Converts a state name string to a probability vector.

    Args:
        current_state: The current state name (e.g. "Z1").
        states: The list of sorted state names.

    Returns:
        A list of floats representing the one-hot state probability vector.
    """
    n_states = len(states)
    if current_state not in states:
        raise ValueError(f"State '{current_state}' not found in known states: {states}")
    vector = [0.0] * n_states
    vector[states.index(current_state)] = 1.0
    return vector


def predict_distribution_n_steps(
    current_state: str, n_steps: int, traffic_history_records_path: str | None = None
) -> dict[str, float]:
    """
    Predicts the state probability distribution after n steps.

    Args:
        current_state: The current state name (e.g. "Z1").
        n_steps: The number of transition steps to predict.
    Returns:
        A dictionary mapping each state name to its probability after n steps.
    """
    if n_steps < 0:
        raise ValueError("n_steps must be non-negative")

    data = get_transition_matrix(traffic_history_records_path)
    states = data["states"]
    prob_matrix = data["matrix"]

    current_vector = get_state_vector(current_state, states)
    n_states = len(states)

    for _ in range(n_steps):
        next_vector = [0.0] * n_states
        for j in range(n_states):
            col_sum = 0.0
            for i in range(n_states):
                from_state = states[i]
                to_state = states[j]
                prob = prob_matrix[from_state].get(to_state, 0.0)
                col_sum += current_vector[i] * prob
            next_vector[j] = col_sum
        current_vector = next_vector

    return {states[k]: current_vector[k] for k in range(n_states)}


def predict_distribution(
    current_state: str, traffic_history_records_path: str | None = None
) -> dict[str, float]:
    """
    Predicts the next state probability distribution (1 step).

    Args:
        current_state: The current state name (e.g. "Z1").
        traffic_history_records_path: Optional path to the traffic history log file. If not provided,
                                      uses the default relative path.

    Returns:
        A dictionary mapping each state name to its probability in the next step.
    """
    return predict_distribution_n_steps(current_state, 1, traffic_history_records_path)


# Initialize stats_agent
stats_agent = Agent(
    name="stats_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are the Luman-Sense Statistics Agent.
    You compute statistical metrics, state transitions, and analyze history logs.
    Use the tools provided to build transition matrices, get state vectors, and predict distributions.
    """,
    tools=[
        build_transition_matrix,
        predict_distribution,
        predict_distribution_n_steps,
        get_state_vector,
        get_transition_matrix,
    ],
)

if __name__ == "__main__":
    # Test transition probability prediction
    print("Testing build_transition_matrix:")
    print(build_transition_matrix()["string_keys"])

    print("\nTesting get_transition_matrix:")
    t_mat = get_transition_matrix()
    print("States:", t_mat["states"])
    print("Matrix:", t_mat["matrix"])

    print("\nTesting predict_distribution_n_steps (3 steps) from A:")
    print(predict_distribution_n_steps("Z1", n_steps=3))
