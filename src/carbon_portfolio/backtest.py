"""避免明显 look-ahead bias 的简化滚动回测。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .carbon import (
    carbon_scores_as_of,
    carbon_snapshot_as_of,
    portfolio_carbon_exposure,
)
from .optimization import equal_weights, optimize_mean_variance


@dataclass(frozen=True)
class BacktestResult:
    portfolio_returns: pd.DataFrame
    rebalance_weights: dict[str, pd.DataFrame]
    diagnostics: pd.DataFrame


def _rebalance_positions(index: pd.DatetimeIndex, start_position: int, frequency: str) -> set[int]:
    """返回每个调仓月份的第一个可交易日位置。"""
    eligible = pd.Series(range(start_position, len(index)), index=index[start_position:])
    positions = eligible.groupby(index[start_position:].to_period(frequency)).first()
    return set(positions.astype(int))


def run_backtest(
    returns: pd.DataFrame,
    carbon_scores: pd.Series | pd.DataFrame,
    lookback_days: int = 252,
    rebalance_frequency: str = "M",
    annualization_factor: int = 252,
    risk_aversion: float = 5.0,
    max_weight: float = 0.35,
    carbon_budget_ratio: float = 0.70,
    covariance_ridge: float = 1e-6,
    transaction_cost_bps: float = 0.0,
) -> BacktestResult:
    """比较 equal-weight、无碳约束 MV 和碳约束 MV。

    日期 i 的参数只使用 returns[i-lookback_days:i]，不包含日期 i 的收益。
    两次月度调仓之间，权重会随各资产收益自然漂移。
    """
    if not isinstance(returns.index, pd.DatetimeIndex):
        raise TypeError("returns must use a DatetimeIndex.")
    if lookback_days < 2 or len(returns) <= lookback_days:
        raise ValueError("Not enough observations for the requested lookback.")
    if not 0 < carbon_budget_ratio <= 1:
        raise ValueError("carbon_budget_ratio must be in (0, 1].")
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps cannot be negative.")
    if returns.isna().any().any():
        raise ValueError("Backtest returns must not contain missing values.")

    returns = returns.sort_index()
    assets = list(returns.columns)
    rebalance_at = _rebalance_positions(
        returns.index, lookback_days, rebalance_frequency
    )
    strategy_names = ["equal_weight", "unconstrained_mv", "carbon_constrained_mv"]
    current: dict[str, pd.Series] = {}
    realized: list[dict[str, float]] = []
    weight_history: dict[str, list[pd.Series]] = {name: [] for name in strategy_names}
    diagnostic_rows: list[dict[str, object]] = []
    cost_rate = transaction_cost_bps / 10_000

    for i in range(lookback_days, len(returns)):
        date = returns.index[i]
        trading_costs = {name: 0.0 for name in strategy_names}
        if i in rebalance_at:
            try:
                scores = carbon_scores_as_of(carbon_scores, date, assets)
            except ValueError:
                # 真实披露面板可能在样本初期尚未覆盖全部股票。
                # 在首次可构建完整组合前跳过，不用未来数据回填历史。
                if not current and isinstance(carbon_scores, pd.DataFrame):
                    continue
                raise

            estimation = returns.iloc[i - lookback_days : i]
            expected = estimation.mean() * annualization_factor
            covariance = estimation.cov() * annualization_factor
            equal = equal_weights(assets)
            budget = portfolio_carbon_exposure(equal, scores) * carbon_budget_ratio

            new_weights = {
                "equal_weight": equal,
                "unconstrained_mv": optimize_mean_variance(
                    expected,
                    covariance,
                    risk_aversion=risk_aversion,
                    max_weight=max_weight,
                    covariance_ridge=covariance_ridge,
                ).weights,
                "carbon_constrained_mv": optimize_mean_variance(
                    expected,
                    covariance,
                    risk_aversion=risk_aversion,
                    max_weight=max_weight,
                    carbon_scores=scores,
                    carbon_budget=budget,
                    covariance_ridge=covariance_ridge,
                ).weights,
            }
            rebalance_turnover: dict[str, float] = {}
            for name, weights in new_weights.items():
                if name in current:
                    rebalance_turnover[name] = 0.5 * float(
                        (weights - current[name]).abs().sum()
                    )
                    trading_costs[name] = rebalance_turnover[name] * cost_rate
                else:
                    # 初始建仓不计入平均换手率，避免与后续再平衡混淆。
                    rebalance_turnover[name] = 0.0
                current[name] = weights
                recorded = weights.copy()
                recorded.name = date
                weight_history[name].append(recorded)

            diagnostic_row: dict[str, object] = {
                "date": date,
                "estimation_start": estimation.index[0],
                "estimation_end": estimation.index[-1],
                "carbon_budget": budget,
                "equal_weight_carbon": portfolio_carbon_exposure(equal, scores),
                "unconstrained_carbon": portfolio_carbon_exposure(
                    new_weights["unconstrained_mv"], scores
                ),
                "constrained_carbon": portfolio_carbon_exposure(
                    new_weights["carbon_constrained_mv"], scores
                ),
                "equal_weight_turnover": rebalance_turnover["equal_weight"],
                "unconstrained_turnover": rebalance_turnover["unconstrained_mv"],
                "constrained_turnover": rebalance_turnover[
                    "carbon_constrained_mv"
                ],
            }
            if isinstance(carbon_scores, pd.DataFrame):
                snapshot = carbon_snapshot_as_of(carbon_scores, date, assets)
                diagnostic_row["carbon_reporting_year_min"] = int(
                    snapshot["reporting_year"].min()
                )
                diagnostic_row["carbon_reporting_year_max"] = int(
                    snapshot["reporting_year"].max()
                )
            diagnostic_rows.append(diagnostic_row)

        if not current:
            continue

        day_return = returns.iloc[i]
        realized_row: dict[str, float | pd.Timestamp] = {"date": date}
        for name in strategy_names:
            gross_return = float(current[name] @ day_return)
            realized_row[name] = gross_return - trading_costs[name]

            # 收盘后资产价值变化，下一交易日前的权重自然漂移。
            gross_growth = 1.0 + gross_return
            if gross_growth <= 0:
                raise ValueError("组合单日总价值变为非正，无法更新漂移权重。")
            current[name] = current[name] * (1.0 + day_return) / gross_growth

        realized.append(realized_row)

    if not realized:
        raise ValueError(
            "No backtest period has complete point-in-time carbon data."
        )
    portfolio_returns = pd.DataFrame(realized).set_index("date")
    weights = {
        name: pd.DataFrame(rows) for name, rows in weight_history.items()
    }
    diagnostics = pd.DataFrame(diagnostic_rows).set_index("date")
    return BacktestResult(portfolio_returns, weights, diagnostics)
