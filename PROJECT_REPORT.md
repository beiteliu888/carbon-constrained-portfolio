# 碳约束下的组合优化初步探索：项目报告

## 1. 项目摘要

本项目构建了一个碳约束组合优化原型，用于观察在传统均值—方差优化（mean-variance optimization）中加入碳预算约束（carbon budget constraint）后，组合权重、碳暴露、历史风险收益指标、回撤和换手率会如何变化。

项目比较三种组合：等权重组合（equal-weight portfolio）、无碳约束的均值—方差组合（unconstrained mean-variance portfolio），以及碳约束下的均值—方差组合（carbon-constrained mean-variance portfolio）。

价格数据来自通过 yfinance 下载的美国大型上市公司 adjusted close，当前输出所使用的数据来源标签为 yfinance_adjusted_close。碳强度的排放分子来自 Climate Data Utility 汇总的 CDP Scope 1 和 location-based Scope 2 披露，收入分母来自 SEC Companyfacts 的年度 10-K revenue。回测采用 252 个交易日滚动估计窗口和月度调仓，并按照信息实际可得日期处理收益和碳披露数据，以减少明显的前视偏差（look-ahead bias）。

在当前样本和简化设定下，碳约束下的均值—方差组合的平均加权披露碳强度为 34.02 tCO2e / USD million revenue，低于等权重组合的 65.45，也低于无碳约束的均值—方差组合的 77.68。与此同时，碳约束组合在本历史样本中的年化收益、Sharpe ratio 和最大回撤均弱于另外两种组合。

这一结果说明，在当前约束设定和样本区间内，降低组合加权披露碳强度可能伴随一定的组合构建权衡（portfolio construction trade-off）。但该结果不能被解释为 alpha、未来表现预测、真实世界减排效果，或已经经过充分验证的交易策略。

## 2. 项目动机：为什么做这个项目

传统投资组合优化通常围绕预期收益和风险之间的权衡展开。投资者会根据资产的预期收益（expected return）、波动率（volatility）和协方差（covariance）决定组合权重，希望在给定风险下获得较高的预期收益，或在给定收益目标下降低风险。

但现实中的投资组合往往还受到其他限制，例如只做多要求（long-only mandate）、单一资产权重上限（single-name weight cap）、跟踪误差约束、流动性约束、ESG 要求或碳预算。加入这些限制后，数学上的最优组合可能发生明显变化，资产权重、行业暴露、分散化程度、换手率和历史风险收益特征都可能受到影响。

因此，本项目关注的问题不是“低碳组合是否一定更好”，而是碳约束如何进入组合构建过程，以及这一约束在当前样本中会带来哪些可观察的组合变化和机会成本。

## 3. Research Question 和 Hypothesis

### 3.1 Research Question

在一个简化的只做多美国股票组合中，如果相对于等权重基准加入碳预算约束，组合权重、平均碳暴露、历史风险收益指标、回撤、换手率和集中度会如何变化？

### 3.2 Hypothesis

加入碳约束后，组合的加权披露碳强度预期会下降，同时股票权重、行业构成、分散化程度和风险收益权衡也可能发生变化。该约束不必然提高收益，也不必然降低风险，其影响需要通过滚动回测、权重记录和历史指标进行观察。

这个 hypothesis 是组合构建假设，而不是 alpha 假设。项目没有预设 carbon intensity 能够预测未来收益。

## 4. 数据选择

### 4.1 价格数据

项目优先使用 yfinance 下载公开历史 adjusted close：

- 配置日期范围：2018-01-01 至 2025-12-31。
- 当前价格缓存最后一个交易日：2025-12-30。
- 数据频率：日度交易数据。
- 价格字段：adjusted close。
- 日简单收益率：相邻交易日 adjusted close 的百分比变化。
- 数据验证：检查日期顺序、重复日期、股票覆盖、数值格式和非正价格。
- 缺失值处理：收益率计算不使用 backward fill；默认删除任一股票缺失的日期。

简单日收益率定义为：

```text
return(i,t) = price(i,t) / price(i,t-1) - 1
```

