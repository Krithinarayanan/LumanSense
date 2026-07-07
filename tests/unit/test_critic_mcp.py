"""Unit tests for the critic MCP server functions."""

import pytest
import uuid
from app.mcp.critic_mcp import get_energy_statistics
from app.mcp.database_mcp import save_decision_event, setup_database


@pytest.fixture(autouse=True)
def init_db():
    """Initializes the database tables before running each test."""
    setup_database()


def test_get_energy_statistics_empty_zone():
    """Verifies that get_energy_statistics returns default structure for non-existent zone."""
    unique_zone = f"test-zone-{uuid.uuid4()}"
    stats = get_energy_statistics(unique_zone)
    assert stats["zone"] == unique_zone
    assert stats["total_energy_saved_watts"] == 0
    assert stats["average_brightness_percent"] == 0.0
    assert stats["total_decisions"] == 0
    assert stats["average_energy_saved_watts"] == 0.0
    assert stats["max_energy_saved_watts"] == 0
    assert stats["average_pred_brightness"] == 0.0
    assert stats["average_reactive_brightness"] == 0.0


def test_get_energy_statistics_populated_zone():
    """Verifies that get_energy_statistics computes correct statistics for a zone."""
    unique_zone = f"test-zone-{uuid.uuid4()}"

    # Save mock decision events for this zone
    event1 = {
        "timestamp": "2026-07-04T12:00:00Z",
        "zone": unique_zone,
        "state": "NORMAL_ACTIVITY",
        "brightness_plan": 50,
        "reactive_brightness": 60,
        "brightness_to_lamp": 55,
        "energy_saved_watts": 35,
        "reason": "Test reason 1",
    }

    event2 = {
        "timestamp": "2026-07-04T12:01:00Z",
        "zone": unique_zone,
        "state": "LOW_ACTIVITY",
        "brightness_plan": 30,
        "reactive_brightness": 40,
        "brightness_to_lamp": 35,
        "energy_saved_watts": 55,
        "reason": "Test reason 2",
    }

    save_decision_event(event1)
    save_decision_event(event2)

    stats = get_energy_statistics(unique_zone)

    assert stats["zone"] == unique_zone
    assert stats["total_energy_saved_watts"] == 90  # 35 + 55
    assert stats["average_brightness_percent"] == 45.0  # (55 + 35) / 2
    assert stats["total_decisions"] == 2
    assert stats["average_energy_saved_watts"] == 45.0  # (35 + 55) / 2
    assert stats["max_energy_saved_watts"] == 55
    assert stats["average_pred_brightness"] == 40.0  # (50 + 30) / 2
    assert stats["average_reactive_brightness"] == 50.0  # (60 + 40) / 2
