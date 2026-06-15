# Carbon-Constrained Portfolio Optimization Prototype

> 碳约束下的组合优化初步探索

这是一个 **exploratory、early-stage、learning-oriented prototype**。项目用于学习
mean-variance portfolio optimization、risk-return trade-off，以及简化的 carbon
budget constraint 如何改变组合权重。它不是成熟交易策略，不提供投资建议，也不构成
alpha、实际减排效果或 downside resilience 的证据。

## 研究问题

在相同资产池和调仓日期下，比较：

1. Equal-weight portfolio
2. Unconstrained mean-variance portfolio
3. Carbon-constrained mean-variance portfolio

观察加入 carbon budget 后，组合权重、公开披露口径下的 carbon intensity、历史风险收益指标、
drawdown、turnover 和集中度如何变化。

## 数据边界

### 真实数据

- 优先通过 `yfinance` 从公开来源下载历史 adjusted close prices。
- 由价格计算的历史简单收益率。
- 由回测收益序列计算的波动率、回撤和其他描述性指标。

公开数据源可能修改历史值、调整口径或出现缺失。缓存文件只是为了提高可复现性，并不
代表数据经过机构级验证。

如果 `yfinance` 因网络、接口或 ticker 问题失败，程序会生成
`data/raw/SIMULATED_adjusted_close.csv`。控制台和
`outputs/tables/data_source.txt` 会明确显示 `SIMULATED_FALLBACK`。模拟价格只用于
教学、测试和检查程序流程，绝不能用于真实投资或气候结论，也不会覆盖真实价格缓存。

### Carbon intensity 数据

- `data/carbon_intensity.csv` 使用公开披露数据，不再使用人为设定的 synthetic score。
- 分子来自 Climate Data Utility 汇总的 CDP 披露：
  `Scope 1 + location-based Scope 2`，单位为 tCO2e。
- 分母来自 SEC Companyfacts 的年度 10-K revenue，单位转换为 USD million。
- 教学用碳强度定义为：
  `(Scope 1 + location-based Scope 2) / revenue_usd_mn`。
- `available_date` 取碳披露日期和对应收入 10-K filing date 中较晚者。回测只使用
  调仓日之前已经公开的数据，减少碳数据上的 look-ahead bias。
- `period_end_gap_days` 记录碳披露期末与收入期末的差距。多数记录期末接近，但并非
  完全一致，例如部分 WMT 和 V 记录存在时间错位。

这些数据来自真实公开披露，但不代表机构级、审计一致或完全可比的数据集。公司组织
边界、Scope 2 方法、估算方法、重述政策和财年可能不同；本版本也没有纳入 Scope 3。

### 其他简化假设

- Carbon constraint 只用于演示线性约束
  `weights @ carbon_intensity <= carbon_budget`。
- 历史样本均值被用作 expected return estimate，但不是可靠的收益预测。
- 历史样本 covariance matrix 存在显著估计误差。
- 固定资产池为事后选择，存在 selection bias 和 survivorship bias。
- 默认 long-only、fully invested，不使用杠杆、做空或现金。
- 默认交易成本为零；可设置简单的 turnover-based cost，但未模拟滑点、税费、
  bid-ask spread、流动性和市场冲击。

## 默认设置

默认参数位于 `config/settings.yaml`：

- 资产池：`AAPL, MSFT, WMT, GOOGL, V, NVDA, JPM, COP, JNJ, PG`
- 样本期：2018-01-01 至 2025-12-31
- 估计窗口：252 个交易日
- 调仓频率：月度
- 单一资产最高权重：25%
- 风险厌恶参数：5
- Carbon budget：当期 equal-weight carbon intensity 的 70%

这些只是教学默认值，不是经过最优化选择的策略参数。调整参数后应报告完整的敏感性
结果，不能只展示表现最好的组合。

WMT、V 和 COP 替换了原示例中披露历史覆盖不足的 AMZN、META 和 XOM。这个选择是
为了获得较连续的公开数据，不代表投资观点，也会带来 data-availability selection bias。

## 方法

优化目标为：

```text
minimize  0.5 * risk_aversion * w'Σw - μ'w
```

共同约束：

```text
sum(w) = 1
0 <= w_i <= max_weight
```

碳约束组合额外满足：

```text
w'carbon_intensity <= carbon_budget
```

滚动回测在日期 `t` 估计参数时，只使用 `t` 之前的收益率，以及 `available_date <= t`
的最新碳披露。日期 `t` 的实现收益不进入该次估计，以减少 look-ahead bias。若当时尚未
覆盖全部股票，程序会等待而不是使用未来披露。组合在两次月度调仓之间随资产收益自然漂移；
turnover 使用调仓前漂移权重与新目标权重计算。优化失败、不可行预算或约束违反会
显式抛出错误，而不是静默替换结果。

## 安装与运行

### 在 PyCharm 中运行（推荐给初学者）

1. 在 PyCharm 选择 **Open**，打开：
   `/Users/max/Developer/carbon-constrained-portfolio`
2. 打开 **Settings > Project > Python Interpreter**。
3. 选择 **Add Interpreter > Add Local Interpreter > Virtualenv**，在项目内创建
   `.venv`，Base interpreter 选择 `/opt/miniconda3/bin/python3`（Python 3.12）。
4. 打开 PyCharm 下方的 **Terminal**，运行：

