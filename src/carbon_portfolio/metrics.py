"""简化回测使用的绩效与组合诊断指标。"""

from __future__ import annotations

import numpy as np
import pandas as pd


def wealth_index(returns: pd.Series | pd.DataFrame, initial_value: float = 1.0):
    """把收益率复合为从 initial_value 开始的累计价值。"""
    return initial_value * (1.0 + returns).cumprod()


def drawdown_series(returns: pd.Series | pd.DataFrame):
    """计算累计价值相对历史高点的回撤。"""
    wealth = wealth_index(returns)
    return wealth / wealth.cummax() - 1.0


def max_drawdown(returns: pd.Series) -> float:
    """返回样本内最大回撤。"""
    return float(drawdown_series(returns).min())


def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    """按复合增长计算历史年化收益率。"""
    if returns.empty:
        return float("nan")
    ending_wealth = float((1.0 + returns).prod())
    if ending_wealth <= 0:
        return float("nan")
    return ending_wealth ** (periods_per_year / len(returns)) - 1.0


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """用日收益标准差乘以 sqrt(252) 计算年化波动率。"""
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """计算简化 Sharpe ratio；默认无风险利率为零。"""
    volatility = annualized_volatility(returns, periods_per_year)
    if volatility == 0 or np.isnan(volatility):
        return float("nan")
    return (annualized_return(returns, periods_per_year) - risk_free_rate) / volatility


def turnover(weights: pd.DataFrame) -> pd.Series:
    """目标权重变化的一半绝对值之和，是简化 turnover 指标。"""
    if weights.empty:
        return pd.Series(dtype=float, name="turnover")
    result = 0.5 * weights.diff().abs().sum(axis=1)
    result.iloc[0] = 0.0
    result.name = "turnover"
    return result


def concentration_hhi(weights: pd.DataFrame) -> pd.Series:
    """计算权重平方和，数值越高表示越集中。"""
    result = weights.pow(2).sum(axis=1)
    result.name = "weight_hhi"
    return result


def performance_summary(
    portfolio_returns: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    """为每个组合汇总核心历史绩效指标。"""
    rows = {}
    for name in portfolio_returns:
        series = portfolio_returns[name].dropna()
        rows[name] = {
            "annualized_return": annualized_return(series, periods_per_year),
            "annualized_volatility": annualized_volatility(series, periods_per_year),
            "sharpe_ratio": sharpe_ratio(series, risk_free_rate, periods_per_year),
            "max_drawdown": max_drawdown(series),
            "observations": len(series),
        }
    return pd.DataFrame.from_dict(rows, orient="index")
