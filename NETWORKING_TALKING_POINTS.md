# Networking Talking Points: Carbon-Constrained Portfolio Optimization Prototype

> 用途：这份文件不是正式 project report，而是帮助我在 networking conversation 中，用自然、诚实、有技术含量的方式介绍这个 learning-oriented prototype。
>
> 核心边界：不要把它说成 alpha research、成熟交易策略、production-level system 或真实世界减排证明。

---

## 1. 30-second project overview

我做了一个 carbon-constrained portfolio optimization 的学习型 prototype，主要想理解在传统 mean-variance optimization 里加入 carbon budget constraint 后，组合权重、风险收益特征、drawdown、turnover 和 carbon exposure 会怎么变化。

项目比较了三种组合：equal-weight、无碳约束的 mean-variance portfolio，以及加入碳预算约束的 mean-variance portfolio。碳约束的形式是让组合加权 carbon intensity 不超过当期 equal-weight portfolio 的 70%。这个项目的定位是 exploratory 和 learning-oriented，不是成熟交易策略，也不是 alpha 发现。

---

## 2. 1-minute version

这个项目是一个小型的 portfolio construction prototype。我用 10 只美国大盘股作为 universe，价格数据来自 yfinance 的 adjusted close，carbon intensity 使用公开披露数据构造，口径是 Scope 1 加 location-based Scope 2，再除以 SEC 10-K revenue。

方法上，我比较了 equal-weight、unconstrained mean-variance 和 carbon-constrained mean-variance。优化是 long-only、fully invested，单只股票最高 25%，月度调仓，用过去 252 个交易日估计 expected return 和 covariance matrix。碳约束是每次调仓时，组合 carbon exposure 不能超过 equal-weight carbon exposure 的 70%。

当前结果比较符合直觉：carbon-constrained portfolio 明显降低了 average carbon exposure，但也改变了权重，并且在这个样本里 annualized return、Sharpe ratio 和 max drawdown 都弱于另外两种组合。所以我不会把它解释为 alpha，而是把它看成一个用于理解 constraints 如何改变 portfolio construction 的 early-stage prototype。

---

## 3. If they ask “What exactly did you build?”

我搭了一个可以从数据到回测输出的最小可运行 pipeline。

主要模块包括：

- `data.py`：下载或读取 adjusted close，验证价格数据，并计算简单日收益率。
- `carbon.py`：读取 carbon intensity 面板，用 `available_date` 做 point-in-time 对齐，并计算组合加权 carbon exposure。
- `optimization.py`：实现 equal-weight、unconstrained mean-variance 和 carbon-constrained mean-variance。
- `backtest.py`：用滚动窗口做月度调仓，记录收益、权重、turnover 和 carbon diagnostics。
- `metrics.py`：计算 annualized return、annualized volatility、Sharpe ratio、max drawdown、average turnover 和 average carbon exposure。
- `visualization.py`：生成 cumulative value、drawdown、average weights 和 carbon exposure comparison 图。

数据进入项目的方式比较直接：

- 价格数据优先来自 yfinance adjusted close。
- 当前数据来源标签是 `yfinance_adjusted_close`。
- 如果 yfinance 失败，代码允许使用明确标注的 simulated fallback，但 simulated data 不能用于真实投资或气候结论。
- 当前 performance output 来自真实价格缓存，不是 simulated fallback。

Carbon intensity 的定义是：

```text
carbon intensity = (Scope 1 + location-based Scope 2) / revenue in USD million
```

这个指标来自公开披露数据，但我会明确说它不是机构级、完全可比或完整审计的数据集，也没有包含 Scope 3。

Backtest 避免明显 look-ahead bias 的方式是：

- 每次调仓只用调仓日前 252 个交易日的收益率估计 expected return 和 covariance。
- 调仓日当天收益不进入该次估计。
- Carbon data 只使用 `available_date <= rebalance date` 的最新披露。
- 早期如果 carbon data 尚未覆盖全部股票，回测会等待，而不是用未来数据回填。

输出包括：

- `performance_summary.csv`
- `portfolio_returns.csv`
- `rebalance_diagnostics.csv`
- 每种策略的 rebalance weights
- `cumulative_returns.png`
- `drawdowns.png`
- `average_portfolio_weights.png`
- `carbon_exposure_comparison.png`

---

## 4. If they ask “What is the quant part?”

Quant 部分主要在 portfolio construction 和 backtesting design。

