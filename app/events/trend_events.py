"""Trend event module.

This module defines the TrendEvent dataclass representing computed traffic trends.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrendEvent:
    """Dataclass representing a computed pedestrian traffic trend in a zone.

    Attributes:
        timestamp: The datetime the trend was analyzed.
        zone: The zone label (e.g. "A").
        current_count: Current count of pedestrians.
        ema: Exponential Moving Average of pedestrian counts.
        trend: The trend classification string.
    """

    timestamp: datetime
    zone: str
    current_count: int
    ema: float
    trend: str
