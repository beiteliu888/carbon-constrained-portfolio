import pandas as pd

import carbon_portfolio.data as data_module


def test_simulated_prices_are_positive_and_reproducible():
    """模拟 fallback 应可复现，并且价格必须为正。"""
    first = data_module.simulate_adjusted_close(
        ["A", "B"], "2024-01-01", "2024-02-01", seed=42
    )
    second = data_module.simulate_adjusted_close(
        ["A", "B"], "2024-01-01", "2024-02-01", seed=42
    )
    pd.testing.assert_frame_equal(first, second)
    assert (first > 0).all().all()


def test_download_failure_uses_labelled_simulated_fallback(monkeypatch, tmp_path):
    """真实数据下载失败时，应使用独立文件和清楚的数据来源标签。"""

    def fail_download(*args, **kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(data_module, "download_adjusted_close", fail_download)
    prices, source = data_module.load_prices_with_fallback(
        tickers=["A", "B"],
        start="2024-01-01",
        end="2024-03-01",
        cache_path=tmp_path / "real.csv",
        simulated_cache_path=tmp_path / "SIMULATED.csv",
        allow_simulated_fallback=True,
    )
    assert source == "SIMULATED_FALLBACK"
    assert list(prices.columns) == ["A", "B"]
    assert (tmp_path / "SIMULATED.csv").exists()
