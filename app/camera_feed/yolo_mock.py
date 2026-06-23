"""YOLO mock producer module.

This module simulates a real-time vision sensor feed by publishing mock pedestrian detections.
"""

import asyncio

from app.camera_feed.scenario import scenarios
from app.mcp.vision_service import process_detection


async def yolo_mock_producer():
    """Loops through mock detection scenarios and publishes events to Vision MCP.

    This mock simulates real-time pedestrian counting per zone by processing
    sequential detection frames and feeding them into the vision service.
    """
    for index, block in enumerate(scenarios):
        for detection in block:
            await process_detection(
                eventid=index,
                zone=detection["zone"],
                pedestrians=detection["pedestrians"],
            )
            await asyncio.sleep(2)
        await asyncio.sleep(3)
    await process_detection(eventid=0, zone=None, pedestrians=0)
