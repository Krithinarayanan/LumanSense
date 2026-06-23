"""Vision MCP service module.

This module exposes the VisionMCP tool server for classifying and processing pedestrian detection events.
"""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

from app.events.event import DetectionEvent
from app.events.event_bus import event_queue
from app.events.event_types import EventType
from app.events.trend_types import TrendType
from app.mcp.trend_analyzer import calculate_exponential_moving_averages

mcp = FastMCP("VisionMCP")
previous_event_type = None


previous_event_types = {}


def classify_event(
    zone: str,
    pedestrians: int,
    trend: TrendType = TrendType.STABLE,
    ema: float = 3.0,
) -> EventType:
    """Classifies pedestrian activity using hysteresis and EMA logic.

    Args:
        zone: Zone name where pedestrian activity occurs.
        pedestrians: Count of pedestrians detected.
        trend: The direction of pedestrian traffic changes.
        ema: Exponential moving average baseline of pedestrian counts.

    Returns:
        The EventType classification representing the current state.
    """

    delta = pedestrians - ema

    # Low activity branch
    if pedestrians < 3:
        if delta < -2 and trend == TrendType.DECREASING:
            return EventType.CLEARING

        return EventType.LOW_ACTIVITY

    # High activity branch
    if pedestrians > 5:
        if delta > 2 and trend == TrendType.INCREASING:
            return EventType.PEAK_FORMING

        return EventType.PEDESTRIAN_SPIKE

    # Mid-range activity
    return EventType.NORMAL_ACTIVITY


@mcp.tool()
async def process_detection(eventid: int, zone: str, pedestrians: int) -> dict:
    """Processes a raw vision detection, generating and queueing event if state changes.

    Args:
        eventid: Unique identifier for the event.
        zone: Zone name where the pedestrian detection occurred.
        pedestrians: Count of pedestrians detected.

    Returns:
        A dict containing the processed pedestrian count and the event type state.
    """
    global previous_event_type
    if not zone:
        await event_queue.put(None)
        return {
            "pedestrians": pedestrians,
            "event_type": "None",
        }
    (trend, ema) = calculate_exponential_moving_averages(zone, pedestrians)
    current_event_type = classify_event(zone, pedestrians, trend, ema)
    if current_event_type != previous_event_type:
        await event_queue.put(
            DetectionEvent(
                eventid=eventid,
                event_type=current_event_type,
                pedestrians=pedestrians,
                timestamp=datetime.now(),
                zone=zone,
                trend=trend,
                ema=ema,
                delta=pedestrians - ema,
            )
        )
        previous_event_type = current_event_type
    return {
        "pedestrians": pedestrians,
        "event_type": current_event_type.value,
    }


if __name__ == "__main__":
    mcp.run()
