"""对关键模型假设进行透明的敏感性分析。"""

from __future__ import annotations

from itertools import product

import pandas as pd

from .backtest import run_backtest
from .metrics import performance_summary, turnover


def run_sensitivity_analysis(
    returns: pd.DataFrame,
    carbon_scores: pd.Series | pd.DataFrame,
    carbon_budget_ratios: list[float],
    risk_aversion_values: list[float],
    **backtest_kwargs,
) -> pd.DataFrame:
    """运行完整参数网格，不根据历史表现挑选所谓“最佳”参数。"""
    rows: list[dict[str, float | str]] = []
    for budget_ratio, risk_aversion in product(
        carbon_budget_ratios, risk_aversion_values
    ):
        result = run_backtest(
            returns,
            carbon_scores,
            carbon_budget_ratio=budget_ratio,
            risk_aversion=risk_aversion,
            **backtest_kwargs,
        )
        summary = performance_summary(result.portfolio_returns)
        carbon_columns = {
            "equal_weight": "equal_weight_carbon",
            "unconstrained_mv": "unconstrained_carbon",
            "carbon_constrained_mv": "constrained_carbon",
        }
        for strategy, metrics in summary.iterrows():
            rows.append(
                {
                    "carbon_budget_ratio": budget_ratio,
                    "risk_aversion": risk_aversion,
                    "strategy": strategy,
                    **metrics.to_dict(),
                    "average_turnover": float(
                        turnover(result.rebalance_weights[strategy]).mean()
                    ),
                    "average_carbon_exposure": float(
                        result.diagnostics[carbon_columns[strategy]].mean()
                    ),
                }
            )
    return pd.DataFrame(rows)
