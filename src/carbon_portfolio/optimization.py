"""带可选碳约束的 long-only mean-variance 优化。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize


class OptimizationError(RuntimeError):
    """优化不可行、失败或违反约束时显式抛出的异常。"""


@dataclass(frozen=True)
class OptimizationResult:
    weights: pd.Series
    expected_return: float
    volatility: float
    carbon_exposure: float | None
    objective_value: float
    solver_message: str


def equal_weights(assets: list[str] | pd.Index) -> pd.Series:
    """构造 fully invested 的等权组合。"""
    labels = list(assets)
    if not labels:
        raise ValueError("At least one asset is required.")
    return pd.Series(1.0 / len(labels), index=labels, name="equal_weight")


def _validate_inputs(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    max_weight: float,
) -> tuple[pd.Series, pd.DataFrame]:
    """检查收益、协方差和权重上限是否适合进入优化器。"""
    assets = list(expected_returns.index)
    covariance = covariance.reindex(index=assets, columns=assets)
    if expected_returns.isna().any() or covariance.isna().any().any():
        raise ValueError("Expected returns and covariance must be complete.")
    if not np.isfinite(expected_returns).all() or not np.isfinite(covariance).all().all():
        raise ValueError("Optimization inputs must be finite.")
    if max_weight <= 0 or max_weight > 1:
        raise ValueError("max_weight must be in (0, 1].")
    if max_weight * len(assets) < 1 - 1e-12:
        raise ValueError("max_weight is infeasible for the number of assets.")
    if not np.allclose(covariance, covariance.T, atol=1e-10):
        raise ValueError("Covariance matrix must be symmetric.")
    return expected_returns.astype(float), covariance.astype(float)


def optimize_mean_variance(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    risk_aversion: float = 5.0,
    max_weight: float = 1.0,
    carbon_scores: pd.Series | None = None,
    carbon_budget: float | None = None,
    covariance_ridge: float = 1e-6,
) -> OptimizationResult:
    """最大化预期收益减去方差惩罚，并可加入线性碳预算。

    scipy.optimize 的 SLSQP 能直接处理等式、不等式和边界约束，比手写 gradient
    descent 更适合作为本项目主优化器。它仍不是 production guarantee，必须检查
    收敛状态和返回权重。等价的最小化目标为：
        0.5 * risk_aversion * w'Covw - expected_returns'w
    """
    expected_returns, covariance = _validate_inputs(
        expected_returns, covariance, max_weight
    )
    if risk_aversion <= 0:
        raise ValueError("risk_aversion must be positive.")
    if covariance_ridge < 0:
        raise ValueError("covariance_ridge cannot be negative.")

    assets = expected_returns.index
    cov_values = covariance.to_numpy() + covariance_ridge * np.eye(len(assets))
    mu_values = expected_returns.to_numpy()

    constraints: list[dict[str, object]] = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    ]
    aligned_carbon: pd.Series | None = None
    initial = equal_weights(assets).to_numpy()
    if carbon_budget is not None:
        if carbon_scores is None:
            raise ValueError("carbon_scores are required with a carbon_budget.")
        aligned_carbon = carbon_scores.reindex(assets).astype(float)
        if aligned_carbon.isna().any():
            raise ValueError("Carbon scores do not cover the full asset universe.")
        minimum_feasible = _minimum_carbon_exposure(aligned_carbon, max_weight)
        if carbon_budget < minimum_feasible - 1e-10:
            raise OptimizationError(
                f"Carbon budget {carbon_budget:.6f} is infeasible; "
                f"minimum feasible exposure is {minimum_feasible:.6f}."
            )
        carbon_values = aligned_carbon.to_numpy()
        carbon_scale = max(float(np.max(np.abs(carbon_values))), abs(carbon_budget), 1.0)
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w: (carbon_budget - w @ carbon_values) / carbon_scale,
            }
        )

        # Equal weight 通常高于其 70% 碳预算。使用可行起点并缩放约束，
        # 可以减少碳强度与收益量级差异造成的数值收敛失败。
        equal_exposure = float(initial @ carbon_values)
        if equal_exposure > carbon_budget:
            minimum_weights = _minimum_carbon_weights(
                aligned_carbon, max_weight
            ).to_numpy()
            minimum_exposure = float(minimum_weights @ carbon_values)
            if equal_exposure > minimum_exposure + 1e-12:
                feasible_fraction = (
                    (carbon_budget - minimum_exposure)
                    / (equal_exposure - minimum_exposure)
                )
                # 留出少量碳预算余量，避免初始点同时贴住碳约束和多个权重边界。
                feasible_fraction = float(
                    np.clip(feasible_fraction * 0.95, 0.0, 1.0)
                )
                initial = minimum_weights + feasible_fraction * (
                    initial - minimum_weights
                )
            else:
                initial = minimum_weights

    def objective(weights: np.ndarray) -> float:
        """把 mean-variance 问题写成 scipy 需要的标量目标函数。"""
        variance_penalty = 0.5 * risk_aversion * weights @ cov_values @ weights
        return float(variance_penalty - mu_values @ weights)

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=[(0.0, max_weight)] * len(assets),
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1_000},
    )
    if not result.success:
        raise OptimizationError(f"Optimization failed: {result.message}")

    weights = pd.Series(result.x, index=assets, name="weight")
    if abs(weights.sum() - 1.0) > 1e-7 or (weights < -1e-8).any():
        raise OptimizationError("Solver returned weights that violate basic constraints.")
    if aligned_carbon is not None and float(weights @ aligned_carbon) > carbon_budget + 1e-7:
        raise OptimizationError("Solver returned weights above the carbon budget.")

    variance = float(weights.to_numpy() @ covariance.to_numpy() @ weights.to_numpy())
    carbon_exposure = (
        float(weights @ aligned_carbon) if aligned_carbon is not None else None
    )
    return OptimizationResult(
        weights=weights,
        expected_return=float(weights @ expected_returns),
        volatility=float(np.sqrt(max(variance, 0.0))),
        carbon_exposure=carbon_exposure,
        objective_value=float(result.fun),
        solver_message=str(result.message),
    )


def _minimum_carbon_exposure(scores: pd.Series, max_weight: float) -> float:
    """计算 long-only 和 weight cap 下最低可行 carbon exposure。"""
    weights = _minimum_carbon_weights(scores, max_weight)
    return float(weights @ scores)


def _minimum_carbon_weights(scores: pd.Series, max_weight: float) -> pd.Series:
    """按碳强度从低到高配置，构造满足权重上限的最低碳组合。"""
    remaining = 1.0
    weights = pd.Series(0.0, index=scores.index)
    for asset in scores.sort_values().index:
        allocation = min(max_weight, remaining)
        weights.loc[asset] = allocation
        remaining -= allocation
        if remaining <= 1e-12:
            return weights
    raise ValueError("Unable to construct a fully invested portfolio.")