如果 yfinance 因网络或接口问题不可用，代码允许使用明确标注的 SIMULATED_FALLBACK。模拟数据使用独立缓存文件，只用于代码测试和教学，不能支持真实投资、alpha 或气候影响结论。当前报告中的结果来自真实价格缓存，而不是模拟数据。

虽然价格配置从 2018 年开始，但回测还需要 252 日估计窗口和完整的 point-in-time carbon data。当前实际组合收益区间为 2020-09-01 至 2025-12-30，共 1,339 个日收益观测；共有 64 个调仓日。

### 4.2 股票池选择

当前股票池包含十只美国大型上市公司：

| Ticker | Company | Broad business category | 选择说明 |
|---|---|---|---|
| AAPL | Apple Inc. | Technology hardware | 大型、流动性较高，并具有公开碳披露 |
| MSFT | Microsoft Corporation | Software / cloud technology | 提供大型科技公司暴露 |
| WMT | Walmart Inc. | Consumer retail | 提供消费与零售业务暴露 |
| GOOGL | Alphabet Inc. | Internet services / technology | 提供数字平台与科技业务暴露 |
| V | Visa Inc. | Payment services | 提供支付服务业务暴露 |
| NVDA | NVIDIA Corporation | Semiconductors | 提供半导体业务暴露 |
| JPM | JPMorgan Chase & Co. | Banking / financial services | 提供金融服务业务暴露 |
| COP | ConocoPhillips | Energy exploration and production | 提供高直接排放能源业务暴露 |
| JNJ | Johnson & Johnson | Healthcare | 提供医疗健康业务暴露 |
| PG | Procter & Gamble Co. | Consumer staples | 提供日常消费品业务暴露 |

表中的类别只是为了便于理解公司的宽泛业务性质。当前代码没有系统读取或维护正式的 sector classification，也没有输出 sector exposure，因此本报告不对行业中性或行业贡献作定量结论。

WMT、V 和 COP 替换了早期示例中的 AMZN、META 和 XOM，原因是当前公开碳数据的连续覆盖更适合 point-in-time backtest。这种基于数据可得性的选择本身会产生 selection bias。十只股票只是小型教学 universe，不能代表完整美国股票市场，也不足以支持广泛的市场层面结论。

### 4.3 Carbon data

当前版本不再使用人为设定的 synthetic carbon score。项目使用真实公开披露构造简化的公司层面碳强度指标：

```text
carbon intensity
= (Scope 1 + location-based Scope 2) / revenue in USD million
```

- 排放来源：Climate Data Utility / CDP。
- 收入来源：SEC Companyfacts 10-K。
- 排放单位：tCO2e。
- 收入单位：USD million。
- 碳强度单位：tCO2e per USD million revenue。
- available_date：CDP 报告日期和 SEC filing date 中较晚者。

代码在每个调仓日只选择 available_date <= rebalance date 的最新记录，以避免提前使用尚未公开的数据。

| Ticker | 披露碳强度范围 | 报告年份 | 数据性质与说明 |
|---|---|---|---|
| AAPL | 2.84–3.51 | 2019–2022 | 公开 Scope 1 + location-based Scope 2，以收入标准化 |
| MSFT | 28.01–32.89 | 2018–2022 | 同上 |
| WMT | 29.48–37.54 | 2018–2022 | 同上；部分排放和收入期末并非完全一致 |
| GOOGL | 25.70–32.34 | 2018–2022 | 同上 |
| V | 2.30–4.93 | 2018–2022 | 同上；部分记录存在报告期时间差 |
| NVDA | 5.13–9.16 | 2018–2023 | 同上 |
| JPM | 6.11–7.54 | 2018–2022 | 同上 |
| COP | 262.31–859.77 | 2018–2022 | 同上；直接能源生产使该口径下数值较高 |
| JNJ | 10.43–13.79 | 2018–2022 | 同上 |
| PG | 55.92–70.87 | 2018–2022 | 同上 |