```bash
python -m pip install -r requirements.txt
```

5. 在左侧找到 `run_prototype.py`，右键选择 **Run 'run_prototype'**。

第一次运行需要联网下载公开价格。之后默认读取
`data/raw/adjusted_close.csv` 缓存。运行结果会出现在：

```text
outputs/tables/    指标、收益率、诊断和权重 CSV
outputs/figures/   累计价值、drawdown、平均权重与碳暴露图
```

入口脚本会自动加入 `src` 路径，因此在 PyCharm 中直接运行时不需要手工设置
`PYTHONPATH`。Notebook 仍可用于逐步学习和解释。

第三个 Notebook 还会运行预先声明的参数网格，比较不同 carbon budget 与
risk-aversion。该分析用于展示模型敏感性，不用于挑选历史表现最好的参数。

### 在 Terminal 中运行

```bash
cd /Users/max/Developer/carbon-constrained-portfolio
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_prototype.py
```

需要重新下载数据时：

```bash
python run_prototype.py --refresh
```

启动 Notebook：

```bash
jupyter notebook
```

建议按顺序运行：

1. `notebooks/01_data_exploration.ipynb`
2. `notebooks/02_portfolio_optimization.ipynb`
3. `notebooks/03_backtest_and_evaluation.ipynb`

运行测试：

```bash
pytest
```

## 输出内容

- `performance_summary.csv`：annualized return、annualized volatility、
  Sharpe ratio、max drawdown、average turnover 和 average carbon exposure。
- `portfolio_returns.csv`：三种组合的历史日收益率。
- `rebalance_diagnostics.csv`：估计窗口、carbon budget、carbon exposure 和
  调仓 turnover；使用年度面板时还记录所用披露年份范围。
- `*_weights.csv`：每次月度调仓的目标权重。
- `cumulative_returns.png`：三种组合的累计价值。
- `drawdowns.png`：历史回撤。
- `average_portfolio_weights.png`：平均目标权重。
- `carbon_exposure_comparison.png`：平均加权披露碳强度。

## 常见错误

- `ModuleNotFoundError`：确认 PyCharm interpreter 是项目内的 `.venv/bin/python`。
- `No module named yfinance/scipy`：在 PyCharm Terminal 运行
  `python -m pip install -r requirements.txt`。
- 下载失败：程序会自动切换到 `SIMULATED_FALLBACK`；检查网络后可用
  `python run_prototype.py --refresh` 重试真实数据。
- `OptimizationError: infeasible`：carbon budget 太低，或 weight cap 使低碳资产
  无法承担全部权重。
- Matplotlib 字体或缓存警告：通常不影响结果，可确认用户目录具有写权限。

## 项目结构

```text
config/       明确记录实验参数
data/         公开价格缓存与公开披露 carbon intensity 面板
notebooks/    教学解释、单期优化和滚动回测
src/          可复用并可测试的 Python 模块
tests/        约束、指标和 look-ahead 检查
outputs/      可选的图表与表格输出
```

## 必须谨慎解释的结果

- 更高的历史收益或 Sharpe ratio 不是 alpha 证据。
- 单一样本期的较小 drawdown 不能证明 downside resilience。
- 降低组合加权披露碳强度不等于真实减排、资本追加性或现实世界 impact。
- Mean-variance 权重可能对 expected returns、covariance、窗口和约束高度敏感。
- Weight cap 会影响最低可实现 carbon exposure，也可能造成边界解。
- Turnover 只是调仓幅度指标；没有完整交易成本模型时不能等同于可交易性。
- 该 simple backtest 不包含完整的数据治理、公司行动验证、执行、风控、监控或
  production controls。
- Carbon 数据按年度更新且通常滞后发布，不能被理解为每日实时暴露。
- 公司组织边界、Scope 2 计算方法、财年和重述政策可能不同，横截面可比性有限。
- 本版本未纳入 Scope 3，也未独立验证披露或第三方 assurance。
- 历史均值作为 expected return estimate 很不稳定，可能导致边界权重。
- 当前股票池只有十只美国大盘股，不能代表完整市场。
- 使用 simulated fallback 时，任何绩效数字都只说明代码可以运行。

## 下一步改进

1. 建立更严格的数据治理流程，处理组织边界、重述、assurance 和异常值。
2. 研究 Scope 3 覆盖、估计误差和供应链 double counting。
3. 加入 covariance shrinkage，并比较是否降低权重不稳定性。
4. 使用更保守的 expected return 假设，例如共同均值或 Black-Litterman。
5. 加入 transaction cost、slippage、流动性和 benchmark tracking constraints。
6. 使用 point-in-time universe 和退市股票降低 survivorship bias。

## 可向 Senior Quant 使用的简短说明

这是一个教学型组合构建 prototype，用于隔离 carbon constraint 对 mean-variance
权重和历史风险指标的影响。价格来自公开历史市场数据；carbon intensity 使用 CDU/CDP
披露的 Scope 1 与 location-based Scope 2，并以 SEC 10-K revenue 标准化。收益与碳数据
都按历史可得日期进入回测，以减少明显的 look-ahead bias，但披露口径可比性、固定资产池、
参数估计误差和简化交易成本仍限制结论。结果只能用于理解机制，不能解释为 alpha、投资
建议、真实减排效果或经过验证的实盘策略。
