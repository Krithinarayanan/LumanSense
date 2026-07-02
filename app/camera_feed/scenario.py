"""Pedestrian scenario data for simulations.

This module defines lists of mock detections representing varying pedestrian activity levels
(low, normal, high, clearing, spike) across different zones over time.
"""

scenarios = [
    [
        {"timestamp": "09:00", "zone": "A", "pedestrians": 40},
        {"timestamp": "09:00", "zone": "B", "pedestrians": 20},
        {"timestamp": "09:00", "zone": "C", "pedestrians": 10},
        {"timestamp": "09:00", "zone": "D", "pedestrians": 5},
    ],
    [
        {"timestamp": "09:05", "zone": "A", "pedestrians": 60},
        {"timestamp": "09:05", "zone": "B", "pedestrians": 25},
        {"timestamp": "09:05", "zone": "C", "pedestrians": 12},
        {"timestamp": "09:05", "zone": "D", "pedestrians": 60},
    ],
    [
        {"timestamp": "09:10", "zone": "A", "pedestrians": 10},
        {"timestamp": "09:10", "zone": "B", "pedestrians": 30},
        {"timestamp": "09:10", "zone": "C", "pedestrians": 5},
        {"timestamp": "09:10", "zone": "D", "pedestrians": 62},
    ],
    [
        {"timestamp": "09:15", "zone": "A", "pedestrians": 62},
        {"timestamp": "09:15", "zone": "B", "pedestrians": 35},
        {"timestamp": "09:15", "zone": "C", "pedestrians": 6},
        {"timestamp": "09:15", "zone": "D", "pedestrians": 60},
    ],
    [
        {"timestamp": "09:20", "zone": "A", "pedestrians": 45},
        {"timestamp": "09:20", "zone": "B", "pedestrians": 40},
        {"timestamp": "09:20", "zone": "C", "pedestrians": 8},
        {"timestamp": "09:20", "zone": "D", "pedestrians": 10},
    ],
    [
        {"timestamp": "09:25", "zone": "A", "pedestrians": 48},
        {"timestamp": "09:25", "zone": "B", "pedestrians": 42},
        {"timestamp": "09:25", "zone": "C", "pedestrians": 10},
        {"timestamp": "09:25", "zone": "D", "pedestrians": 12},
    ],
    [
        {"timestamp": "09:30", "zone": "A", "pedestrians": 50},
        {"timestamp": "09:30", "zone": "B", "pedestrians": 45},
        {"timestamp": "09:30", "zone": "C", "pedestrians": 11},
        {"timestamp": "09:30", "zone": "D", "pedestrians": 13},
    ],
]
