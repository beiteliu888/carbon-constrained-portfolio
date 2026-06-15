"""教学 prototype 使用的简单图表函数。"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import drawdown_series, wealth_index


def plot_cumulative_returns(portfolio_returns: pd.DataFrame):
    """绘制三种组合从 1 开始的累计价值。"""
    ax = wealth_index(portfolio_returns).plot(figsize=(10, 5))
    ax.set(title="Growth of 1 (exploratory backtest)", ylabel="Portfolio value")
    ax.grid(alpha=0.3)
    return ax


def plot_drawdowns(portfolio_returns: pd.DataFrame):
    """绘制三种组合的历史回撤。"""
    ax = drawdown_series(portfolio_returns).plot(figsize=(10, 5))
    ax.set(title="Historical drawdowns", ylabel="Drawdown")
    ax.grid(alpha=0.3)
    return ax


def plot_latest_weights(weights: dict[str, pd.DataFrame]):
    """绘制最后一次调仓的目标权重。"""
    latest = pd.DataFrame({name: frame.iloc[-1] for name, frame in weights.items()})
    ax = latest.plot.bar(figsize=(11, 5))
    ax.set(title="Latest rebalance weights", ylabel="Weight")
    ax.legend(title="Portfolio")
    plt.xticks(rotation=45)
    return ax


def plot_average_weights(weights: dict[str, pd.DataFrame]):
    """绘制各次调仓目标权重的时间平均值。"""
    averages = pd.DataFrame(
        {name: frame.mean(axis=0) for name, frame in weights.items()}
    )
    ax = averages.plot.bar(figsize=(12, 5))
    ax.set(title="Average target portfolio weights", ylabel="Average weight")
    ax.legend(title="Portfolio")
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45)
    return ax


def plot_carbon_exposure_comparison(diagnostics: pd.DataFrame):
    """比较三种组合在调仓日的平均加权碳强度。"""
    columns = {
        "equal_weight_carbon": "Equal weight",
        "unconstrained_carbon": "Unconstrained MV",
        "constrained_carbon": "Carbon-constrained MV",
    }
    average_exposure = diagnostics[list(columns)].mean().rename(index=columns)
    ax = average_exposure.plot.bar(
        figsize=(8, 5), color=["#4C78A8", "#F58518", "#54A24B"]
    )
    ax.set(
        title="Average disclosed carbon intensity",
        ylabel="tCO2e per USD million revenue",
    )
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=20)
    return ax