这些数据来自真实公开披露，但不等同于机构级、审计一致或完全可比的数据集。不同公司可能使用不同的组织边界、Scope 2 方法、估算流程、重述政策和财年。本项目没有纳入 Scope 3，也没有独立验证第三方 assurance。

组合碳暴露计算为：

```text
portfolio carbon exposure = sum(weight(i) * carbon_intensity(i))
```

这是一项加权披露指标，不代表组合实际造成的排放，也不代表资本配置产生了现实世界减排。

## 5. 方法论

### 5.1 Equal-weight portfolio

等权重组合在每次调仓时为十只股票分别配置 10%：

```text
weight(i) = 1 / number_of_assets
```

该组合不依赖预期收益或协方差估计，因此是最简单、透明的 benchmark。它用于比较优化过程是否改变历史收益、风险、权重集中度和碳暴露。

等权重组合不是无风险基准。它仍然受到股票池选择、市场行情和定期再平衡的影响。

### 5.2 Unconstrained mean-variance portfolio

无碳约束的均值—方差组合在不设置碳预算的情况下，权衡历史均值收益和组合方差。项目使用过去 252 个交易日估计：

```text
expected return = daily sample mean * 252
covariance = daily sample covariance * 252
```

优化目标写成最小化形式：

```text
minimize:
0.5 * risk_aversion * weight' * covariance * weight
- expected_return' * weight
```

共同约束为：

```text
sum(weights) = 1
0 <= weight(i) <= 25%
```

因此，组合是只做多、满仓配置，并限制单一股票最高权重为 25%。风险厌恶参数为 5.0。协方差矩阵加入 1e-6 的 diagonal ridge，以减少部分数值不稳定问题。

均值—方差框架直观且便于解释约束如何改变权重，但历史均值是噪声较大的预期收益估计量，样本协方差也可能不稳定。优化权重可能对窗口长度、风险厌恶参数和输入数据的小变化较为敏感。

### 5.3 Carbon-constrained mean-variance portfolio

碳约束下的均值—方差组合使用相同的均值—方差目标函数和基本约束，并增加以下碳预算约束：

```text
weight' * carbon_intensity <= carbon_budget
```

每个调仓日的 carbon budget 定义为：

```text
carbon budget
= 70% * current equal-weight carbon exposure
```

预算会随着当时最新可得的公司披露数据而变化。优化器在每次调仓时重新检查该预算在 25% 单股权重上限下是否可行，并验证求解结果没有超过预算。

碳约束会限制高碳强度股票可以承担的权重，但最终权重仍同时受到预期收益、协方差、风险厌恶参数和单股权重上限的影响。因此，约束组合不一定每次都刚好位于碳预算边界。如果无碳约束的最优解已经低于预算，碳约束可能不会成为 active constraint。

这一方法属于 carbon-aware portfolio construction，而不是 return-predictive alpha signal。

### 5.4 Optimizer

项目使用 scipy.optimize.minimize 的 SLSQP 方法。SLSQP 可以同时处理：

- 权重和为 1 的等式约束；
- 碳预算不等式约束；
- 只做多和单一股票最高权重的边界约束。

为改善数值稳定性，代码将碳约束按其量级归一化；当 equal-weight 初始点超过预算时，使用最低碳可行组合与 equal-weight 之间的内部可行点作为初始值。求解失败、预算不可行或返回权重违反约束时，程序会显式报错。

本项目没有使用 custom NumPy gradient descent 作为主求解器。SLSQP 适合本教学型 constrained optimization 原型，但这并不构成 production-level solver guarantee。

### 5.5 Backtesting design

回测设计如下：

| 项目 | 当前设定 |
|---|---|
| Price frequency | Daily |
| Rebalance frequency | Monthly |
| Rebalance timing | 每月第一个可交易日 |
| Lookback window | 252 个交易日 |
| Annualization factor | 252 |
| Risk aversion | 5.0 |
| Maximum single-name weight | 25% |
| Carbon budget ratio | Equal-weight exposure 的 70% |
| Transaction cost | 0 bps |
| Risk-free rate | 0% |

在调仓日 t，预期收益和协方差只使用：

```text
returns[t - 252 : t]
```

