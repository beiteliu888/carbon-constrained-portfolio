"""公司碳强度数据的读取、时间对齐与组合暴露计算。"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "ticker",
    "reporting_year",
    "available_date",
    "scope1_tco2e",
    "scope2_location_tco2e",
    "revenue_usd_mn",
    "carbon_intensity_tco2e_per_usd_mn",
}


def load_carbon_intensity(
    path: str | Path,
    tickers: Sequence[str] | None = None,
) -> pd.DataFrame:
    """读取真实披露数据构造的年度碳强度面板，并执行基本质量检查。

    碳强度定义为：
    (Scope 1 + location-based Scope 2) / revenue in USD million。
    原始排放来自 Climate Data Utility / CDP，收入来自 SEC 10-K facts。
    """
    frame = pd.read_csv(path)
    missing_columns = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing_columns:
        raise ValueError(
            f"Carbon intensity file is missing columns: {missing_columns}"
        )

    frame = frame.copy()
    frame["ticker"] = frame["ticker"].astype(str)
    frame["available_date"] = pd.to_datetime(
        frame["available_date"], errors="raise"
    )
    numeric_columns = [
        "reporting_year",
        "scope1_tco2e",
        "scope2_location_tco2e",
        "revenue_usd_mn",
        "carbon_intensity_tco2e_per_usd_mn",
    ]
    frame[numeric_columns] = frame[numeric_columns].apply(
        pd.to_numeric, errors="raise"
    )

    if frame.duplicated(["ticker", "reporting_year"]).any():
        raise ValueError("Ticker and reporting_year pairs must be unique.")
    if not np.isfinite(frame[numeric_columns]).all().all():
        raise ValueError("Carbon intensity numeric fields must be finite.")
    if (frame[["scope1_tco2e", "scope2_location_tco2e"]] < 0).any().any():
        raise ValueError("Reported emissions cannot be negative.")
    if (frame["revenue_usd_mn"] <= 0).any():
        raise ValueError("Revenue must be positive.")

    recalculated = (
        frame["scope1_tco2e"] + frame["scope2_location_tco2e"]
    ) / frame["revenue_usd_mn"]
    if not np.allclose(
        recalculated,
        frame["carbon_intensity_tco2e_per_usd_mn"],
        rtol=1e-8,
        atol=1e-10,
    ):
        raise ValueError("Stored carbon intensity does not match its components.")

    if tickers is not None:
        requested = list(tickers)
        missing_tickers = sorted(set(requested) - set(frame["ticker"]))
        if missing_tickers:
            raise ValueError(
                f"Missing disclosed carbon intensity for: {missing_tickers}"
            )
        frame = frame[frame["ticker"].isin(requested)]

    return frame.sort_values(
        ["available_date", "ticker", "reporting_year"]
    ).reset_index(drop=True)


def carbon_snapshot_as_of(
    panel: pd.DataFrame,
    as_of: str | pd.Timestamp,
    tickers: Sequence[str],
) -> pd.DataFrame:
    """选择在指定日期已经公开的每家公司最新一条碳强度记录。

    这里使用 available_date，而不是直接按 reporting_year 选择，目的是避免
    在历史回测中提前使用尚未公开的排放或收入信息。
    """
    date = pd.Timestamp(as_of)
    requested = list(tickers)
    available = panel[
        (panel["available_date"] <= date) & panel["ticker"].isin(requested)
    ]
    latest = (
        available.sort_values(["available_date", "reporting_year"])
        .groupby("ticker", as_index=False)
        .tail(1)
        .set_index("ticker")
        .reindex(requested)
    )
    missing = latest.index[latest["available_date"].isna()].tolist()
    if missing:
        raise ValueError(
            f"No point-in-time carbon intensity available on {date.date()} "
            f"for: {missing}"
        )
    return latest


def carbon_scores_as_of(
    carbon_data: pd.Series | pd.DataFrame,
    as_of: str | pd.Timestamp,
    tickers: Sequence[str],
) -> pd.Series:
    """统一处理静态测试分数与真实年度碳强度面板。

    Series 仅保留给单元测试和教学小例子；主程序使用 DataFrame 面板。
    """
    requested = list(tickers)
    if isinstance(carbon_data, pd.Series):
        scores = carbon_data.reindex(requested).astype(float)
        if scores.isna().any():
            raise ValueError("Carbon scores must cover every asset.")
    elif isinstance(carbon_data, pd.DataFrame):
        snapshot = carbon_snapshot_as_of(carbon_data, as_of, requested)
        scores = snapshot["carbon_intensity_tco2e_per_usd_mn"].astype(float)
    else:
        raise TypeError("carbon_data must be a pandas Series or DataFrame.")

    if not np.isfinite(scores).all() or (scores < 0).any():
        raise ValueError("Carbon intensity values must be finite and non-negative.")
    scores.name = "carbon_intensity_tco2e_per_usd_mn"
    return scores


def portfolio_carbon_exposure(
    weights: pd.Series,
    scores: pd.Series,
) -> float:
    """计算组合加权平均碳强度，单位为 tCO2e / USD million revenue。"""
    aligned_scores = scores.reindex(weights.index)
    if aligned_scores.isna().any():
        raise ValueError("Weights and carbon intensity are not fully aligned.")
    return float(weights @ aligned_scores)
