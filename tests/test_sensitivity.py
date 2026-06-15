import numpy as np
import pandas as pd

from carbon_portfolio.sensitivity import run_sensitivity_analysis


def test_sensitivity_returns_every_scenario_and_strategy():
    rng = np.random.default_rng(7)
    returns = pd.DataFrame(
        rng.normal(0.0002, 0.01, size=(70, 4)),
        index=pd.bdate_range("2024-01-01", periods=70),
        columns=["A", "B", "C", "D"],
    )
    carbon = pd.Series([10.0, 20.0, 60.0, 90.0], index=returns.columns)
    result = run_sensitivity_analysis(
        returns,
        carbon,
        carbon_budget_ratios=[0.7, 1.0],
        risk_aversion_values=[5.0],
        lookback_days=20,
        rebalance_frequency="M",
        max_weight=0.5,
    )
    assert len(result) == 6
    assert set(result["strategy"]) == {
        "equal_weight",
        "unconstrained_mv",
        "carbon_constrained_mv",
    }
