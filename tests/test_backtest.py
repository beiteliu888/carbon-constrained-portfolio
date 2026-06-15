import numpy as np
import pandas as pd

from carbon_portfolio.backtest import run_backtest


def synthetic_returns(rows=90):
    rng = np.random.default_rng(42)
    index = pd.bdate_range("2024-01-01", periods=rows)
    return pd.DataFrame(
        rng.normal(0.0003, 0.01, size=(rows, 4)),
        index=index,
        columns=["A", "B", "C", "D"],
    )


def test_backtest_outputs_three_comparable_portfolios():
    returns = synthetic_returns()
    carbon = pd.Series([10.0, 20.0, 60.0, 90.0], index=returns.columns)
    result = run_backtest(
        returns,
        carbon,
        lookback_days=20,
        rebalance_frequency="M",
        max_weight=0.5,
        carbon_budget_ratio=0.7,
    )
    assert list(result.portfolio_returns.columns) == [
        "equal_weight",
        "unconstrained_mv",
        "carbon_constrained_mv",
    ]
    assert not result.portfolio_returns.isna().any().any()


def test_estimation_window_ends_before_rebalance_return():
    returns = synthetic_returns()
    carbon = pd.Series([10.0, 20.0, 60.0, 90.0], index=returns.columns)
    result = run_backtest(
        returns,
        carbon,
        lookback_days=20,
        rebalance_frequency="M",
        max_weight=0.5,
        carbon_budget_ratio=0.7,
    )
    assert (result.diagnostics["estimation_end"] < result.diagnostics.index).all()
    assert (
        result.diagnostics["constrained_carbon"]
        <= result.diagnostics["carbon_budget"] + 1e-7
    ).all()
    assert {
        "equal_weight_turnover",
        "unconstrained_turnover",
        "constrained_turnover",
    }.issubset(result.diagnostics.columns)
    assert (
        result.diagnostics[
            [
                "equal_weight_turnover",
                "unconstrained_turnover",
                "constrained_turnover",
            ]
        ]
        >= 0
    ).all().all()


def test_panel_waits_for_disclosed_carbon_data():
    returns = synthetic_returns(rows=120)
    available_date = returns.index[45]
    panel = pd.DataFrame(
        {
            "ticker": returns.columns,
            "reporting_year": 2023,
            "available_date": available_date,
            "scope1_tco2e": [10.0, 20.0, 30.0, 40.0],
            "scope2_location_tco2e": [5.0, 5.0, 5.0, 5.0],
            "revenue_usd_mn": [1.0, 1.0, 1.0, 1.0],
            "carbon_intensity_tco2e_per_usd_mn": [
                15.0,
                25.0,
                35.0,
                45.0,
            ],
        }
    )
    result = run_backtest(
        returns,
        panel,
        lookback_days=20,
        rebalance_frequency="M",
        max_weight=0.5,
        carbon_budget_ratio=0.7,
    )
    assert result.portfolio_returns.index.min() >= available_date
    assert (
        result.diagnostics["constrained_carbon"]
        <= result.diagnostics["carbon_budget"] + 1e-7
    ).all()
