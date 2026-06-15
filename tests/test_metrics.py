import numpy as np
import pandas as pd
import pytest

from carbon_portfolio.metrics import max_drawdown, turnover, wealth_index


def test_wealth_index_compounds_returns():
    returns = pd.Series([0.10, -0.05])
    assert wealth_index(returns).iloc[-1] == pytest.approx(1.045)


def test_max_drawdown_uses_previous_peak():
    returns = pd.Series([0.10, -0.20, 0.05])
    assert max_drawdown(returns) == pytest.approx(-0.20)


def test_turnover_is_half_absolute_weight_change():
    weights = pd.DataFrame(
        [[0.5, 0.5], [0.7, 0.3]],
        index=pd.to_datetime(["2024-01-01", "2024-02-01"]),
        columns=["A", "B"],
    )
    result = turnover(weights)
    assert result.iloc[0] == 0.0
    assert result.iloc[1] == pytest.approx(0.2)
    assert np.isfinite(result).all()
