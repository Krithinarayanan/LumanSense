"""Event type definitions.

This module defines the EventType enum classifying pedestrian activity events in
particular lighting zones.
"""

from enum import Enum


class EventType(Enum):
    """Enumeration of possible pedestrian activity event types."""

    LOW_ACTIVITY = "LOW_ACTIVITY"
    NORMAL_ACTIVITY = "NORMAL_ACTIVITY"
    PEDESTRIAN_SPIKE = "PEDESTRIAN_SPIKE"

    PEAK_FORMING = "PEAK_FORMING"
    CLEARING = "CLEARING"
