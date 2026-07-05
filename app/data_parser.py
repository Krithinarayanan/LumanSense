"""Common traffic data parser module.

This module provides utility functions to load and parse the historical
traffic dataset from the CSV file.
"""

import os
import pandas as pd

# Global cache to avoid reading the CSV multiple times
_cached_records = None


def parse_traffic_data() -> list[dict]:
    """Parses the historical traffic CSV file.

    Translates Junction 1 -> A, 2 -> B, 3 -> C, 4 -> D.
    Returns a list of dictionaries with keys:
        - 'datetime' (str): The full date and time string.
        - 'timestamp' (str): The time of day (HH:MM).
        - 'zone' (str): The translated zone (A, B, C, or D).
        - 'vehicles' (int): The vehicle count.
    """
    global _cached_records
    if _cached_records is not None:
        return _cached_records

    # Find the CSV file path relative to this module
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(current_dir, "training-dataset", "traffic.csv"))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Traffic CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Translate Junction to Zone
    junction_to_zone = {1: "A", 2: "B", 3: "C", 4: "D"}
    df["zone"] = df["Junction"].map(junction_to_zone)

    # Parse DateTime
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["timestamp"] = df["DateTime"].dt.strftime("%H:%M")
    df["datetime_str"] = df["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Rename columns to match expected output
    df_out = df[["datetime_str", "timestamp", "zone", "Vehicles"]].rename(
        columns={"datetime_str": "datetime", "Vehicles": "vehicles"}
    )

    _cached_records = df_out.to_dict("records")
    return _cached_records
