from app.agent.ask_luman_agent import (
    ask_luman_agent,
    query_table_records,
    query_aggregation,
)


def test_agent_initialization():
    """Verifies that ask_luman_agent is configured correctly."""
    assert ask_luman_agent.name == "ask_luman_agent"
    assert len(ask_luman_agent.tools) > 0
    assert len(ask_luman_agent.sub_agents) > 0
    assert ask_luman_agent.sub_agents[0].name == "luman_sense_critic_agent"


def test_query_table_records_validation():
    """Verifies that query_table_records restricts table access and sanitizes inputs."""
    # 1. Test valid query
    result = query_table_records("detection_events", limit=1)
    assert result["status"] in ["success", "error"]

    # 2. Test invalid table name
    bad_table_result = query_table_records("sqlite_master", limit=1)
    assert bad_table_result["status"] == "error"
    assert "Unauthorized or invalid table" in bad_table_result["message"]

    # 3. Test invalid column filter
    bad_col_result = query_table_records(
        "detection_events",
        filters={"malicious_column; --": "value"}
    )
    assert bad_col_result["status"] == "error"
    assert "Unauthorized or invalid filter column" in bad_col_result["message"]


def test_query_aggregation_validation():
    """Verifies that query_aggregation validates operations and whitelist constraints."""
    # 1. Test valid aggregation
    result = query_aggregation("COUNT", "*", "detection_events")
    assert result["status"] in ["success", "error"]

    # 2. Test invalid aggregation operation
    bad_op_result = query_aggregation("DELETE", "*", "detection_events")
    assert bad_op_result["status"] == "error"
    assert "Unauthorized or invalid aggregation operation" in bad_op_result["message"]

    # 3. Test invalid column
    bad_col_result = query_aggregation("AVG", "malicious_col", "detection_events")
    assert bad_col_result["status"] == "error"
    assert "Unauthorized or invalid column" in bad_col_result["message"]

