"""Unit test for the ask_luman_agent."""

from app.agent.ask_luman_agent import ask_luman_agent, query_database


def test_agent_initialization():
    """Verifies that ask_luman_agent is configured correctly."""
    assert ask_luman_agent.name == "ask_luman_agent"
    assert len(ask_luman_agent.tools) > 0
    assert len(ask_luman_agent.sub_agents) > 0
    assert ask_luman_agent.sub_agents[0].name == "luman_sense_critic_agent"


def test_query_database_validation():
    """Verifies that query_database tool only allows read-only SELECT queries."""
    # Test valid query
    result = query_database("SELECT * FROM detection_events LIMIT 1")
    # Result status should be success or a connection error (but not query type error)
    assert result["status"] in ["success", "error"]
    if result["status"] == "error":
        assert "Only read-only SELECT queries" not in result["message"]

    # Test invalid query (modification attempts)
    bad_result = query_database("DELETE FROM detection_events")
    assert bad_result["status"] == "error"
    assert "Only read-only SELECT queries are allowed" in bad_result["message"]

    bad_result2 = query_database("DROP TABLE detection_events")
    assert bad_result2["status"] == "error"
    assert "Only read-only SELECT queries are allowed" in bad_result2["message"]
