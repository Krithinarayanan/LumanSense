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
        eventid: Unique identifier for the event.
        event_type: The EventType classifying the pedestrian counts.
        pedestrians: Count of pedestrians detected.
        timestamp: The datetime the event was captured.
        ema: Exponential moving average of the pedestrian counts in the zone.
        trend: Current classified pedestrian trend.
        delta: The difference between current counts and the EMA.
        zone: Optional zone name where detection occurred.
    """

    eventid: int
    event_type: EventType
    pedestrians: int
    timestamp: datetime
    ema: float
    trend: str
    delta: float
    flag:bool
    zone: str | None = None
    cluster_label: str = "None"
    trend_label: str = "@TODO"
    current_occupancy_forecast: int = 0
    delta_occupancy: float = 0.0

    @property
    def new_brightness(self) -> int:
        """Determines the target brightness level based on the event type.

        Returns:
            The calculated target brightness percentage (0-100).
        """
        match self.event_type:
            case EventType.LOW_ACTIVITY:
                return 30

            case EventType.CLEARING:
                return 50

            case EventType.NORMAL_ACTIVITY:
                return 60

            case EventType.PEAK_FORMING:
                return 80

            case EventType.PEDESTRIAN_SPIKE:
                return 100

            case _:
                return 0
