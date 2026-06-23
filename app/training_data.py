"""Historical pedestrian training journeys data.

This module contains a dataset of historical pedestrian movement paths (journeys)
across different lighting zones, used to build transition matrices and calculate Markov
probabilities.
"""

journeys = [
    {
        "id": "P001",
        "path": [
            {"timestamp": "08:00", "zone": "A"},
            {"timestamp": "08:01", "zone": "B"},
            {"timestamp": "08:02", "zone": "D"},
        ],
    },
    {
        "id": "P002",
        "path": [
            {"timestamp": "08:00", "zone": "A"},
            {"timestamp": "08:01", "zone": "B"},
            {"timestamp": "08:02", "zone": "C"},
            {"timestamp": "08:03", "zone": "D"},
        ],
    },
    {
        "id": "P003",
        "path": [
            {"timestamp": "08:01", "zone": "A"},
            {"timestamp": "08:02", "zone": "B"},
            {"timestamp": "08:03", "zone": "A"},
        ],
    },
    {
        "id": "P004",
        "path": [
            {"timestamp": "08:01", "zone": "A"},
            {"timestamp": "08:02", "zone": "B"},
            {"timestamp": "08:03", "zone": "C"},
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "D"},
        ],
    },
    {
        "id": "P005",
        "path": [
            {"timestamp": "08:01", "zone": "A"},
            {"timestamp": "08:02", "zone": "B"},
            {"timestamp": "08:03", "zone": "C"},
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "D"},
        ],
    },
    {
        "id": "P006",
        "path": [
            {"timestamp": "08:01", "zone": "A"},
            {"timestamp": "08:02", "zone": "C"},
            {"timestamp": "08:03", "zone": "D"},
        ],
    },
    {
        "id": "P007",
        "path": [
            {"timestamp": "08:02", "zone": "A"},
            {"timestamp": "08:03", "zone": "B"},
            {"timestamp": "08:04", "zone": "D"},
        ],
    },
    {
        "id": "P008",
        "path": [
            {"timestamp": "08:02", "zone": "A"},
            {"timestamp": "08:03", "zone": "B"},
            {"timestamp": "08:04", "zone": "D"},
        ],
    },
    {
        "id": "P009",
        "path": [
            {"timestamp": "08:02", "zone": "B"},
            {"timestamp": "08:03", "zone": "C"},
            {"timestamp": "08:04", "zone": "D"},
        ],
    },
    {
        "id": "P010",
        "path": [
            {"timestamp": "08:02", "zone": "A"},
            {"timestamp": "08:03", "zone": "B"},
            {"timestamp": "08:04", "zone": "C"},
            {"timestamp": "08:05", "zone": "D"},
        ],
    },
    {
        "id": "P011",
        "path": [
            {"timestamp": "08:02", "zone": "A"},
            {"timestamp": "08:03", "zone": "B"},
            {"timestamp": "08:04", "zone": "C"},
            {"timestamp": "08:05", "zone": "D"},
        ],
    },
    {
        "id": "P012",
        "path": [
            {"timestamp": "08:03", "zone": "A"},
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "D"},
        ],
    },
    {
        "id": "P013",
        "path": [
            {"timestamp": "08:03", "zone": "A"},
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "C"},
            {"timestamp": "08:06", "zone": "B"},
            {"timestamp": "08:07", "zone": "D"},
        ],
    },
    {
        "id": "P014",
        "path": [
            {"timestamp": "08:03", "zone": "A"},
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "C"},
            {"timestamp": "08:06", "zone": "B"},
            {"timestamp": "08:07", "zone": "D"},
        ],
    },
    {
        "id": "P015",
        "path": [
            {"timestamp": "08:03", "zone": "A"},
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "C"},
            {"timestamp": "08:06", "zone": "D"},
        ],
    },
    {
        "id": "P016",
        "path": [
            {"timestamp": "08:04", "zone": "A"},
            {"timestamp": "08:05", "zone": "B"},
            {"timestamp": "08:06", "zone": "C"},
            {"timestamp": "08:07", "zone": "B"},
            {"timestamp": "08:08", "zone": "D"},
        ],
    },
    {
        "id": "P017",
        "path": [
            {"timestamp": "08:04", "zone": "B"},
            {"timestamp": "08:05", "zone": "C"},
            {"timestamp": "08:06", "zone": "D"},
        ],
    },
    {
        "id": "P018",
        "path": [
            {"timestamp": "08:04", "zone": "A"},
            {"timestamp": "08:05", "zone": "B"},
            {"timestamp": "08:06", "zone": "C"},
            {"timestamp": "08:07", "zone": "B"},
            {"timestamp": "08:08", "zone": "D"},
        ],
    },
    {
        "id": "P019",
        "path": [
            {"timestamp": "08:10", "zone": "C"},
            {"timestamp": "08:11", "zone": "D"},
        ],
    },
    {
        "id": "P020",
        "path": [
            {"timestamp": "08:10", "zone": "A"},
            {"timestamp": "08:11", "zone": "B"},
            {"timestamp": "08:12", "zone": "A"},
        ],
    },
    {
        "id": "P021",
        "path": [
            {"timestamp": "08:10", "zone": "A"},
            {"timestamp": "08:11", "zone": "B"},
            {"timestamp": "08:12", "zone": "C"},
            {"timestamp": "08:13", "zone": "D"},
        ],
    },
    {
        "id": "P022",
        "path": [
            {"timestamp": "08:10", "zone": "A"},
            {"timestamp": "08:11", "zone": "C"},
            {"timestamp": "08:12", "zone": "D"},
        ],
    },
    {
        "id": "P023",
        "path": [
            {"timestamp": "08:10", "zone": "B"},
            {"timestamp": "08:11", "zone": "C"},
            {"timestamp": "08:12", "zone": "D"},
        ],
    },
    {
        "id": "P024",
        "path": [
            {"timestamp": "08:10", "zone": "A"},
            {"timestamp": "08:11", "zone": "C"},
            {"timestamp": "08:12", "zone": "B"},
            {"timestamp": "08:13", "zone": "A"},
        ],
    },
    {
        "id": "P025",
        "path": [
            {"timestamp": "08:10", "zone": "A"},
            {"timestamp": "08:11", "zone": "B"},
            {"timestamp": "08:12", "zone": "A"},
        ],
    },
    {
        "id": "P026",
        "path": [
            {"timestamp": "08:10", "zone": "A"},
            {"timestamp": "08:11", "zone": "C"},
            {"timestamp": "08:12", "zone": "D"},
        ],
    },
    {
        "id": "P027",
        "path": [
            {"timestamp": "08:11", "zone": "A"},
            {"timestamp": "08:12", "zone": "B"},
            {"timestamp": "08:13", "zone": "C"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "D"},
        ],
    },
    {
        "id": "P028",
        "path": [
            {"timestamp": "08:11", "zone": "A"},
            {"timestamp": "08:12", "zone": "C"},
            {"timestamp": "08:13", "zone": "B"},
            {"timestamp": "08:14", "zone": "A"},
        ],
    },
    {
        "id": "P029",
        "path": [
            {"timestamp": "08:11", "zone": "A"},
            {"timestamp": "08:12", "zone": "B"},
            {"timestamp": "08:13", "zone": "D"},
        ],
    },
    {
        "id": "P030",
        "path": [
            {"timestamp": "08:11", "zone": "A"},
            {"timestamp": "08:12", "zone": "B"},
            {"timestamp": "08:13", "zone": "D"},
        ],
    },
    {
        "id": "P031",
        "path": [
            {"timestamp": "08:11", "zone": "B"},
            {"timestamp": "08:12", "zone": "C"},
            {"timestamp": "08:13", "zone": "D"},
        ],
    },
    {
        "id": "P032",
        "path": [
            {"timestamp": "08:11", "zone": "A"},
            {"timestamp": "08:12", "zone": "B"},
            {"timestamp": "08:13", "zone": "D"},
        ],
    },
    {
        "id": "P033",
        "path": [
            {"timestamp": "08:11", "zone": "A"},
            {"timestamp": "08:12", "zone": "C"},
            {"timestamp": "08:13", "zone": "B"},
            {"timestamp": "08:14", "zone": "A"},
        ],
    },
    {
        "id": "P034",
        "path": [
            {"timestamp": "08:12", "zone": "A"},
            {"timestamp": "08:13", "zone": "C"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "A"},
        ],
    },
    {
        "id": "P035",
        "path": [
            {"timestamp": "08:12", "zone": "A"},
            {"timestamp": "08:13", "zone": "B"},
            {"timestamp": "08:14", "zone": "A"},
        ],
    },
    {
        "id": "P036",
        "path": [
            {"timestamp": "08:12", "zone": "A"},
            {"timestamp": "08:13", "zone": "B"},
            {"timestamp": "08:14", "zone": "C"},
            {"timestamp": "08:15", "zone": "D"},
        ],
    },
    {
        "id": "P037",
        "path": [
            {"timestamp": "08:12", "zone": "C"},
            {"timestamp": "08:13", "zone": "D"},
        ],
    },
    {
        "id": "P038",
        "path": [
            {"timestamp": "08:12", "zone": "A"},
            {"timestamp": "08:13", "zone": "B"},
            {"timestamp": "08:14", "zone": "D"},
        ],
    },
    {
        "id": "P039",
        "path": [
            {"timestamp": "08:12", "zone": "B"},
            {"timestamp": "08:13", "zone": "C"},
            {"timestamp": "08:14", "zone": "D"},
        ],
    },
    {
        "id": "P040",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "D"},
        ],
    },
    {
        "id": "P041",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "A"},
        ],
    },
    {
        "id": "P042",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "C"},
            {"timestamp": "08:15", "zone": "B"},
            {"timestamp": "08:16", "zone": "A"},
        ],
    },
    {
        "id": "P043",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "C"},
            {"timestamp": "08:16", "zone": "B"},
            {"timestamp": "08:17", "zone": "D"},
        ],
    },
    {
        "id": "P044",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "D"},
        ],
    },
    {
        "id": "P045",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "C"},
            {"timestamp": "08:16", "zone": "D"},
        ],
    },
    {
        "id": "P046",
        "path": [
            {"timestamp": "08:13", "zone": "A"},
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "C"},
            {"timestamp": "08:16", "zone": "B"},
            {"timestamp": "08:17", "zone": "D"},
        ],
    },
    {
        "id": "P047",
        "path": [
            {"timestamp": "08:14", "zone": "A"},
            {"timestamp": "08:15", "zone": "B"},
            {"timestamp": "08:16", "zone": "A"},
        ],
    },
    {
        "id": "P048",
        "path": [
            {"timestamp": "08:14", "zone": "A"},
            {"timestamp": "08:15", "zone": "B"},
            {"timestamp": "08:16", "zone": "D"},
        ],
    },
    {
        "id": "P049",
        "path": [
            {"timestamp": "08:14", "zone": "A"},
            {"timestamp": "08:15", "zone": "B"},
            {"timestamp": "08:16", "zone": "C"},
            {"timestamp": "08:17", "zone": "B"},
            {"timestamp": "08:18", "zone": "D"},
        ],
    },
    {
        "id": "P050",
        "path": [
            {"timestamp": "08:14", "zone": "A"},
            {"timestamp": "08:15", "zone": "B"},
            {"timestamp": "08:16", "zone": "D"},
        ],
    },
    {
        "id": "P051",
        "path": [
            {"timestamp": "08:14", "zone": "B"},
            {"timestamp": "08:15", "zone": "C"},
            {"timestamp": "08:16", "zone": "D"},
        ],
    },
    {
        "id": "P052",
        "path": [
            {"timestamp": "08:25", "zone": "A"},
            {"timestamp": "08:26", "zone": "B"},
            {"timestamp": "08:27", "zone": "A"},
        ],
    },
    {
        "id": "P053",
        "path": [
            {"timestamp": "08:26", "zone": "C"},
            {"timestamp": "08:27", "zone": "D"},
        ],
    },
    {
        "id": "P054",
        "path": [
            {"timestamp": "08:45", "zone": "A"},
            {"timestamp": "08:46", "zone": "C"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "A"},
        ],
    },
    {
        "id": "P055",
        "path": [
            {"timestamp": "08:45", "zone": "A"},
            {"timestamp": "08:46", "zone": "C"},
            {"timestamp": "08:47", "zone": "D"},
        ],
    },
    {
        "id": "P056",
        "path": [
            {"timestamp": "08:45", "zone": "A"},
            {"timestamp": "08:46", "zone": "C"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "A"},
        ],
    },
    {
        "id": "P057",
        "path": [
            {"timestamp": "08:45", "zone": "A"},
            {"timestamp": "08:46", "zone": "C"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "A"},
        ],
    },
    {
        "id": "P058",
        "path": [
            {"timestamp": "08:45", "zone": "A"},
            {"timestamp": "08:46", "zone": "B"},
            {"timestamp": "08:47", "zone": "C"},
            {"timestamp": "08:48", "zone": "B"},
            {"timestamp": "08:49", "zone": "D"},
        ],
    },
    {
        "id": "P059",
        "path": [
            {"timestamp": "08:45", "zone": "A"},
            {"timestamp": "08:46", "zone": "B"},
            {"timestamp": "08:47", "zone": "A"},
        ],
    },
    {
        "id": "P060",
        "path": [
            {"timestamp": "08:46", "zone": "A"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "D"},
        ],
    },
    {
        "id": "P061",
        "path": [
            {"timestamp": "08:46", "zone": "A"},
            {"timestamp": "08:47", "zone": "C"},
            {"timestamp": "08:48", "zone": "D"},
        ],
    },
    {
        "id": "P062",
        "path": [
            {"timestamp": "08:46", "zone": "A"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "C"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "D"},
        ],
    },
    {
        "id": "P063",
        "path": [
            {"timestamp": "08:46", "zone": "A"},
            {"timestamp": "08:47", "zone": "C"},
            {"timestamp": "08:48", "zone": "D"},
        ],
    },
    {
        "id": "P064",
        "path": [
            {"timestamp": "08:46", "zone": "C"},
            {"timestamp": "08:47", "zone": "D"},
        ],
    },
    {
        "id": "P065",
        "path": [
            {"timestamp": "08:46", "zone": "B"},
            {"timestamp": "08:47", "zone": "C"},
            {"timestamp": "08:48", "zone": "D"},
        ],
    },
    {
        "id": "P066",
        "path": [
            {"timestamp": "08:46", "zone": "A"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "A"},
        ],
    },
    {
        "id": "P067",
        "path": [
            {"timestamp": "08:46", "zone": "A"},
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "C"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "D"},
        ],
    },
    {
        "id": "P068",
        "path": [
            {"timestamp": "08:47", "zone": "A"},
            {"timestamp": "08:48", "zone": "C"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "A"},
        ],
    },
    {
        "id": "P069",
        "path": [
            {"timestamp": "08:47", "zone": "A"},
            {"timestamp": "08:48", "zone": "B"},
            {"timestamp": "08:49", "zone": "C"},
            {"timestamp": "08:50", "zone": "D"},
        ],
    },
    {
        "id": "P070",
        "path": [
            {"timestamp": "08:47", "zone": "A"},
            {"timestamp": "08:48", "zone": "B"},
            {"timestamp": "08:49", "zone": "C"},
            {"timestamp": "08:50", "zone": "B"},
            {"timestamp": "08:51", "zone": "D"},
        ],
    },
    {
        "id": "P071",
        "path": [
            {"timestamp": "08:47", "zone": "A"},
            {"timestamp": "08:48", "zone": "B"},
            {"timestamp": "08:49", "zone": "C"},
            {"timestamp": "08:50", "zone": "D"},
        ],
    },
    {
        "id": "P072",
        "path": [
            {"timestamp": "08:47", "zone": "A"},
            {"timestamp": "08:48", "zone": "C"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "A"},
        ],
    },
    {
        "id": "P073",
        "path": [
            {"timestamp": "08:47", "zone": "B"},
            {"timestamp": "08:48", "zone": "C"},
            {"timestamp": "08:49", "zone": "D"},
        ],
    },
    {
        "id": "P074",
        "path": [
            {"timestamp": "08:47", "zone": "A"},
            {"timestamp": "08:48", "zone": "B"},
            {"timestamp": "08:49", "zone": "A"},
        ],
    },
    {
        "id": "P075",
        "path": [
            {"timestamp": "08:48", "zone": "A"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "D"},
        ],
    },
    {
        "id": "P076",
        "path": [
            {"timestamp": "08:48", "zone": "A"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "C"},
            {"timestamp": "08:51", "zone": "B"},
            {"timestamp": "08:52", "zone": "D"},
        ],
    },
    {
        "id": "P077",
        "path": [
            {"timestamp": "08:48", "zone": "A"},
            {"timestamp": "08:49", "zone": "C"},
            {"timestamp": "08:50", "zone": "B"},
            {"timestamp": "08:51", "zone": "A"},
        ],
    },
    {
        "id": "P078",
        "path": [
            {"timestamp": "08:48", "zone": "A"},
            {"timestamp": "08:49", "zone": "B"},
            {"timestamp": "08:50", "zone": "C"},
            {"timestamp": "08:51", "zone": "B"},
            {"timestamp": "08:52", "zone": "D"},
        ],
    },
    {
        "id": "P079",
        "path": [
            {"timestamp": "08:48", "zone": "C"},
            {"timestamp": "08:49", "zone": "D"},
        ],
    },
    {
        "id": "P080",
        "path": [
            {"timestamp": "08:48", "zone": "B"},
            {"timestamp": "08:49", "zone": "C"},
            {"timestamp": "08:50", "zone": "D"},
        ],
    },
]