该窗口不包含日期 t 的实现收益。Carbon data 也只使用 available_date <= t 的记录。如果早期样本尚未覆盖全部股票，回测会等待，而不是使用未来披露填充历史。

调仓后，组合在两次调仓之间随资产收益自然漂移。每日组合收益计算为当日开端权重与资产收益的加权和。Turnover 使用调仓前漂移权重与新目标权重之间的一半绝对差之和。

代码支持简单的 turnover-based transaction cost 参数，但当前配置为 0 bps。回测没有模拟 bid-ask spread、slippage、tax、liquidity constraint 或 market impact。

## 6. Evaluation Metrics

### 6.1 Annualized return

项目使用累计复合增长计算年化收益：

```text
annualized return
= ending_wealth^(252 / number_of_observations) - 1
```

该指标便于比较不同组合在本样本中的历史增长速度，但高度依赖样本起止日期，不能作为未来收益预测。

### 6.2 Annualized volatility

```text
annualized volatility = daily_return_std * sqrt(252)
```

该指标衡量日收益波动的年化尺度。它没有完整描述尾部风险，也假设日波动可以按平方根时间规则年化。

### 6.3 Sharpe ratio

```text
Sharpe ratio
= (annualized return - risk_free_rate) / annualized volatility
```

当前无风险利率设为 0。Sharpe ratio 用于比较每单位历史波动对应的年化收益，但它对样本、收益分布和无风险利率假设敏感，也不能直接反映偏度和尾部风险。

### 6.4 Max drawdown

Drawdown 是当前累计价值相对于此前历史高点的下降：

```text
drawdown = current_wealth / historical_peak - 1
```

Max drawdown 是样本中最负的 drawdown。它可以描述历史路径中的深度损失，但只反映当前样本经历，不能证明未来 downside resilience。

### 6.5 Turnover

每次调仓的简化 turnover 为：

```text
turnover = 0.5 * sum(abs(new_weight - pre_rebalance_drifted_weight))
```

较高 turnover 通常意味着潜在交易成本和实施负担更高。但 turnover 本身不是实际成本，还需要结合 bid-ask spread、market impact、流动性和交易规模信息进行判断。

### 6.6 Average carbon exposure

该指标是各调仓日组合加权披露碳强度的平均值，单位为 tCO2e per USD million revenue。它用于检查碳约束是否改变组合的披露碳强度，但不能衡量 financed emissions、Scope 3、追加性或真实世界 impact。

### 6.7 Portfolio weights

项目保存每次调仓的目标权重，并计算其时间平均值。权重可以显示优化器如何在预期收益、协方差、单股权重上限和碳预算之间进行配置。

### 6.8 Cumulative value

累计价值从 1 开始，将每日收益复合：

```text
wealth(t) = product(1 + portfolio_return)
```

累计价值展示完整历史路径，但不包含当前配置下的实际交易成本。

### 6.9 Drawdown curve

Drawdown curve 显示每个时点相对历史高点的损失，有助于观察损失深度和恢复时间。该曲线不代表压力测试，也不能替代多市场状态或尾部情景分析。

## 7. 项目结果与图表分析

### 7.1 图 1：三种组合的累计价值

![图 1：三种组合的累计价值](outputs/figures/cumulative_returns.png)

图表说明： 图中展示 2020-09-01 至 2025-12-30 期间，1 单位初始价值在三种组合中的历史复合增长路径。

这张图显示了什么：

- 三种组合在样本期内最终累计价值均高于 1。
- 无碳约束的均值—方差组合最终累计价值约为 3.18，等权重组合约为 3.15。
- 碳约束下的均值—方差组合最终累计价值约为 2.86。
- 在本历史样本中，碳约束下的均值—方差组合在样本后半段总体低于另外两种组合，说明当前碳约束和权重变化伴随一定历史收益机会成本。

这张图不能说明什么：

- 不能说明无碳约束的均值—方差组合或等权重组合未来会继续领先。
- 不能证明碳约束导致了较低收益；结果也受到预期收益估计、股票池选择和样本市场行情影响。
- 不能被解释为 alpha、统计显著性，或经过成本调整后的可交易表现。

