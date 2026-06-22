"""Traffic pattern utilities module.

This module provides tools for building transition matrices, probability distributions,
and printing matrix tables from historical pedestrian journeys.
"""

from app.training_data import journeys


def build_transition_matrix(traffic_history_records_path: str | None = None) -> dict:
    """Builds a transition count matrix from history records.

    Args:
        traffic_history_records_path: Optional path to the traffic logs.

    Returns:
        A dict containing transition counts in nested and flat formats.
    """

    # Build transition counts
    transitions = {}
    for journey in journeys:
        path = journey.get("path", [])
        for i in range(len(path) - 1):
            from_state = path[i]
            to_state = path[i + 1]
            transition = (from_state, to_state)
            transitions[transition] = transitions.get(transition, 0) + 1

    # Format transition changes dict in multiple common formats for clarity
    nested_transitions = {}
    string_transitions = {}
    for (f_state, t_state), count in transitions.items():
        # String key format: "A -> B"
        key = f"{f_state} -> {t_state}"
        string_transitions[key] = count

        # Nested dict format: {"A": {"B": 1}}
        if f_state not in nested_transitions:
            nested_transitions[f_state] = {}
        nested_transitions[f_state][t_state] = count

    return {
        "tuple_keys": transitions,
        "string_keys": string_transitions,
        "nested_dict": nested_transitions,
    }


def build_probability_matrix(nested_dict: dict) -> tuple[list[str], dict]:
    """
    Builds a transition probability distribution matrix from transition counts.
    """
    # 1. Identify all unique states
    all_states = set(nested_dict.keys())
    for target_states in nested_dict.values():
        all_states.update(target_states.keys())

    sorted_states = sorted(all_states)

    # 2. Build probability matrix: {from_state: {to_state: prob}}
    prob_matrix = {}
    for from_state in sorted_states:
        prob_matrix[from_state] = dict.fromkeys(sorted_states, 0.0)

        outgoing = nested_dict.get(from_state, {})
        total_transitions = sum(outgoing.values())

        if total_transitions > 0:
            for to_state, count in outgoing.items():
                prob_matrix[from_state][to_state] = count / total_transitions
        else:
            prob_matrix[from_state][from_state] = 1.0

    return sorted_states, prob_matrix


def pretty_print_matrix(states: list[str], prob_matrix: dict):
    """
    Pretty prints the transition probability matrix as a table.
    """
    # Print header
    header = f"{'State':<6} | " + " | ".join(f"{s:<6}" for s in states)
    print(header)
    print("-" * len(header))

    # Print rows
    for from_state in states:
        row_str = f"{from_state:<6} | "
        row_values = []
        for to_state in states:
            prob = prob_matrix[from_state][to_state]
            row_values.append(f"{prob:<6.2f}")
        row_str += " | ".join(row_values)
        print(row_str)


if __name__ == "__main__":
    result = build_transition_matrix()
    print("Transition Counts (String Keys):")
    print(result["string_keys"])
    print("\nTransition Counts (Nested Dict):")
    print(result["nested_dict"])

    print("\nTransition Probability Matrix:")
    states, prob_matrix = build_probability_matrix(result["nested_dict"])
    pretty_print_matrix(states, prob_matrix)
