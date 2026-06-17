# Project Log

## 2026-06-17

- 进展：将历史项目 001 接入新的 `/Users/max/Developer` 工作流。
- 动作：
  - 补齐 `prompts/`、`prompts/templates/`、`notes/`、`docs/change_requests/`。
  - 根据现有项目文档反推并保存 `prompts/01_原始想法.md`。
  - 根据现有 README、项目报告和学习笔记反推并保存 `prompts/03_Codex执行Brief.md`。
  - 创建项目级 `AGENTS.md`，补充项目运行、测试、数据和输出保护规则。
  - 更新 `README.md`，加入项目状态、Prompt 资产位置、变更管理方式和下一步建议。
- 决策：
  - 本次只做 workflow migration 和项目档案整理。
  - 不修改研究代码，不运行回测，不覆盖现有 `outputs/`。
  - 保留未跟踪文件 `NETWORKING_TALKING_POINTS.md`。
- 下一步：确认是否将 `NETWORKING_TALKING_POINTS.md` 纳入版本管理；若继续研究，优先做 transaction costs、sector exposure diagnostics 和 covariance shrinkage。

## 2026-06-17 - 项目停留在当前 v1

- 进展：用户确认本项目停留于当前版本，并要求将所有项目更改上传到 GitHub。
- 动作：
  - 补齐 `prompts/02_GPT研究讨论Prompt.md`。
  - 补齐 `prompts/04_Codex实施Prompt.md`。
  - 更新 Developer 全局 `02_项目索引.md`，将项目 001 标记为 `completed`，并写入 GitHub 地址。
  - 将 `NETWORKING_TALKING_POINTS.md` 纳入本次项目提交范围。
- 决策：
  - 当前 v1 不继续新增研究功能。
  - 后续如需重启研究，应先写 Change Request，而不是直接覆盖当前输出。
- 下一步：提交并推送 workflow migration、prompt 补档和 networking talking points。

## 2026-06-17 - 项目收尾复盘

- 进展：项目 001 已完成当前阶段收尾；本地提交已推送至 GitHub，项目状态在 Developer 索引中标记为 `completed`。
- 项目结果：
  - v1 prototype 保留为 learning-oriented / exploratory portfolio construction project。
  - 研究代码、数据和 outputs 未在 workflow migration 中被修改或覆盖。
  - `NETWORKING_TALKING_POINTS.md`、完整 prompt 链路、项目级 `AGENTS.md`、change request 模板和日志均已纳入项目。
- 可复刻做法：
  - 历史项目补档时明确写“根据现有项目文档反推”。
  - 停止开发时先确认项目状态，再更新 README、项目索引和日志。
  - 对量化项目保留谨慎表述：prototype、not alpha、not production strategy。
- 踩坑与修正：
  - 本机缺少 `gh` 和 `brew`，GitHub HTTPS push 初次认证被挡住。
  - 通过 GitHub Personal Access Token 完成认证后，项目成功推送。
- 用户偏好：
  - 达到学习目标后，项目可以明确停在当前版本，不强行扩展功能。
  - 收尾复盘要短、清楚、可复用，不写流水账。
- 下一步：无立即开发任务；未来若重启 v2，先写 Change Request。