### 7.2 图 2：历史 Drawdown

![图 2：三种组合的历史回撤](outputs/figures/drawdowns.png)

图表说明： 图中展示每种组合累计价值相对于其此前历史高点的下降幅度。

这张图显示了什么：

- 等权重组合的样本最大回撤约为 -21.93%。
- 无碳约束的均值—方差组合的样本最大回撤约为 -26.42%。
- 碳约束下的均值—方差组合的样本最大回撤约为 -29.76%。
- 在 2022 年前后和 2025 年部分时期，碳约束组合经历了更深或更长的 drawdown。

这张图不能说明什么：

- 不能仅根据一个样本期断言某种组合具有或不具有长期 downside resilience。
- 不能区分回撤来自碳约束、行业配置、个股权重还是均值估计误差。
- 这不是独立的 stress test，也未覆盖所有可能的市场状态。

### 7.3 图 3：平均目标组合权重

![图 3：平均目标组合权重](outputs/figures/average_portfolio_weights.png)

图表说明： 图中比较 64 个调仓日中三种组合目标权重的时间平均值。

这张图显示了什么：

- 等权重组合对所有股票保持 10% 目标权重。
- 两种均值—方差组合平均更偏向 NVDA、WMT 和 JPM。在碳约束组合中，这三只股票的平均权重分别约为 19.0%、15.8% 和 15.3%。
- 碳约束将 COP 的平均权重从无碳约束的均值—方差组合中的约 9.8% 降至约 2.7%。
- 相对于无碳约束的均值—方差组合，碳约束组合略微提高了 AAPL、MSFT、WMT、GOOGL、V、NVDA、JPM 和 JNJ 等股票的平均配置，以重新分配从高碳强度股票减少的权重。
- Average weight HHI 为：等权重组合 0.100，无碳约束的均值—方差组合 0.231，碳约束下的均值—方差组合 0.224。两种优化组合均明显比等权重组合更集中。

这张图不能说明什么：

- 平均权重会隐藏不同调仓日的变化、边界解和短期集中情况。
- 不能把个别股票权重变化完全归因于 carbon intensity，因为预期收益和协方差也会共同影响优化结果。
- 当前代码没有系统计算 sector exposure，因此不能从图中得出行业中性结论。

### 7.4 图 4：平均披露碳强度

![图 4：平均披露碳强度比较](outputs/figures/carbon_exposure_comparison.png)

图表说明： 图中比较三种组合在调仓日的平均加权披露碳强度。

这张图显示了什么：

- 等权重组合平均碳强度为 65.45。
- 无碳约束的均值—方差组合平均碳强度为 77.68，高于等权重组合。
- 碳约束下的均值—方差组合平均碳强度为 34.02。
- 在当前构造下，碳约束使组合的加权披露碳强度低于等权重基准。
- 碳约束组合在不同调仓日的实际 exposure 与 equal-weight exposure 比率并不总是 70%；平均比率约为 49%。这说明部分时期无碳约束下的最优配置已经明显低于预算，或约束与其他优化条件共同产生了更低的碳暴露。

这张图不能说明什么：

- 不能说明组合促成了现实世界减排。
- 不能反映 Scope 3、financed emissions 或供应链排放。
- 不能证明较低碳强度会带来较高收益或较低风险。
- 不能消除不同公司披露口径和收入分母造成的可比性问题。

### 7.5 Turnover

当前项目没有单独保存 turnover 图，因此本报告不编造该图。Turnover 已由 performance_summary.csv 输出：

- 等权重组合：2.42%。
- 无碳约束的均值—方差组合：17.01%。
- 碳约束下的均值—方差组合：16.00%。

等权重组合的换手率较低，因为其目标权重固定为 10%，主要交易来自资产收益导致的权重漂移。两种均值—方差组合每月根据滚动估计重新求解，因此换手率明显更高。

当前 transaction cost 参数为 0 bps。如果实际实施成本随 turnover 增加，两种优化组合的净表现可能低于报告中的未扣成本结果。

