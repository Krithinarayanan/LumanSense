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
    # blended = max(60, 0.5 * 90) = max(60, 45) = 60
    # target = 60 * 1.0 = 60
    brightness, decision = _compute_brightness_and_decision(event, zone_plan, carbon_intensity=100.0)
    assert brightness == 60.0
    assert decision.carbon_intensity == 100.0
    assert decision.co2_saved_grams > 0.0

    # Test 2: Dirty Grid (550 gCO2eq/kWh) -> c_scale = 0.8
    # target = 60 * 0.8 = 48
    brightness_dirty, decision_dirty = _compute_brightness_and_decision(event, zone_plan, carbon_intensity=550.0)
    assert brightness_dirty == 48.0
    assert decision_dirty.carbon_intensity == 550.0

    # Test 3: Safety Floor enforcement under high carbon intensity (1000 gCO2eq/kWh)
    # NORMAL_ACTIVITY (pedestrians active) -> safety floor is 30%
    # With carbon intensity = 1000, c_scale = 0.8
    # If we force a low blended brightness: plan = 30%, prob dist = 1.0 -> blended = max(60, 30) = 60 -> target = 48 -> remains 48
    # If we force a low reactive brightness by using a LOW_ACTIVITY event (reactive is 30%):
    # blended = max(30, 0.0 * 30) = 30.
    # target = 30 * 0.8 = 24. Low activity safety floor is 15 -> remains 24.
    low_event = DetectionEvent(
        eventid=2,
        event_type=EventType.LOW_ACTIVITY,
        pedestrians=5,
        timestamp=datetime.now(),
        ema=5.0,
        trend="STABLE",
        delta=0.0,
        flag=True,
        zone="A"
    )
    low_zone_plan = {"brightness": 10, "prob dist": 1.0} # blended = max(30, 10) = 30.
    # target = 30 * 0.8 = 24 -> 24 is above safety floor of 15.
    brightness_low, decision_low = _compute_brightness_and_decision(low_event, low_zone_plan, carbon_intensity=550.0)
    assert brightness_low == 24.0

    # Test 4: Pre-warming brightness check (reactive is 30%, predictive is 90%, prob dist = 0.6)
    # blended = max(30, 0.6 * 90) = max(30, 54) = 54
    prewarm_zone_plan = {"brightness": 90, "prob dist": 0.6}
    brightness_prewarm, decision_prewarm = _compute_brightness_and_decision(low_event, prewarm_zone_plan, carbon_intensity=100.0)
    assert brightness_prewarm == 54.0


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_classify_event())
    asyncio.run(test_carbon_scaling_decision())
