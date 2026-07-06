import asyncio

import pytest

from app.events.event_types import EventType
from app.events.trend_types import TrendType
from app.mcp.vision_service import classify_event


@pytest.mark.asyncio
async def test_classify_event():
    # High activity, delta > 5, trend increasing -> PEAK_FORMING
    assert (
        classify_event(pedestrians=60, trend=TrendType.INCREASING, ema=50.0)
        == EventType.PEAK_FORMING
    )
    # High activity, delta <= 5, trend increasing -> PEDESTRIAN_SPIKE
    assert (
        classify_event(pedestrians=60, trend=TrendType.STABLE, ema=50.0)
        == EventType.PEDESTRIAN_SPIKE
    )
    # Low activity, delta < -5, trend decreasing -> CLEARING
    assert (
        classify_event(pedestrians=10, trend=TrendType.DECREASING, ema=16.0)
        == EventType.CLEARING
    )
    # Low activity, delta >= -5 -> LOW_ACTIVITY
    assert (
        classify_event(pedestrians=10, trend=TrendType.STABLE, ema=12.0)
        == EventType.LOW_ACTIVITY
    )
    # Normal activity -> NORMAL_ACTIVITY
    assert (
        classify_event(pedestrians=30, trend=TrendType.STABLE, ema=30.0)
        == EventType.NORMAL_ACTIVITY
    )


@pytest.mark.asyncio
async def test_carbon_scaling_decision():
    from app.events.event import DetectionEvent
    from app.agent.controller_agent import _compute_brightness_and_decision
    from datetime import datetime

    # Mock detection event (NORMAL_ACTIVITY -> reactive brightness is 60%)
    event = DetectionEvent(
        eventid=1,
        event_type=EventType.NORMAL_ACTIVITY,
        pedestrians=30,
        timestamp=datetime.now(),
        ema=30.0,
        trend="STABLE",
        delta=0.0,
        flag=True,
        zone="A"
    )
    # Mock zone plan (brightness is 90% if expected, probability is 0.5)
    zone_plan = {"brightness": 90, "prob dist": 0.5}

    # Test 1: Clean Grid (100 gCO2eq/kWh) -> c_scale = 1.0
    # blended = 0.5 * 90 + 0.5 * 60 = 75
    # target = 75 * 1.0 = 75
    brightness, decision = _compute_brightness_and_decision(event, zone_plan, carbon_intensity=100.0)
    assert brightness == 75.0
    assert decision.carbon_intensity == 100.0
    assert decision.co2_saved_grams > 0.0

    # Test 2: Dirty Grid (550 gCO2eq/kWh) -> c_scale = 1.0 - (550-150)/2000 = 0.8
    # target = 75 * 0.8 = 60
    brightness_dirty, decision_dirty = _compute_brightness_and_decision(event, zone_plan, carbon_intensity=550.0)
    assert brightness_dirty == 60.0
    assert decision_dirty.carbon_intensity == 550.0

    # Test 3: Safety Floor enforcement under high carbon intensity (1000 gCO2eq/kWh)
    # NORMAL_ACTIVITY (pedestrians active) -> safety floor is 30%
    # If we force a low blended brightness: plan = 30%, prob dist = 1.0 -> blended = 30%
    # With carbon intensity = 1000, c_scale = 1.0 - (1000-150)/2000 = 0.575 -> capped at 0.8
    # target = 30 * 0.8 = 24.
    # Final brightness should be max(24, 30) = 30.
    low_zone_plan = {"brightness": 30, "prob dist": 1.0}
    brightness_clamped, decision_clamped = _compute_brightness_and_decision(event, low_zone_plan, carbon_intensity=1000.0)
    assert brightness_clamped == 30.0  # Clamped to safetyfloor of active zone


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_classify_event())
    asyncio.run(test_carbon_scaling_decision())