第一层是 mean-variance optimization。每次调仓时，我用过去 252 个交易日估计：

```text
expected return = daily sample mean * 252
covariance matrix = daily sample covariance * 252
```

然后优化器在 expected return 和 portfolio variance 之间做权衡。目标函数可以理解为：

```text
minimize risk penalty - expected return
```

更具体地：

```text
minimize 0.5 * risk_aversion * portfolio variance - portfolio expected return
```

第二层是 constraints。所有优化组合都满足：

```text
sum(weights) = 1
0 <= weight_i <= 25%
```

这意味着组合是 fully invested、long-only，并且限制单一股票集中度。

第三层是 carbon budget constraint。碳约束组合额外满足：

```text
portfolio carbon exposure <= 70% * equal-weight carbon exposure
```

这里的 portfolio carbon exposure 是 weights 和 carbon intensity 的加权平均。

第四层是回测。组合月度调仓，两次调仓之间权重随资产收益自然漂移。项目记录 turnover 和 drawdown，因为 optimized portfolio 不能只看收益，还要看交易频率、回撤和组合稳定性。

这个项目的 quant 内容不是复杂模型，而是清楚地把 objective function、constraints、rolling estimation、turnover 和 diagnostics 串起来。

---

## 5. If they ask “What is the climate finance part?”

Climate finance 部分主要体现在：我把 carbon exposure 作为 portfolio construction constraint，而不是把它当成收益预测因子。

本项目使用的 carbon intensity 是：

```text
(Scope 1 + location-based Scope 2) / revenue in USD million
```

这可以理解为一种 simplified carbon-aware portfolio construction：在满足收益风险优化框架的同时，对组合加权披露碳强度设置预算。

但是我不会把它说成 impact measurement。原因是：

- 降低组合加权 carbon intensity 不等于公司真实排放下降。
- 它不证明资本配置产生了 additionality。
- 它没有纳入 Scope 3。
- 不同公司的披露边界、Scope 2 方法、财年和估算方式可能不同。
- 它只是组合层面的披露指标约束，不是真实世界减排证明。

所以更准确的说法是：这是 carbon-aware portfolio construction，不是 real-world decarbonization measurement。

---

## 6. If they ask “What did you find?”

我会用非常谨慎的语言回答：

在当前 10 只美国大盘股、2018 到 2025 配置区间、252 日估计窗口、月度调仓、25% 单股上限和 70% carbon budget 的设定下，carbon-constrained portfolio 确实降低了 average carbon exposure，并且明显改变了组合权重。

但它没有在当前样本中带来更好的 risk-return profile。具体来说，carbon-constrained portfolio 的 annualized return、Sharpe ratio 和 max drawdown 都弱于 equal-weight 和 unconstrained mean-variance。这个结果更像是在展示约束带来的 trade-off，而不是证明低碳组合更好。

当前项目输出结果如下：

| Portfolio | Annualized Return | Annualized Volatility | Sharpe Ratio | Max Drawdown | Average Turnover | Average Carbon Exposure |
|---|---:|---:|---:|---:|---:|---:|
| Equal-weight | 24.13% | 17.01% | 1.42 | -21.93% | 2.42% | 65.45 |
| Unconstrained MV | 24.35% | 21.47% | 1.13 | -26.42% | 17.01% | 77.68 |
| Carbon-constrained MV | 21.90% | 21.57% | 1.02 | -29.76% | 16.00% | 34.02 |

单位说明：

- Return、volatility、drawdown 和 turnover 为比例指标，表中用百分比表达。
- Average carbon exposure 的单位是 `tCO2e / USD million revenue`。
- 当前回测有效日收益观测数为 1,339。

我会强调：这只是一个 simplified historical backtest observation，不是 proof，不是 alpha，也不是未来表现预测。

---

## 7. If they ask “Is this alpha?”

No, not at this stage.

我会直接说，这不是 alpha research。Carbon constraint 在这里不是 return-predictive signal，而是 portfolio construction constraint。

当前项目没有做：

- IC 或 rank IC 分析；
- long-short factor portfolio；
- factor neutralization；
- sector-neutral 或 beta-neutral portfolio；
- strict out-of-sample validation；
- 完整 transaction cost model；
- slippage、bid-ask spread、market impact 或 liquidity constraint；
- 多样本、多市场 robustness tests。

所以更准确的定位是：