### 7.6 核心 Metrics 汇总

| Portfolio | Annualized Return | Annualized Volatility | Sharpe Ratio | Max Drawdown | Avg Turnover | Avg Carbon Exposure |
|---|---|---|---|---|---|---|
| Equal-weight | 24.13% | 17.01% | 1.419 | -21.93% | 2.42% | 65.45 |
| Unconstrained MV | 24.35% | 21.47% | 1.134 | -26.42% | 17.01% | 77.68 |
| Carbon-constrained MV | 21.90% | 21.57% | 1.015 | -29.76% | 16.00% | 34.02 |

这些指标都是当前固定股票池、样本区间和参数设定下的历史描述统计，不包含统计置信区间，也不是未来表现预测。

## 8. 结果告诉了什么？

在本项目的简化设定下，碳约束降低了组合的平均加权披露碳强度。主要机制是降低 COP 等高碳强度股票的权重，并将权重重新分配给碳强度较低或中等的股票。

当前结果显示，降低碳强度并未伴随更高的历史风险调整收益。碳约束下的均值—方差组合在本历史样本中的年化收益和 Sharpe ratio 较低，波动率与无碳约束的均值—方差组合接近，而最大回撤更深。这提示我们，碳预算可能限制均值—方差优化器可选择的权重集合，并产生风险收益权衡；但当前设计不能把差异严格识别为碳约束的因果影响。

两种优化组合都比等权重组合更集中，且 turnover 更高。碳约束下的均值—方差组合的平均 HHI 略低于无碳约束的均值—方差组合，但仍远高于等权重组合。这里没有观察到“碳约束必然增加集中度”的简单关系，原因是约束也可能迫使权重从某个高碳资产分散到多个其他资产。

均值—方差优化对预期收益和协方差估计较为敏感。252 日历史均值可能包含较大估计误差，并推动权重向近期表现较强的股票集中。因此，当前结果同时反映了碳约束、历史估计误差、单股权重上限、股票池选择和样本市场状态。

## 9. 这个项目能作为 signal 或 alpha 吗？

目前不能。

碳约束是组合构建约束，不是收益预测信号。它规定组合允许承担的加权碳强度上限，但没有产生关于哪只股票未来收益更高的预测。

本项目没有：

- 证明 carbon exposure 能预测 future returns；
- 进行 factor validation；
- 计算 IC 或 rank IC；
- 构建 carbon long-short factor portfolio；
- 进行完整 out-of-sample validation；
- 建立完整 transaction cost、slippage 或 market impact 模型；
- 对 sector、market beta、size、value、momentum 和 quality 进行 neutralization；
- 对 carbon data 的披露差异进行机构级数据治理。

因此，本项目更适合称为：

carbon-aware portfolio construction prototype

或：

portfolio optimization with carbon constraint

而不适合称为 alpha research、trading strategy 或 validated signal。

## 10. 如果要发展成 signal / alpha research，还差什么？

1. 获取覆盖更广、口径统一且具有 point-in-time 历史版本的 company-level Scope 1、Scope 2 和 Scope 3 数据。
2. 定义具有潜在预测含义的变量，例如 carbon intensity change、emissions surprise、transition risk score 或 carbon disclosure improvement。
3. 检验 signal 与 future returns 的时间和横截面关系。
4. 进行 cross-sectional regression，控制已知公司特征。
5. 计算 IC、rank IC、稳定性和统计显著性。
6. 构建 long-short factor portfolio，检查收益是否集中于少数股票或行业。
7. 控制 sector、market beta、size、value、momentum 和 quality 等风险暴露。
8. 进行严格的 out-of-sample、walk-forward 和 rolling validation。
9. 加入 transaction costs、slippage、turnover penalty 和 market impact。
10. 分析 capacity、liquidity 和不同资金规模下的可实施性。
11. 进行不同 universe、时期、数据供应商、定义和 winsorization 方法的 robustness test。
12. 检查 signal decay、更新频率和披露滞后。
13. 建立清楚的经济逻辑，解释市场为何可能低估或错误定价该变量。

