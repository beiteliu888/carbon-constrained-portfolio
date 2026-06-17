# 02_research_to_codex_brief

用途：让 GPT 把理念讨论结果压缩成 Codex 可以执行的 brief。

```text
请把上面的研究讨论整理成一份 Codex Brief。不要写代码。

Codex Brief 需要让 Codex 能直接创建项目、实现初版研究原型、运行验证并生成报告。

请按以下结构输出：

# Codex Brief: 【项目名】

## 研究目标

## 因子假设

## 数据需求
- 股票池或资产范围：
- 时间范围：
- 数据频率：
- 必需字段：
- 可选字段：

## 初版因子定义

## 回测设计
- 调仓频率：
- signal date：
- rebalance date：
- execution date：
- return window：
- 组合构建方式：
- benchmark：

## 主要偏差检查

## 交付物

## 暂不纳入范围

## 给 Codex 的执行要求
```
