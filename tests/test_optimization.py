import numpy as np
import pandas as pd
import pytest

from carbon_portfolio.optimization import (
    OptimizationError,
    equal_weights,
    optimize_mean_variance,
)


def sample_inputs():
    assets = ["A", "B", "C", "D"]
    expected = pd.Series([0.08, 0.10, 0.07, 0.12], index=assets)
    covariance = pd.DataFrame(
        np.diag([0.04, 0.05, 0.03, 0.08]), index=assets, columns=assets
    )
    carbon = pd.Series([10.0, 30.0, 60.0, 90.0], index=assets)
    return expected, covariance, carbon


def test_equal_weights_are_fully_invested():
    weights = equal_weights(["A", "B", "C", "D"])
    assert weights.sum() == pytest.approx(1.0)
    assert (weights == 0.25).all()


def test_unconstrained_solution_respects_bounds():
    expected, covariance, _ = sample_inputs()
    result = optimize_mean_variance(
        expected, covariance, risk_aversion=5.0, max_weight=0.4
    )
    assert result.weights.sum() == pytest.approx(1.0, abs=1e-7)
    assert (result.weights >= -1e-8).all()
    assert (result.weights <= 0.4 + 1e-8).all()


def test_carbon_constrained_solution_respects_budget():
    expected, covariance, carbon = sample_inputs()
    result = optimize_mean_variance(
        expected,
        covariance,
        risk_aversion=5.0,
        max_weight=0.5,
        carbon_scores=carbon,
        carbon_budget=35.0,
    )
    assert float(result.weights @ carbon) <= 35.0 + 1e-7


def test_infeasible_carbon_budget_is_explicit():
    expected, covariance, carbon = sample_inputs()
    with pytest.raises(OptimizationError, match="infeasible"):
        optimize_mean_variance(
            expected,
            covariance,
            max_weight=0.5,
            carbon_scores=carbon,
            carbon_budget=5.0,
        )


def test_carbon_constraint_is_invariant_to_score_units():
    """碳强度换单位后，等价约束不应改变优化权重。"""
    assets = ["A", "B", "C", "D"]
    expected = pd.Series([0.08, 0.07, 0.06, 0.05], index=assets)
    covariance = pd.DataFrame(np.eye(4) * 0.04, index=assets, columns=assets)
    scores = pd.Series([2.0, 8.0, 30.0, 800.0], index=assets)
    budget = 20.0

    original = optimize_mean_variance(
        expected,
        covariance,
        risk_aversion=5.0,
        max_weight=0.5,
        carbon_scores=scores,
        carbon_budget=budget,
    )
    rescaled = optimize_mean_variance(
        expected,
        covariance,
        risk_aversion=5.0,
        max_weight=0.5,
        carbon_scores=scores * 1_000,
        carbon_budget=budget * 1_000,
    )

    assert np.allclose(original.weights, rescaled.weights, atol=1e-6)
