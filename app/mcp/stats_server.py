"""Statistics MCP tool server wrapper.

This module exposes the Stats tool server using FastMCP, wrapping business logic
defined in the app/analytics/stats_engine module.
"""

from mcp.server.fastmcp import FastMCP

from app.analytics.stats_engine import (
    get_exponential_moving_averages as _get_exponential_moving_averages,
)
from app.analytics.stats_engine import (
    get_five_point_summary as _get_five_point_summary,
)
from app.analytics.stats_engine import (
    predict_distribution_n_steps,
)

mcp = FastMCP("Stats")


@mcp.tool()
def predict_distribution(zone: str, steps: int):
    """Predicts the state probability distribution after n steps.

    Args:
        zone: The current zone/state name.
        steps: The number of transition steps to predict.
    """
    return predict_distribution_n_steps(current_state=zone, n_steps=steps)


@mcp.tool()
def get_exponential_moving_averages(x_list: list[float], alpha: float) -> list[float]:
    """Computes the exponential moving average of a list of numbers."""
    return _get_exponential_moving_averages(x_list, alpha)


@mcp.tool()
def get_five_point_summary(x_list: list):
    """Computes the five point summary of a list of numbers."""
    return _get_five_point_summary(x_list)


if __name__ == "__main__":
    mcp.run()
