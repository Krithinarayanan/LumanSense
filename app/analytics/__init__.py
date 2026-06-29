"""Analytics package.

This package contains pure Python analytics engines and transition statistics logic.
"""

from .stats_engine import (
    predict_distribution_n_steps as predict_distribution_n_steps,
    predict_distribution as predict_distribution,
    get_exponential_moving_averages as get_exponential_moving_averages,
    get_five_point_summary as get_five_point_summary,
)
