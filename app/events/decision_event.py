"""Decision event module.

This module defines the DecisionEvent dataclass representing a control loop decision.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DecisionEvent:
    """Dataclass representing a hysteresis brightness decision for a lighting zone.

    Attributes:
        eventid: Unique identifier for the event.
        zone: The zone label (e.g. "A").
        event_type: The type of event leading to the decision.
        brightness: The brightness level (0-100) set.
        reason: The reason description for the adjustment.
        energy_saved_watts: The energy saved calculated in watts.
        timestamp: The datetime of the event decision.
    """

    eventid: int
    zone: str
    event_type: str
    brightness: int
    reason: str
    energy_saved_watts: int
    timestamp: datetime
    carbon_intensity: float = 320.0
    co2_saved_grams: float = 0.0