```text
This is a portfolio construction prototype that studies how a carbon budget constraint mechanically changes weights, carbon exposure, and historical risk-return metrics.
```

而不是：

```text
This is an alpha strategy.
```

---

## 8. If they ask “What are the main limitations?”

最重要的 limitations 是：

- **Small universe**：只有 10 只美国大盘股，不能代表完整市场。
- **Survivorship / selection bias**：股票池是固定的，并且受到 carbon data 可得性影响。
- **Expected return estimation noise**：历史均值作为 expected return 很 noisy。
- **Covariance instability**：252 日样本 covariance matrix 可能不稳定。
- **No full transaction costs**：当前交易成本设为 0 bps。
- **No slippage / market impact**：没有 bid-ask spread、流动性和执行成本模拟。
- **No sector or factor neutralization**：没有控制 sector、beta、momentum、value、size 等暴露。
- **Carbon data comparability issues**：公司披露边界、财年、Scope 2 方法和估计方式可能不同。
- **No Scope 3**：当前只包含 Scope 1 和 location-based Scope 2。
- **Simple backtest**：回测设计适合教学，但不是 institutional production backtest。
- **Cannot infer future performance**：历史结果不能证明未来表现。
- **Not alpha research**：项目没有证明 carbon intensity 可以预测股票收益。

---

## 9. If they ask “What would you improve next?”

### Immediate next steps

- 加入 transaction costs，并做 turnover sensitivity。
- 加入 sector exposure analysis，观察碳约束是否隐含改变 sector tilt。
- 测试不同 carbon budget，例如 60%、70%、80%、100%。
- 加入 covariance shrinkage，比较权重稳定性是否改善。
- 改善 expected return assumption，例如使用共同均值、shrinkage mean 或更保守假设。
- 加强 diagnostics，例如记录 active constraints、边界权重、优化失败次数和权重集中度。

### More advanced next steps

- 使用更大的 point-in-time universe，包括退市和历史成分变化。
- 引入 factor risk model，控制 sector、beta、size、value、momentum 等暴露。
- 加入 Scope 3、transition risk 或 forward-looking climate metrics。
- 如果要研究 signal，再单独做 carbon-related signal research。
- 做 IC / rank IC，判断 carbon intensity 或变化率是否有预测关系。
- 构建 long-short factor portfolio，和 portfolio construction prototype 分开。
- 做严格 out-of-sample validation 和 walk-forward robustness tests。
- 在不同样本期、不同 universe、不同参数下做 robustness tests。

---

## 10. Strong phrasing vs weak phrasing

| Instead of saying | Say this |
|---|---|
| I found alpha. | I explored how a carbon constraint changes portfolio construction. |
| The strategy works. | In this simplified backtest, the constraint lowered carbon exposure but came with trade-offs. |
| This proves low-carbon investing works. | This prototype helps isolate the mechanical effect of a carbon budget constraint. |
| The carbon-constrained portfolio is better. | The carbon-constrained portfolio achieved lower carbon exposure, but its risk-return metrics were weaker in this sample. |
| This is a trading strategy. | This is a learning-oriented portfolio construction prototype. |
| The model predicts returns. | The model uses historical sample means as a simple expected return input, which is noisy. |
| The backtest validates the strategy. | The backtest is a simplified historical exercise and needs stronger robustness checks. |
| The portfolio reduces emissions. | The portfolio lowers weighted disclosed carbon intensity under this data definition. |
| The carbon data is clean and comparable. | The carbon data is based on public disclosures and has comparability limitations. |
| The optimized portfolio should outperform. | The optimized portfolio reflects the objective function and constraints, not a guarantee of future performance. |
| Sharpe ratio proves quality. | Sharpe ratio is one descriptive metric and is sensitive to sample period and assumptions. |
| The carbon constraint is a signal. | The carbon constraint is used as an investment mandate or risk constraint, not as a return signal. |

---

## 11. Possible follow-up questions and good answers

### 1. Why mean-variance?

Because it is a transparent framework for studying the trade-off between expected return and risk. It is not perfect, but it makes the role of constraints very clear, which is useful for this learning-oriented prototype.

### 2. How did you estimate expected returns?

I used the annualized mean of the previous 252 daily returns at each rebalance date. I know this is noisy and not a strong forecasting model. It is mainly used here as a simple input to make the optimization framework operational.

### 3. How stable is the covariance matrix?

