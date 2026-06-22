"""Detection event module.

This module defines the DetectionEvent dataclass representing pedestrian detection from vision sensors.
"""

from dataclasses import dataclass
from datetime import datetime

from .event_types import EventType


@dataclass
class DetectionEvent:
    """Dataclass representing a vision sensor pedestrian detection event.

    Attributes:
        event_type: The EventType classifying the pedestrian counts.
        pedestrians: Count of pedestrians detected.
        timestamp: The datetime the event was captured.
        zone: Optional zone name where detection occurred.
    """

    eventid: int
    event_type: EventType
    pedestrians: int
    timestamp: datetime
    zone: str | None = None

    @property
    def new_brightness(self) -> int:
        """Determines the target brightness level based on the event type."""
        if self.event_type == EventType.PEDESTRIAN_SPIKE:
            return 90
        elif self.event_type == EventType.LOW_ACTIVITY:
            return 50
        return 0
