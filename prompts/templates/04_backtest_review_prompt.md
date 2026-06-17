# 04_backtest_review_prompt

用途：让 GPT 或 Codex 专门审查量化回测结果和偏差。

```text
请从量化研究审查角度 review 这个项目/结果。重点不是优化代码，而是判断研究结果是否可信。

请检查：
1. 因子定义是否清楚，是否可能泄露未来信息。
2. signal date、rebalance date、execution date、return window 是否对齐。
3. 是否存在 lookahead bias、survivorship bias、selection bias、data snooping。
4. 缺失数据、停牌、退市、极端值处理是否合理。
5. benchmark、调仓频率、交易成本、换手率是否足以支持结论。
6. 指标和图表是否能解释收益来源和风险。
7. 哪些结果可以相信，哪些需要二次实验。

请输出：
- 主要风险
- 必须修正的问题
- 建议增加的稳健性测试
- 下一版 Codex Brief
```
