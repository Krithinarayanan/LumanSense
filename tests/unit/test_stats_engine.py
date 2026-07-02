from app.analytics.stats_engine import (
    build_transition_matrix,
    get_exponential_moving_averages,
    get_transition_matrix,
    predict_distribution_n_steps,
)


def test_transition_matrix():
    transition_data = build_transition_matrix()
    assert "nested_dict" in transition_data
    assert "string_keys" in transition_data

    prob_data = get_transition_matrix()
    assert "states" in prob_data
    assert "matrix" in prob_data
    assert len(prob_data["states"]) > 0


def test_predict_distribution_n_steps():
    # Predict distribution for 3 steps starting from state 'A'
    result = predict_distribution_n_steps("A", n_steps=3)
    assert isinstance(result, dict)
    assert len(result) > 0
    # Probabilities should sum close to 1
    total_prob = sum(result.values())
    assert abs(total_prob - 1.0) < 1e-5


def test_get_exponential_moving_averages():
    x_list = [10.0, 20.0, 30.0]
    alpha = 0.5
    ema = get_exponential_moving_averages(x_list, alpha)
    assert len(ema) == 3
    assert ema[0] == 10.0
    # ema[1] = 0.5 * 20.0 + 0.5 * 10.0 = 15.0
    assert ema[1] == 15.0
    # ema[2] = 0.5 * 30.0 + 0.5 * 15.0 = 22.5
    assert ema[2] == 22.5