即使完成这些步骤，也只能逐步积累证据，不能预先假定存在 carbon-related alpha。

## 11. Limitations

- 股票池只有十只美国大型公司，无法代表完整投资 universe。
- 固定股票池基于当前可得公司，存在 survivorship bias 和 selection bias。
- 部分股票因公开碳披露覆盖不足被替换，产生 data-availability bias。
- Carbon data 来自真实公开披露，但组织边界、估算方法和 Scope 2 口径可能不同。
- 未纳入 Scope 3，因此不能代表公司的完整价值链排放。
- 排放和收入报告期可能存在时间差。
- Carbon disclosure 按年度更新且存在发布滞后，不是实时信息。
- Expected return 使用历史均值估计，噪声较大。
- Sample covariance matrix 可能不稳定。
- 仅使用简单 diagonal ridge，没有系统比较 covariance shrinkage 方法。
- 回测实际区间约为 2020 年 9 月至 2025 年 12 月，市场状态覆盖有限。
- 未建立正式 regime analysis 或 crisis stress test。
- 当前 transaction cost 设置为零。
- 未加入 bid-ask spread、slippage、tax 和 market impact。
- 未加入交易容量和流动性约束。
- 未系统计算或控制 sector exposure。
- 未控制 market beta 和 common risk factors。
- 未完成严格的 out-of-sample validation。
- 70% carbon threshold 是教学性参数，不是由政策、负债或客户 mandate 推导。
- Long-only、fully invested 和 25% weight cap 都是简化假设。
- Risk-free rate 设为零，会影响 Sharpe ratio。
- 优化结果对 lookback、risk aversion、carbon threshold 和 universe 敏感。
- 降低加权披露碳强度不等于真实世界减排或投资 impact。
- 历史结果不能解释为 alpha。
- 历史结果不能解释为已验证交易策略或投资建议。

## 12. Next Steps

### 12.1 短期改进

- 增加 turnover 时间序列图和 carbon exposure 时间序列图。
- 建立更严格的 carbon data validation、异常值和重述检查。
- 加入非零 transaction cost，并展示 gross 与 net performance。
- 补充正式 sector classification 和 sector exposure 分析。
- 比较不同 optimizer tolerance 和初始值下的稳定性。
- 增加约束 active status、边界权重和失败调仓的诊断输出。
- 运行并保存现有 carbon budget 与 risk-aversion sensitivity analysis。

### 12.2 中期改进

- 扩大股票池并使用 point-in-time universe。
- 纳入退市股票，减少 survivorship bias。
- 使用 Ledoit-Wolf 等 covariance shrinkage。
- 比较共同均值、Black-Litterman 或其他保守 expected return 方法。
- 加入 factor risk model 和 benchmark tracking constraint。
- 进行 rolling-window 和 walk-forward validation。
- 比较不同 carbon thresholds、lookback 和 rebalance frequencies。
- 进行 transaction-cost-adjusted robustness test。

### 12.3 长期研究方向

- 从 carbon constraint 扩展到可检验的 carbon-related signal。
- 研究 carbon-related variables 与 future returns 的关系。
- 建立具有历史版本控制的 climate / ESG data pipeline。
- 进行 forward test 和持续监控。
- 研究是否存在 carbon-related risk premium 或 mispricing。
- 区分风险补偿、监管冲击、技术转型和投资者偏好等可能机制。

## 13. 项目结论

本项目完成了一个可以运行、测试和解释的碳约束均值—方差组合优化原型。项目将公开 adjusted close、公开 Scope 1 和 location-based Scope 2 披露、SEC revenue、滚动参数估计和 constrained optimization 连接在同一研究流程中，并比较了等权重组合、无碳约束的均值—方差组合和碳约束下的均值—方差组合。

在当前样本和参数下，碳约束降低了组合的平均加权披露碳强度，主要表现为高碳强度资产平均权重下降。与此同时，碳约束组合在本历史样本中的年化收益、Sharpe ratio 和最大回撤弱于其他组合。这个观察说明碳约束可能带来权重重分配和风险收益权衡，但不能说明低碳组合普遍表现更差，也不能识别严格因果关系。

