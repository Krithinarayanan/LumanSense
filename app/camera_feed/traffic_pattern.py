"""Traffic pattern utilities module.

This module provides tools for building transition matrices, probability distributions,
and printing matrix tables from historical traffic data.
"""

from app.data_parser import parse_traffic_data


def build_transition_matrix() -> dict:
    """Builds a transition count matrix from historical traffic data.

    Returns:
        A dict containing transition counts in nested and flat formats:
            - "tuple_keys" (dict): Dict with tuple keys (from_zone, to_zone) and counts.
            - "string_keys" (dict): Dict with string keys "from_zone -> to_zone" and counts.
            - "nested_dict" (dict): Nested dictionary with from_zone keys containing to_zone counts.
    """
    from collections import defaultdict

    records = parse_traffic_data()

    # To calculate transitions, we group by datetime to get counts for all zones at each hour
    by_datetime = defaultdict(dict)
    for r in records:
        by_datetime[r["datetime"]][r["zone"]] = r["vehicles"]

    # Sort datetimes chronologically
    sorted_dts = sorted(by_datetime.keys())

    zones = ["A", "B", "C", "D"]
    transitions = {(z_from, z_to): 0 for z_from in zones for z_to in zones}

    # Iterate through consecutive hours and calculate transition counts
    for t in range(len(sorted_dts) - 1):
        t_curr = by_datetime[sorted_dts[t]]
        t_next = by_datetime[sorted_dts[t + 1]]

        for z_from in zones:
            val_from = t_curr.get(z_from, 0)
            if val_from > 0:
                for z_to in zones:
                    val_to = t_next.get(z_to, 0)
                    transitions[(z_from, z_to)] += min(val_from, val_to)

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
    """Builds a transition probability distribution matrix from transition counts.

    Args:
        nested_dict: Nested dictionary containing transition counts.

    Returns:
        A tuple containing:
            - sorted_states (list[str]): Sorted unique state names.
            - prob_matrix (dict): Nested dictionary mapping state names to transition probabilities.
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
    """Pretty prints the transition probability matrix as a formatted table.

    Args:
        states: List of sorted state names.
        prob_matrix: Nested transition probability dictionary.
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
