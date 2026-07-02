"""Pedestrian traffic analysis and transition forecasting engine.

This module provides functions to calculate state transition probabilities and
forecast pedestrian occupancy distributions across lighting zones using historical traffic telemetry.
"""

from app.camera_feed.traffic_pattern import build_probability_matrix
from app.camera_feed.traffic_pattern import (
    build_transition_matrix as _build_transition_matrix,
)


def build_transition_matrix() -> dict:
    """Reads historical pedestrian traffic logs and builds a transition count matrix between lighting zones.

    Returns:
        A dictionary containing transition counts in nested and flat formats:
            - "nested_dict" (dict): Nested zone-to-zone counts.
            - "string_keys" (dict): Zone-to-zone string keys and counts.
            - "tuple_keys" (dict): Zone-to-zone tuple keys and counts.
    """
    return _build_transition_matrix()


def get_transition_matrix() -> dict:
    """Calculates zone transition probabilities from the aggregated traffic counts.

    Returns:
        A dictionary with:
            - "states" (list[str]): Sorted lighting zone identifiers.
            - "matrix" (dict): Nested transition probability dictionary mapping starting zones to target zones.
    """
    counts = build_transition_matrix()
    states, prob_matrix = build_probability_matrix(counts["nested_dict"])
    return {"states": states, "matrix": prob_matrix}


def get_state_vector(current_state: str, states: list[str]) -> list[float]:
    """Converts a starting lighting zone identifier to a probability distribution vector.

    Args:
        current_state: The starting zone name (e.g., "A").
        states: The list of sorted known zones.

    Returns:
        A list of floats representing the one-hot starting zone probability vector.

    Raises:
        ValueError: If `current_state` is not in the list of known zones.
    """
    n_states = len(states)
    if current_state not in states:
        raise ValueError(f"State '{current_state}' not found in known states: {states}")
    vector = [0.0] * n_states
    vector[states.index(current_state)] = 1.0
    return vector


def predict_distribution_n_steps(current_state: str, n_steps: int) -> dict[str, float]:
    """Predicts the pedestrian occupancy probability distribution across zones after n transition hops.

    Args:
        current_state: The current starting zone name (e.g., "A").
        n_steps: The number of transition intervals to forecast ahead.

    Returns:
        A dictionary mapping each zone identifier to its forecasted probability after n transitions.

    Raises:
        ValueError: If `n_steps` is negative or current_state is invalid.
    """
    if n_steps < 0:
        raise ValueError("n_steps must be non-negative")

    data = get_transition_matrix()
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


def get_exponential_moving_averages(x_list: list[float], alpha: float) -> list[float]:
    """Computes the exponential moving average of a list of numbers.

    Args:
        x_list: The list of numbers.
        alpha: The smoothing factor.

    Returns:
        A list of the same length as x_list, where each element is the EMA of the corresponding element in x_list.
    """
    ema_list = []
    ema = x_list[0]
    ema_list.append(ema)
    for i in range(1, len(x_list)):
        ema = alpha * x_list[i] + (1 - alpha) * ema
        ema_list.append(ema)
    return ema_list


def get_five_point_summary(x_list: list):
    """Computes the five point summary of a list of numbers.

    Args:
        x_list: The list of numbers.

    Returns:
        A tuple of (min, Q1, median, Q3, max).
    """
    x_list.sort()
    n = len(x_list)
    q1 = x_list[n // 4]
    median = x_list[n // 2]
    q3 = x_list[3 * n // 4]
    return (x_list[0], q1, median, q3, x_list[-1])