项目的主要研究价值是展示碳预算如何以线性约束进入组合构建，以及如何用 point-in-time 信息、调仓权重、turnover、drawdown 和 carbon exposure 对其影响进行透明检查。它不能说明 carbon intensity 是 alpha signal，不能证明真实减排效果，也不能被视为经过充分验证的实盘策略。

下一步最重要的改进是扩大并治理 point-in-time carbon dataset，引入更稳健的 expected return 和 covariance estimation，加入实际交易成本与风险因子控制，并开展严格的 out-of-sample robustness analysis。

## 14. Appendix

### 14.1 主要数据字段

| 字段 | 含义 |
|---|---|
| ticker | 股票代码 |
| reporting_year | 排放记录对应报告年度 |
| available_date | 排放和收入信息均已公开的最早日期 |
| scope1_tco2e | 公司直接排放 |
| scope2_location_tco2e | Location-based Scope 2 排放 |
| revenue_usd_mn | 年度收入，单位为 USD million |
| carbon_intensity_tco2e_per_usd_mn | Scope 1 + Scope 2 除以收入 |
| period_end_gap_days | 排放期末和收入期末之间的天数差 |

### 14.2 核心公式

简单收益率：

```text
return(i,t) = price(i,t) / price(i,t-1) - 1
```

组合日收益率：

```text
portfolio_return(t) = sum(weight(i,t) * return(i,t))
```

Mean-variance objective：

```text
minimize:
0.5 * risk_aversion * weight' * covariance * weight
- expected_return' * weight
```

基本约束：

```text
sum(weights) = 1
0 <= weight(i) <= 0.25
```

碳强度：

```text
carbon_intensity(i)
= (scope1(i) + scope2_location_based(i)) / revenue_usd_mn(i)
```

组合碳暴露：

```text
portfolio_carbon_exposure
= sum(weight(i) * carbon_intensity(i))
```

碳预算：

```text
portfolio_carbon_exposure
<= 0.70 * equal_weight_carbon_exposure
```

Turnover：

```text
turnover
= 0.5 * sum(abs(new_target_weight - pre_rebalance_drifted_weight))
```

### 14.3 主要代码文件

| 文件 | 作用 |
|---|---|
| run_prototype.py | 读取配置、运行完整流程并保存结果 |
| config/settings.yaml | 股票池、日期、优化和回测参数 |
| src/carbon_portfolio/data.py | 价格下载、模拟 fallback、验证和收益率计算 |
| src/carbon_portfolio/carbon.py | 碳强度读取、point-in-time 对齐和组合暴露 |
| src/carbon_portfolio/optimization.py | Equal-weight 和 constrained mean-variance optimization |
| src/carbon_portfolio/backtest.py | 月度滚动回测、权重漂移、换手率和诊断 |
| src/carbon_portfolio/metrics.py | 收益、波动率、Sharpe ratio、drawdown 和集中度 |
| src/carbon_portfolio/visualization.py | 项目图表 |
| src/carbon_portfolio/sensitivity.py | Carbon budget 和 risk-aversion sensitivity |
| tests/ | 数据、约束、回测时序和指标测试 |

### 14.4 图表文件路径

outputs/figures/cumulative_returns.png
outputs/figures/drawdowns.png
outputs/figures/average_portfolio_weights.png
outputs/figures/carbon_exposure_comparison.png

### 14.5 结果表路径

outputs/tables/performance_summary.csv
outputs/tables/portfolio_returns.csv
outputs/tables/rebalance_diagnostics.csv
outputs/tables/equal_weight_weights.csv
outputs/tables/unconstrained_mv_weights.csv
outputs/tables/carbon_constrained_mv_weights.csv
outputs/tables/data_source.txt

### 14.6 数据来源说明

- Price data：Yahoo Finance，通过 yfinance 下载 adjusted close。
- Emissions data：Climate Data Utility 汇总的 CDP disclosure。
- Revenue data：SEC Companyfacts 10-K。
- 项目当前使用的 source record：yfinance_adjusted_close。
