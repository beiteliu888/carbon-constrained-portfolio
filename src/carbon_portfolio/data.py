"""市场数据下载、模拟 fallback 与收益率计算。"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


def download_adjusted_close(
    tickers: Sequence[str],
    start: str,
    end: str,
    cache_path: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """从 Yahoo Finance 下载 adjusted close。

    这是公开历史市场数据，但仍依赖第三方数据源的可用性和调整口径。
    如果已有缓存与当前股票池不匹配，会重新下载，而不是误用旧缓存。
    """
    path = Path(cache_path) if cache_path else None
    if path and path.exists() and not refresh:
        try:
            cached = pd.read_csv(path, index_col=0, parse_dates=True)
            return validate_prices(cached, tickers)
        except ValueError:
            # 股票池改变时旧缓存可能不完整，因此继续尝试重新下载。
            pass

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("Install yfinance to download public price data.") from exc

    raw = yf.download(
        list(tickers),
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )
    if raw.empty:
        raise ValueError("The price download returned no observations.")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Adj Close" not in raw.columns.get_level_values(0):
            raise ValueError("Adjusted close prices were not returned by the provider.")
        prices = raw["Adj Close"]
    else:
        if "Adj Close" not in raw.columns:
            raise ValueError("Adjusted close prices were not returned by the provider.")
        prices = raw[["Adj Close"]].rename(columns={"Adj Close": tickers[0]})

    prices = validate_prices(prices, tickers)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        prices.to_csv(path)
    return prices


def simulate_adjusted_close(
    tickers: Sequence[str],
    start: str,
    end: str,
    seed: int = 42,
) -> pd.DataFrame:
    """生成明确标注的模拟价格，仅用于教学和程序 fallback。

    模拟数据不能用于真实投资、alpha 或气候影响结论。这里使用共同市场因子加
    个股噪声生成相关日收益，再累积为从 100 开始的价格路径。
    """
    dates = pd.bdate_range(start=start, end=end, inclusive="left")
    if len(dates) < 2:
        raise ValueError("模拟价格日期范围至少需要两个工作日。")

    rng = np.random.default_rng(seed)
    asset_count = len(tickers)
    market = rng.normal(0.00025, 0.009, size=(len(dates), 1))
    betas = rng.uniform(0.75, 1.25, size=(1, asset_count))
    idiosyncratic = rng.normal(0.0, 0.011, size=(len(dates), asset_count))
    daily_returns = np.clip(market @ betas + idiosyncratic, -0.25, 0.25)
    prices = 100.0 * np.cumprod(1.0 + daily_returns, axis=0)
    return pd.DataFrame(prices, index=dates, columns=list(tickers))


def load_prices_with_fallback(
    tickers: Sequence[str],
    start: str,
    end: str,
    cache_path: str | Path,
    simulated_cache_path: str | Path,
    refresh: bool = False,
    allow_simulated_fallback: bool = True,
    seed: int = 42,
) -> tuple[pd.DataFrame, str]:
    """优先读取真实价格；失败时可回退到明确标注的模拟价格。

    第二个返回值是数据来源标签。模拟数据使用独立文件名，绝不会覆盖真实缓存。
    """
    try:
        prices = download_adjusted_close(
            tickers=tickers,
            start=start,
            end=end,
            cache_path=cache_path,
            refresh=refresh,
        )
        return prices, "yfinance_adjusted_close"
    except Exception as exc:
        if not allow_simulated_fallback:
            raise
        print(
            "警告：yfinance 数据不可用，改用 clearly labelled simulated prices。\n"
            f"原始错误：{type(exc).__name__}: {exc}\n"
            "模拟数据只能用于教学和测试，不能用于真实投资结论。"
        )
        simulated_path = Path(simulated_cache_path)
        if simulated_path.exists() and not refresh:
            simulated = pd.read_csv(simulated_path, index_col=0, parse_dates=True)
            return validate_prices(simulated, tickers), "SIMULATED_FALLBACK"

        simulated = simulate_adjusted_close(tickers, start, end, seed=seed)
        simulated_path.parent.mkdir(parents=True, exist_ok=True)
        simulated.to_csv(simulated_path)
        return simulated, "SIMULATED_FALLBACK"


def validate_prices(prices: pd.DataFrame, tickers: Sequence[str] | None = None) -> pd.DataFrame:
    """检查价格表；不使用 backward fill，以免引入未来信息。"""
    clean = prices.copy()
    clean.index = pd.to_datetime(clean.index)
    clean = clean.sort_index()
    clean = clean.loc[~clean.index.duplicated(keep="first")]
    clean = clean.apply(pd.to_numeric, errors="coerce")

    if tickers is not None:
        missing = sorted(set(tickers) - set(clean.columns))
        if missing:
            raise ValueError(f"Missing requested tickers: {missing}")
        clean = clean.loc[:, list(tickers)]
    if clean.empty or clean.dropna(how="all").empty:
        raise ValueError("No usable prices remain after validation.")
    if (clean <= 0).any().any():
        raise ValueError("Prices must be strictly positive.")
    return clean


def calculate_returns(prices: pd.DataFrame, drop_incomplete: bool = True) -> pd.DataFrame:
    """计算简单日收益率。

    不进行 backward filling，因为它可能把未来日期的信息带回过去。
    """
    returns = prices.pct_change(fill_method=None).replace([float("inf"), -float("inf")], pd.NA)
    return returns.dropna(how="any" if drop_incomplete else "all")
