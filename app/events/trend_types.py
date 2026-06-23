"""Trend type definitions.

This module defines the TrendType enum classifying pedestrian traffic movement changes.
"""

from enum import Enum


class TrendType(Enum):
    """Enumeration of possible pedestrian traffic trend types."""

    STABLE = "STABLE"
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
