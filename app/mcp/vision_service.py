"""Vision MCP service module.

This module exposes the VisionMCP tool server for classifying and processing pedestrian detection events.
"""

from mcp.server.fastmcp import FastMCP

from app.events.event import DetectionEvent
from app.events.event_bus import event_queue
from app.events.event_types import EventType
from app.events.trend_types import TrendType
from app.mcp.trend_analyzer import calculate_exponential_moving_averages

mcp = FastMCP("VisionMCP")

previous_event_types = {}


def classify_event(
    pedestrians: int,
    trend: TrendType,
    ema: float,
) -> EventType:
    """Classifies pedestrian activity using hysteresis and EMA logic.

    Args:
        pedestrians: Count of pedestrians detected.
        trend: The direction of pedestrian traffic changes.
        ema: Exponential moving average baseline of pedestrian counts.

    Returns:
        The EventType classification representing the current state.
    """

    delta = pedestrians - ema

    # Low activity branch
    if pedestrians < 15:
        if delta < -5 and trend == TrendType.DECREASING:
            return EventType.CLEARING

        return EventType.LOW_ACTIVITY

    # High activity branch
    if pedestrians > 50:
        if delta > 5 and trend == TrendType.INCREASING:
            return EventType.PEAK_FORMING

        return EventType.PEDESTRIAN_SPIKE

    # Mid-range activity
    return EventType.NORMAL_ACTIVITY


def _create_detection_event(
    eventid: int,
    zone: str,
    pedestrians: int,
    timestamp: str,
    current_event_type: EventType,
    trend: TrendType,
    ema: float,
) -> DetectionEvent:
    """Creates a DetectionEvent instance from raw data and metrics.

    Args:
        eventid: Unique identifier for the event.
        zone: Zone name where the detection occurred.
        pedestrians: Count of pedestrians detected.
        timestamp: Time of the detection.
        current_event_type: The classified event type.
        trend: Current pedestrian traffic trend.
        ema: Exponential moving average baseline of pedestrian counts.

    Returns:
        A DetectionEvent instance.
    """
    return DetectionEvent(
        eventid=eventid,
        event_type=current_event_type,
        pedestrians=pedestrians,
        timestamp=timestamp,
        zone=zone,
        trend=trend,
        ema=ema,
        delta=pedestrians - ema,
        flag=(previous_event_types.get(zone) != current_event_type),
    )


async def _enqueue_event(event: DetectionEvent | None) -> None:
    """Enqueues the detection event into the global event queue.

    Args:
        event: DetectionEvent instance or None to indicate queue termination.
    """
    await event_queue.put(event)


@mcp.tool()
async def process_detection(eventid: int, zone: str, pedestrians: int, timestamp: str) -> dict:
    """Processes a raw vision detection, generating and queueing event if state changes.

    Args:
        eventid: Unique identifier for the event.
        zone: Zone name where the pedestrian detection occurred.
        pedestrians: Count of pedestrians detected.

    Returns:
        A dict containing the processed pedestrian count and the event type state.
    """
    global previous_event_types
    if not zone:
        await _enqueue_event(None)
        return {
            "pedestrians": pedestrians,
            "event_type": "None",
        }
    (trend, ema) = calculate_exponential_moving_averages(zone, pedestrians)
    current_event_type = classify_event(pedestrians, trend, ema)

    event = _create_detection_event(
        eventid=eventid,
        zone=zone,
        pedestrians=pedestrians,
        timestamp=timestamp,
        current_event_type=current_event_type,
        trend=trend,
        ema=ema,
    )
    await _enqueue_event(event)

    previous_event_types[zone] = current_event_type
    return {
        "pedestrians": pedestrians,
        "event_type": current_event_type.value,
    }


if __name__ == "__main__":
    mcp.run()
