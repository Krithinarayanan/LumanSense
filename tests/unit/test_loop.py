import asyncio

import pytest

from app.events.event_types import EventType
from app.events.trend_types import TrendType
from app.mcp.vision_service import classify_event


# Create a mock agent that captures tool calls
class MockAgent:
    async def call_tool(self, server, tool, args):
        print(f"DEBUG: Called {tool} on {server} with {args}")
        if tool == "get_traffic_state":
            return {
                "pedestrians": 10,
                "vehicles": 15,
            }  # Force a 'high traffic' scenario
        return "Success"


@pytest.mark.asyncio
async def test_classify_event():
    # High activity, delta > 5, trend increasing -> PEAK_FORMING
    assert classify_event(pedestrians=60, trend=TrendType.INCREASING, ema=50.0) == EventType.PEAK_FORMING
    # High activity, delta <= 5, trend increasing -> PEDESTRIAN_SPIKE
    assert classify_event(pedestrians=60, trend=TrendType.STABLE, ema=50.0) == EventType.PEDESTRIAN_SPIKE
    # Low activity, delta < -5, trend decreasing -> CLEARING
    assert classify_event(pedestrians=10, trend=TrendType.DECREASING, ema=16.0) == EventType.CLEARING
    # Low activity, delta >= -5 -> LOW_ACTIVITY
    assert classify_event(pedestrians=10, trend=TrendType.STABLE, ema=12.0) == EventType.LOW_ACTIVITY
    # Normal activity -> NORMAL_ACTIVITY
    assert classify_event(pedestrians=30, trend=TrendType.STABLE, ema=30.0) == EventType.NORMAL_ACTIVITY


if __name__ == "__main__":
    asyncio.run(test_classify_event())
