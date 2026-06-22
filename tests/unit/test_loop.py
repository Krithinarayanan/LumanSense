import asyncio

import pytest

from app.events.event_types import EventType
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
    assert classify_event("A", 8) == EventType.PEDESTRIAN_SPIKE


if __name__ == "__main__":
    asyncio.run(test_classify_event())
