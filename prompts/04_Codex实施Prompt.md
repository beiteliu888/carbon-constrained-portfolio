# 04 Codex 实施 Prompt

> 标注：本文件为历史项目补档，内容根据现有项目实现和最终交付物反推，不是项目启动时实际发送给 Codex 的逐字实施 prompt。

## 任务

请基于 `prompts/03_Codex执行Brief.md`，实现一个可运行、可解释、适合学习的 Carbon-Constrained Portfolio Optimization Prototype。

项目路径：

```text
/Users/max/Developer/10_active/001_carbon-constrained-portfolio
```

## 实施要求

1. 建立清晰项目结构：
   - `config/`
   - `data/`
   - `notebooks/`
   - `src/carbon_portfolio/`
   - `tests/`
   - `outputs/`
2. 使用函数封装，不要过度工程化。
3. 每个关键模块使用中文注释和谨慎说明。
4. 保持项目定位为 learning-oriented prototype。
5. 不声称 alpha，不声称 production-level strategy。

## 需要实现的模块

- `data.py`：下载、缓存、验证 adjusted close，并计算 returns。
- `carbon.py`：读取 carbon intensity，按 `available_date` 做 point-in-time 对齐，并计算 portfolio carbon exposure。
- `optimization.py`：实现 equal-weight、unconstrained MV 和 carbon-constrained MV。
- `backtest.py`：实现 rolling monthly rebalance，避免明显 look-ahead bias。
- `metrics.py`：计算 performance metrics。
- `visualization.py`：生成图表。
- `sensitivity.py`：做基础参数敏感性分析。
- `run_prototype.py`：项目入口脚本。

## 数据要求

- 价格数据优先使用 yfinance adjusted close。
- 若 yfinance 不可用，允许 simulated fallback，但必须明确标注 `SIMULATED_FALLBACK`，且模拟数据不能用于真实结论。
- Carbon intensity 使用公开披露数据构造：

```text
(Scope 1 + location-based Scope 2) / revenue in USD million
```

- Carbon data 必须记录数据可得日期，回测中不得提前使用未来披露。

## Optimization 要求

- Long-only。
- Fully invested。
- 单一股票最大权重 25%。
- Carbon-constrained portfolio 的 carbon exposure 不超过当期 equal-weight carbon exposure 的 70%。
- 使用 scipy SLSQP 作为主优化器。
- 优化失败、约束不可行或返回权重违反约束时显式报错。

## Backtest 要求

- Monthly rebalance。
- Rolling lookback window 为 252 trading days。
- 每次 rebalance 只使用过去 returns 和当时可得 carbon data。
- 不覆盖旧 outputs。
- 记录 returns、weights、rebalance diagnostics 和 turnover。

## 输出要求

生成：

- `outputs/tables/performance_summary.csv`
- `outputs/tables/portfolio_returns.csv`
- `outputs/tables/rebalance_diagnostics.csv`
- 三种 portfolio weights CSV
- `outputs/figures/cumulative_returns.png`
- `outputs/figures/drawdowns.png`
- `outputs/figures/average_portfolio_weights.png`
- `outputs/figures/carbon_exposure_comparison.png`

生成或更新：

- `README.md`
- `PROJECT_REPORT.md`
- `CODE_NOTES.md`
- `PORTFOLIO_OPTIMIZATION_NOTES.md`
- `NETWORKING_TALKING_POINTS.md`

## 验证要求

- 添加单元测试，覆盖数据验证、碳数据对齐、优化约束、回测时间切分和 metrics。
- 运行 `pytest`。
- 若不能运行测试，必须说明原因。

## 诚信边界

README、报告和话术中必须明确：

- 这是 exploratory / learning-oriented prototype。
- 结果不是 alpha 证据。
- Backtest 是 simplified historical exercise。
- Carbon exposure 下降不等于真实世界减排。
- Expected return estimate 和 covariance matrix 都有显著不确定性。
- 当前股票池小，存在 selection bias 和 survivorship bias。

