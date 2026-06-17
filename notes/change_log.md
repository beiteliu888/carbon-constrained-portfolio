# Change Log

记录项目中途的重要变更。小 bug、研究逻辑调整、架构调整都可以记录，但只有跨项目可复用的经验才写入全局复利日志。

## 2026-06-17 - Workflow migration

- 变更类型：架构框架 / prompt 沟通
- 发现的问题：
  - 项目是在 Developer 新工作流完善前启动的，缺少项目级 `AGENTS.md`、prompt 资产目录、prompt log、change log 和 change request 目录。
  - 原始 prompt 与 Codex Brief 未按新标准保存。
- 决策：
  - 只做 workflow 接入和项目档案整理。
  - 根据现有项目文档反推 `prompts/01_原始想法.md` 与 `prompts/03_Codex执行Brief.md`，并明确标注“根据现有项目文档反推”。
  - 不修改研究代码，不跑重构，不覆盖已有 outputs。
- 影响范围：
  - 代码：无。
  - 数据：无。
  - 输出：无。
  - 报告：README 增加工作流状态与变更管理说明。
  - prompt：新增 prompt 资产与模板目录。
- 输出版本：v1 文档补档；研究输出版本不变。
- 是否需要 GPT 讨论：否。
- 是否写入全局复利日志：否。

## 2026-06-17 - Complete prompt archive and close v1

- 变更类型：prompt 沟通 / 项目状态
- 发现的问题：
  - 初次 workflow migration 只补齐了 `01_原始想法` 和 `03_Codex执行Brief`。
  - 项目索引仍显示需要确认 `NETWORKING_TALKING_POINTS.md` 是否纳入项目。
- 决策：
  - 补齐 `02_GPT研究讨论Prompt` 和 `04_Codex实施Prompt`。
  - 将 `NETWORKING_TALKING_POINTS.md` 纳入项目提交范围。
  - 全局项目索引将项目 001 标记为 `completed`，表示当前 v1 暂停继续开发。
- 影响范围：
  - 代码：无。
  - 数据：无。
  - 输出：无。
  - 报告：无新增研究结论。
  - prompt：补齐完整 prompt 链路。
- 输出版本：v1 文档补档完成。
- 是否需要 GPT 讨论：否。
- 是否写入全局复利日志：否。
