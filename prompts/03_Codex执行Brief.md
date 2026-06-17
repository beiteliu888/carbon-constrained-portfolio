# 03 Codex 执行 Brief

> 标注：本文件为历史项目补档，内容为根据现有 `README.md`、`PROJECT_REPORT.md`、`CODE_NOTES.md` 和 `PORTFOLIO_OPTIMIZATION_NOTES.md` 反推。它不是 GPT 在项目启动时生成的原始 Codex Brief。

## 项目目标

构建一个 learning-oriented / exploratory Python prototype，用于比较 equal-weight、unconstrained mean-variance 和 carbon-constrained mean-variance 三种组合，并观察 carbon budget constraint 对 portfolio weights、carbon exposure、risk-return metrics、drawdown 和 turnover 的影响。

项目必须保持诚实表述：这是 portfolio construction prototype，不是 alpha research，不是投资建议，不是 production-level strategy。

## 数据需求

### 价格数据

- 使用美国大盘股小型股票池。
- 优先通过 yfinance 下载 adjusted close。
- 若 yfinance 不可用，可使用 clearly labelled simulated fallback，但 simulated data 只用于教学和流程测试。
- 当前项目使用真实价格缓存，数据来源标签为 `yfinance_adjusted_close`。

### Carbon data

- 使用公开披露构造的 carbon intensity。
- 当前定义：

```text
carbon intensity = (Scope 1 + location-based Scope 2) / revenue in USD million
```

- 排放分子来自 Climate Data Utility / CDP。
- 收入分母来自 SEC Companyfacts 10-K revenue。
- 使用 `available_date` 做 point-in-time 对齐。
- 不纳入 Scope 3。
- 不把该指标描述为完整、机构级或完全可比的数据集。

## 默认 universe 与参数

- Tickers: `AAPL, MSFT, WMT, GOOGL, V, NVDA, JPM, COP, JNJ, PG`
- 日期范围：2018-01-01 至 2025-12-31
- Lookback window：252 trading days
- Rebalance frequency：monthly
- Max single-name weight：25%
- Risk aversion：5.0
- Carbon budget：当期 equal-weight carbon exposure 的 70%

## Portfolio 定义

### Equal-weight

每次调仓对全部股票赋予相同权重。它是 baseline，不依赖 expected return 或 covariance matrix。

### Unconstrained mean-variance

使用历史窗口估计 expected returns 和 covariance matrix，在 long-only、fully invested 和 max weight 约束下求解 mean-variance portfolio，不加入 carbon budget。

### Carbon-constrained mean-variance

使用同样的 mean-variance objective 和基本权重约束，但额外加入：

```text
weights @ carbon_intensity <= 70% * equal_weight_carbon_exposure
```

## 优化要求

- 使用 scipy SLSQP 作为主优化器。
- 不使用 custom gradient descent 作为主求解器。
- 约束包括：
  - `sum(weights) = 1`
  - `0 <= weight_i <= max_weight`
  - 可选 carbon budget constraint
- 优化失败、预算不可行或返回权重违反约束时必须显式报错。

## Backtest 要求

- Monthly rebalance。
- 每次调仓只使用调仓日前的历史 returns。
- 每次调仓只使用 `available_date <= rebalance date` 的 carbon data。
- 不用未来数据回填早期 carbon coverage。
- 记录每次调仓的 weights、carbon budget、carbon exposure 和 turnover。
- 不覆盖旧输出，除非用户明确要求。

## Evaluation metrics

至少输出：

- annualized return；
- annualized volatility；
- Sharpe ratio；
- max drawdown；
- average turnover；
- average carbon exposure；
- average weight HHI；
- rebalance diagnostics。

## 图表输出

至少生成：

- cumulative portfolio value；
- drawdown chart；
- average portfolio weights；
- carbon exposure comparison。

## 交付物

- 可运行 Python 模块；
- notebooks；
- tests；
- README；
- PROJECT_REPORT；
- CODE_NOTES；
- PORTFOLIO_OPTIMIZATION_NOTES；
- NETWORKING_TALKING_POINTS；
- outputs/tables；
- outputs/figures。

## 不做什么

- 不声称 alpha。
- 不做 production-level strategy。
- 不做完整 transaction cost、slippage、tax、market impact 模型。
- 不做 factor neutralization。
- 不把 carbon constraint 解释为 return signal。
- 不把 portfolio carbon exposure 下降解释为真实世界减排。

