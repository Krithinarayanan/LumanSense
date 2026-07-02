"""Pedestrian traffic telemetry module.

This module defines the DetectionEvent representing pedestrian counts and trend events
captured by municipal street-lighting sensors.
"""

from dataclasses import dataclass
from datetime import datetime

from .event_types import EventType


@dataclass
class DetectionEvent:
    """Dataclass representing a street-lighting zone pedestrian detection event.

    Attributes:
        eventid: Unique identifier for the event.
        event_type: The EventType classifying the pedestrian activity level.
        pedestrians: Count of pedestrians detected.
        timestamp: The datetime the event was captured.
        ema: Exponential moving average of the pedestrian counts in the zone.
        trend: Current classified pedestrian trend (e.g. INCREASING, DECREASING).
        delta: The difference between current counts and the EMA baseline.
        flag: Flag indicating if the activity classification state has changed.
        zone: Optional zone name where detection occurred.
        cluster_label: Classified traffic density category.
        trend_label: Long-term traffic trend summary.
        current_occupancy_forecast: Expected pedestrian occupancy for the next interval.
        delta_occupancy: Expected change in zone occupancy.
    """

    eventid: int
    event_type: EventType
    pedestrians: int
    timestamp: datetime
    ema: float
    trend: str
    delta: float
    flag: bool
    zone: str | None = None
    cluster_label: str = "None"
    trend_label: str = "UNKNOWN"
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
