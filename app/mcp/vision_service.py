"""Vision MCP service module.

This module exposes the VisionMCP tool server for classifying and processing pedestrian detection events.
"""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

from app.events.event import DetectionEvent
from app.events.event_bus import event_queue
from app.events.event_types import EventType

mcp = FastMCP("VisionMCP")
previous_event_type = None


previous_event_types = {}


def classify_event(zone: str, pedestrians: int) -> EventType:
    """
    Classify activity for a specific zone using hysteresis.

    Args:
        zone: Zone identifier (A, B, C, ...)
        pedestrians: Number of pedestrians detected.

    Returns:
        EventType for the zone.
    """

    previous_state = previous_event_types.get(zone, EventType.LOW_ACTIVITY)

    if previous_state == EventType.PEDESTRIAN_SPIKE:
        if pedestrians < 3:
            new_state = EventType.LOW_ACTIVITY
        else:
            new_state = EventType.PEDESTRIAN_SPIKE

    else:
        if pedestrians > 5:
            new_state = EventType.PEDESTRIAN_SPIKE
        else:
            new_state = EventType.LOW_ACTIVITY

    previous_event_types[zone] = new_state

    return new_state


@mcp.tool()
async def process_detection(eventid: int, zone: str, pedestrians: int) -> dict:
    """Processes a raw vision detection, generating and queueing event if state changes.

    Args:
        zone: Zone name where the pedestrian detection occurred.
        pedestrians: Count of pedestrians detected.

    Returns:
        A dict containing processed pedestrian count and the event type state.
    """
    global previous_event_type
    if not zone:
        await event_queue.put(None)
        return {
            "pedestrians": pedestrians,
            "event_type": "None",
        }
    current_event_type = classify_event(zone, pedestrians)
    if current_event_type != previous_event_type:
        await event_queue.put(
            DetectionEvent(
                eventid=eventid,
                event_type=current_event_type,
                pedestrians=pedestrians,
                timestamp=datetime.now(),
                zone=zone,
            )
        )
        previous_event_type = current_event_type
    return {
        "pedestrians": pedestrians,
        "event_type": current_event_type.value,
    }


if __name__ == "__main__":
    mcp.run()