Probably not very stable, especially with a 252-day rolling window and a small universe. I added a small diagonal ridge for numerical stability, but a better next step would be covariance shrinkage or a factor risk model.

### 4. Why 70% carbon budget?

It is a transparent teaching parameter: the constrained portfolio must stay below 70% of the equal-weight portfolio’s carbon exposure at each rebalance. I would not claim 70% is optimal. It should be tested through sensitivity analysis.

### 5. Why monthly rebalance?

Monthly rebalance is a simple compromise. It updates the portfolio regularly without turning the exercise into a high-turnover daily optimization. It is still an assumption, and I would test quarterly or different rebalance frequencies later.

### 6. Why this universe?

I used 10 liquid U.S. large-cap names to keep the prototype interpretable and easy to inspect. The universe also reflects carbon data availability, which creates selection bias. A more robust version would use a larger point-in-time universe.

### 7. Did you include transaction costs?

Not in the current result. The configuration has transaction cost set to 0 bps. I report turnover, but I do not yet convert it into realistic trading costs, slippage, bid-ask spread or market impact.

### 8. How did you avoid look-ahead bias?

For returns, each rebalance uses only the previous 252 trading days. For carbon data, the backtest only uses records with `available_date` on or before the rebalance date. If early carbon coverage is incomplete, the backtest waits instead of using future data.

### 9. Is carbon intensity a signal?

Not in this project. Carbon intensity is used as a constraint, not a predictor of future returns. To test it as a signal, I would need IC, rank IC, factor controls, long-short portfolio construction and out-of-sample validation.

### 10. How would you make it more robust?

I would add transaction costs, sector and factor exposure diagnostics, covariance shrinkage, parameter sensitivity, a larger point-in-time universe, and robustness tests across different periods and carbon budget levels.

### 11. What would you do with factor controls?

I would check whether the carbon constraint is simply creating sector, beta, size, value or momentum tilts. A stronger version would either report those tilts clearly or add constraints to neutralize them.

### 12. What surprised you?

The main useful observation is that lowering portfolio carbon exposure is mechanically achievable, but it changes weights and can come with risk-return trade-offs. Also, the unconstrained MV portfolio can become more carbon-intensive than equal-weight, depending on estimated returns and covariance.

---

## 12. My personal learning angle

This project helped me connect my climate finance background with quantitative portfolio construction. I learned that carbon exposure can be introduced into a portfolio not only as a reporting metric, but also as a constraint inside the optimization problem.

The most important learning point is that constraints are not just comments added after the model. They directly change the feasible set and therefore change optimal weights. I also learned that backtest results need careful interpretation: historical returns, Sharpe ratio and drawdown can describe what happened in one simplified setup, but they do not prove future performance.

From the quant side, the project made expected return estimation feel much more fragile. A small change in historical mean, covariance, risk aversion or carbon budget can change the optimized portfolio. From the climate data side, I also became more aware that carbon data has boundary, timing and comparability issues. The honest boundary of the project matters as much as the code itself.

---

## 13. Final concise script

I recently built a small carbon-constrained portfolio optimization prototype to connect my climate finance background with portfolio construction.

The project compares three portfolios on the same 10-stock U.S. large-cap universe: equal-weight, unconstrained mean-variance, and carbon-constrained mean-variance. Prices come from yfinance adjusted close, and carbon intensity is based on public Scope 1 plus location-based Scope 2 disclosures divided by SEC 10-K revenue.

The quant part is a rolling monthly backtest. At each rebalance, I use only the previous 252 trading days to estimate expected returns and the covariance matrix, then solve a long-only, fully invested mean-variance optimization with a 25% single-name cap. The carbon-constrained version adds one extra condition: portfolio carbon exposure has to stay below 70% of the equal-weight portfolio’s carbon exposure at that point in time.

In the current output, the carbon-constrained portfolio lowered average carbon exposure from 65.45 for equal-weight and 77.68 for unconstrained MV to 34.02. But it did not improve the historical risk-return profile in this sample: its annualized return was 21.90%, Sharpe ratio was 1.02, and max drawdown was -29.76%, weaker than the other two portfolios.

So I would not describe this as alpha or a validated strategy. I see it as an exploratory portfolio construction prototype that shows how a carbon budget constraint mechanically changes weights and trade-offs. The next thing I would improve is to add transaction costs, sector and factor diagnostics, covariance shrinkage, and broader robustness tests.

