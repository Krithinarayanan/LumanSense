"""Trend Analyzer MCP service module.

This module exposes the TrendAnalyzer tool server for analyzing pedestrian traffic trends.
"""

from collections import defaultdict

from mcp.server.fastmcp import FastMCP

from app.events.trend_types import TrendType
from app.training_data import journeys

mcp = FastMCP("TrendAnalyzer")

zone_wise_ema = {}


@mcp.tool()
def get_traffic_trends() -> list[dict]:
    """Aggregates training journey paths by timestamp and zone, returning traffic counts.

    Returns:
        A list of dictionaries containing:
            - "timestamp" (str): Time of detection.
            - "zone" (str): Lighting zone label.
            - "count" (int): Count of pedestrian transitions.
    """
    counts = defaultdict(int)
    for journey in journeys:
        path = journey.get("path", [])
        for step in path:
            ts = step.get("timestamp")
            zone = step.get("zone")
            if ts and zone:
                counts[(ts, zone)] += 1

    result = []
    for (ts, zone), count in counts.items():
        result.append({"timestamp": ts, "zone": zone, "count": count})
    result.sort(key=lambda x: (x["timestamp"], x["zone"]))
    return result


@mcp.tool()
def update_ema_and_trend(zone: str, pedestrian: int) -> tuple[TrendType, float]:
    """Calculates the Exponential Moving Average (EMA) and husterically classifies the trend.

    Args:
        zone: Zone name where the pedestrian detection occurred.
        pedestrian: Count of pedestrians detected.

    Returns:
        A tuple containing:
            - trend (TrendType): The classified trend type (INCREASING, DECREASING, STABLE).
            - ema (float): The newly calculated Exponential Moving Average.
    """
    alpha = 0.3
    ema = zone_wise_ema.get(zone, None)
    if ema is None:
        ema = float(pedestrian)
        zone_wise_ema[zone] = ema
        return (TrendType.STABLE, ema)
    else:
        old_ema = ema
        ema = alpha * pedestrian + (1 - alpha) * ema
        zone_wise_ema[zone] = ema
        delta = ema - old_ema
        trend = (
            TrendType.INCREASING
            if delta > 0.1
            else TrendType.DECREASING
            if delta < -0.1
            else TrendType.STABLE
        )
        return (trend, ema)


if __name__ == "__main__":
    mcp.run()
