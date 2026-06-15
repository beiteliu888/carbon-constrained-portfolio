"""可在 PyCharm 直接运行的 learning-oriented prototype 入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from carbon_portfolio.backtest import run_backtest
from carbon_portfolio.carbon import load_carbon_intensity
from carbon_portfolio.data import calculate_returns, load_prices_with_fallback
from carbon_portfolio.metrics import concentration_hhi, performance_summary
from carbon_portfolio.visualization import (
    plot_average_weights,
    plot_carbon_exposure_comparison,
    plot_cumulative_returns,
    plot_drawdowns,
)


def parse_args() -> argparse.Namespace:
    """读取命令行参数；PyCharm 直接运行时不需要填写任何参数。"""
    parser = argparse.ArgumentParser(
        description="Run the learning-oriented carbon portfolio prototype."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Download price data again instead of using the local cache.",
    )
    return parser.parse_args()


def main() -> None:
    """依次完成数据、回测、指标、图表和结果保存。"""
    args = parse_args()
    config_path = PROJECT_ROOT / "config" / "settings.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    data_cfg = config["data"]
    optimization_cfg = config["optimization"]
    backtest_cfg = config["backtest"]

    print("正在读取公开 adjusted close；失败时会使用明确标注的模拟 fallback...")
    prices, data_source = load_prices_with_fallback(
        tickers=data_cfg["tickers"],
        start=data_cfg["start_date"],
        end=data_cfg["end_date"],
        cache_path=PROJECT_ROOT / data_cfg["cache_path"],
        simulated_cache_path=PROJECT_ROOT / data_cfg["simulated_cache_path"],
        refresh=args.refresh,
        allow_simulated_fallback=data_cfg["allow_simulated_fallback"],
        seed=config["project"]["seed"],
    )
    returns = calculate_returns(prices)
    carbon_scores = load_carbon_intensity(
        PROJECT_ROOT / "data" / "carbon_intensity.csv", returns.columns
    )

    print(f"数据来源：{data_source}")
    print("正在运行月度调仓的简化滚动回测...")
    result = run_backtest(
        returns=returns,
        carbon_scores=carbon_scores,
        lookback_days=backtest_cfg["lookback_days"],
        rebalance_frequency=backtest_cfg["rebalance_frequency"],
        annualization_factor=optimization_cfg["annualization_factor"],
        risk_aversion=optimization_cfg["risk_aversion"],
        max_weight=optimization_cfg["max_weight"],
        carbon_budget_ratio=optimization_cfg["carbon_budget_ratio"],
        covariance_ridge=optimization_cfg["covariance_ridge"],
        transaction_cost_bps=backtest_cfg["transaction_cost_bps"],
    )

    summary = performance_summary(
        result.portfolio_returns,
        risk_free_rate=backtest_cfg["risk_free_rate"],
        periods_per_year=optimization_cfg["annualization_factor"],
    )
    turnover_columns = {
        "equal_weight": "equal_weight_turnover",
        "unconstrained_mv": "unconstrained_turnover",
        "carbon_constrained_mv": "constrained_turnover",
    }
    carbon_columns = {
        "equal_weight": "equal_weight_carbon",
        "unconstrained_mv": "unconstrained_carbon",
        "carbon_constrained_mv": "constrained_carbon",
    }
    summary["average_turnover"] = {
        name: result.diagnostics[column].mean()
        for name, column in turnover_columns.items()
    }
    summary["average_carbon_exposure"] = {
        name: result.diagnostics[column].mean()
        for name, column in carbon_columns.items()
    }
    summary["average_weight_hhi"] = {
        name: concentration_hhi(weights).mean()
        for name, weights in result.rebalance_weights.items()
    }

    table_dir = PROJECT_ROOT / "outputs" / "tables"
    figure_dir = PROJECT_ROOT / "outputs" / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    summary.to_csv(table_dir / "performance_summary.csv")
    (table_dir / "data_source.txt").write_text(
        f"{data_source}\n"
        "SIMULATED_FALLBACK means simulated educational data and must not be "
        "used for real investment conclusions.\n"
        "Carbon numerator: Climate Data Utility / CDP disclosed Scope 1 plus "
        "location-based Scope 2. Revenue denominator: SEC 10-K Companyfacts.\n",
        encoding="utf-8",
    )
    result.portfolio_returns.to_csv(table_dir / "portfolio_returns.csv")
    result.diagnostics.to_csv(table_dir / "rebalance_diagnostics.csv")
    for name, weights in result.rebalance_weights.items():
        weights.to_csv(table_dir / f"{name}_weights.csv")

    plot_cumulative_returns(result.portfolio_returns)
    plt.tight_layout()
    plt.savefig(figure_dir / "cumulative_returns.png", dpi=150)
    plt.close()

    plot_drawdowns(result.portfolio_returns)
    plt.tight_layout()
    plt.savefig(figure_dir / "drawdowns.png", dpi=150)
    plt.close()

    plot_average_weights(result.rebalance_weights)
    plt.tight_layout()
    plt.savefig(figure_dir / "average_portfolio_weights.png", dpi=150)
    plt.close()

    plot_carbon_exposure_comparison(result.diagnostics)
    plt.tight_layout()
    plt.savefig(figure_dir / "carbon_exposure_comparison.png", dpi=150)
    plt.close()

    print("\n探索性结果摘要：")
    print(summary.round(4).to_string())
    print(f"\nOutputs saved under: {PROJECT_ROOT / 'outputs'}")
    print(
        "\n谨慎解释：这是 simplified educational prototype。"
        "碳强度来自公开披露，但仍受口径、覆盖和发布时间差异影响；"
        "历史回测结果不是 alpha、未来表现或真实减排效果的证据。"
    )


if __name__ == "__main__":
    main()
