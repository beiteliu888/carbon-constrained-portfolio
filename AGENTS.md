# AGENTS.md

适用范围：本项目目录 `/Users/max/Developer/10_active/001_carbon-constrained-portfolio`。

本文件是项目级工作规则。若与 `/Users/max/Developer/AGENTS.md` 冲突，以母目录安全规则和复盘规则为准。

## 开工前必读

1. 先读项目 `README.md`，确认项目定位、运行方式、数据边界和限制。
2. 再读 `/Users/max/Developer/00_全局控制台.md` 与 `/Users/max/Developer/03_prompt_系统.md`，确认 Developer 工作流。
3. 如果是接续任务，查看 `/Users/max/Developer/02_项目索引.md` 中项目 001 的最近进展和下一步。
4. 如果任务涉及研究想法、prompt、Codex Brief、变更请求或复盘，读取项目 `prompts/` 与 `notes/`。

## 项目定位

- 这是 learning-oriented / exploratory portfolio construction prototype。
- 不要把项目描述成 alpha research、投资建议、production-level strategy 或真实世界减排证明。
- 项目目标是理解 carbon budget constraint 如何进入 mean-variance portfolio optimization，并观察其对 weights、carbon exposure、risk-return profile、drawdown 和 turnover 的影响。

## 常用命令

在项目根目录运行：

```bash
python -m pip install -r requirements.txt
python run_prototype.py
pytest
```

Notebook 建议按顺序运行：

```text
notebooks/01_data_exploration.ipynb
notebooks/02_portfolio_optimization.ipynb
notebooks/03_backtest_and_evaluation.ipynb
```

## 测试方式

- 修改研究代码后运行 `pytest`。
- 如果修改回测、优化、数据读取或 metrics，优先检查对应测试：
  - `tests/test_data.py`
  - `tests/test_carbon.py`
  - `tests/test_optimization.py`
  - `tests/test_backtest.py`
  - `tests/test_metrics.py`
  - `tests/test_sensitivity.py`
- 本次 workflow migration 不要求运行测试，因为不修改研究代码。

## 数据注意事项

- 价格数据优先来自 yfinance adjusted close；若使用 simulated fallback，必须明确标注为教学/测试用途。
- `data/carbon_intensity.csv` 使用公开披露构造的 carbon intensity，不是机构级、审计一致或完全可比的数据集。
- Carbon intensity 口径为 `Scope 1 + location-based Scope 2` 除以 SEC 10-K revenue；当前不包含 Scope 3。
- 回测中的 carbon data 必须使用 `available_date <= rebalance date` 的 point-in-time 逻辑。
- 不要把 average carbon exposure 下降解释为真实世界减排或 impact。

## 输出保护

- 不要覆盖现有 `outputs/`，除非用户明确要求重新运行并接受覆盖。
- 重大研究逻辑、数据口径或回测框架变更，先写 `docs/change_requests/CR-XXX_short-title.md`。
- 如果需要生成新实验输出，优先使用版本化目录，例如 `outputs/v2/`，不要直接替换 v1 结果。
- 当前存在未跟踪文件 `NETWORKING_TALKING_POINTS.md`，不要删除、移动或忽略它。

## Prompt 与变更管理

- 原始想法与反推 brief 保存在 `prompts/`。
- Prompt 模板保存在 `prompts/templates/`。
- Prompt 迭代记录在 `notes/prompt_log.md`。
- 项目变更记录在 `notes/change_log.md`。
- 项目进展记录在 `notes/project_log.md`。
- 重大变更请求保存在 `docs/change_requests/`。

