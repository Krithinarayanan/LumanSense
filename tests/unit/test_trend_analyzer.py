from app.mcp.trend_analyzer import get_traffic_trends


def test_get_traffic_trends():
    trends = get_traffic_trends()
    assert isinstance(trends, list)
    assert len(trends) > 0

    # Verify that the keys and format match the requirements
    for entry in trends:
        assert "timestamp" in entry
        assert "zone" in entry
        assert "count" in entry
        assert isinstance(entry["count"], int)

    # Spot check specific values from training_data.py
    # e.g., P001 and P002 both start at 08:00 in zone A
    # Let's find the entry for 08:00, zone A
    entry_0800_A = next(
        (e for e in trends if e["timestamp"] == "08:00" and e["zone"] == "A"), None
    )
    assert entry_0800_A is not None
    assert entry_0800_A["count"] >= 2
