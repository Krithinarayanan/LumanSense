"""Pedestrian scenario data for simulations.

This module defines lists of mock detections representing varying pedestrian activity levels
(low, normal, high, clearing, spike) across different zones over time.
"""

scenarios = [
    [
        {"timestamp": "10:01", "zone": "A", "pedestrians": 1},
        {"timestamp": "10:02", "zone": "B", "pedestrians": 1},
        {"timestamp": "10:03", "zone": "C", "pedestrians": 1},
        {"timestamp": "10:04", "zone": "D", "pedestrians": 1},
    ],
    [
        {"timestamp": "10:05", "zone": "A", "pedestrians": 3},
        {"timestamp": "10:06", "zone": "B", "pedestrians": 3},
        {"timestamp": "10:07", "zone": "C", "pedestrians": 2},
        {"timestamp": "10:08", "zone": "B", "pedestrians": 1},
        {"timestamp": "10:09", "zone": "D", "pedestrians": 2},
    ],
    [
        {"timestamp": "10:10", "zone": "A", "pedestrians": 8},
        {"timestamp": "10:11", "zone": "B", "pedestrians": 7},
        {"timestamp": "10:12", "zone": "C", "pedestrians": 6},
        {"timestamp": "10:13", "zone": "D", "pedestrians": 5},
    ],
    [
        {"timestamp": "10:24", "zone": "B", "pedestrians": 4},
        {"timestamp": "10:25", "zone": "C", "pedestrians": 5},
        {"timestamp": "10:26", "zone": "B", "pedestrians": 2},
        {"timestamp": "10:27", "zone": "D", "pedestrians": 4},
    ],
    [
        {"timestamp": "10:45", "zone": "A", "pedestrians": 1},
        {"timestamp": "10:46", "zone": "B", "pedestrians": 1},
        {"timestamp": "10:47", "zone": "D", "pedestrians": 1},
    ],
    [
        {"timestamp": "10:48", "zone": "A", "pedestrians": 10},
        {"timestamp": "10:49", "zone": "B", "pedestrians": 9},
        {"timestamp": "10:50", "zone": "C", "pedestrians": 8},
        {"timestamp": "10:51", "zone": "D", "pedestrians": 8},
    ],
    [
        {"timestamp": "09:00", "zone": "C", "pedestrians": 4},
        {"timestamp": "09:01", "zone": "B", "pedestrians": 2},
        {"timestamp": "09:02", "zone": "A", "pedestrians": 1},
    ],
]
