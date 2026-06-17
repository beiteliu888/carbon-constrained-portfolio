# Prompt Log

这个文件只记录本项目中对未来有复用价值的 prompt 迭代，不保存完整聊天记录。

## 2026-06-17 - 历史项目补档

- 使用 prompt：用户要求将现有 Carbon Constrained Portfolio 项目接入 Developer 新工作流。
- 目标：
  - 补齐项目 prompt 资产和工作流目录。
  - 根据现有文档反推 `prompts/01_原始想法.md` 与 `prompts/03_Codex执行Brief.md`。
  - 明确记录这不是从原始 prompt 开始的新项目。
- 效果：
  - 已将原始想法和 Codex Brief 以“根据现有项目文档反推”的方式补档。
  - 保留历史项目定位：learning-oriented、exploratory、not alpha research。
- 造成返工的模糊点：
  - 原项目早期 prompt 没有按新 workflow 保存，因此无法还原逐字原始 prompt。
  - 只能依据 README、PROJECT_REPORT、CODE_NOTES 和专题学习笔记进行反推。
- 下次默认改进：
  - 新项目启动时先保存 `prompts/01_原始想法.md`。
  - GPT 讨论后立即保存 `prompts/03_Codex执行Brief.md`。
  - 重大研究方向变化前先写 Change Request。
- 是否写入全局复利日志：否；这是项目局部补档，暂不沉淀为跨项目经验。

## 2026-06-17 - 补齐完整 prompt 链路

- 使用 prompt：用户要求项目停留于当前版本，并补齐前次提到的第 2、3 点。
- 目标：
  - 补齐 `prompts/02_GPT研究讨论Prompt.md`。
  - 补齐 `prompts/04_Codex实施Prompt.md`。
  - 更新全局项目索引。
- 效果：
  - 项目现已具备 `01_原始想法`、`02_GPT研究讨论Prompt`、`03_Codex执行Brief`、`04_Codex实施Prompt` 四段 prompt 资产。
  - 所有补档文件均标注为“根据现有项目文档反推”，避免误认为原始逐字 prompt。
- 造成返工的模糊点：无；本次是历史项目补档。
- 下次默认改进：项目启动时立即保存完整 prompt 链路，减少后续反推。
- 是否写入全局复利日志：否。

## 2026-06-17 - 项目收尾复盘

- 使用 prompt：用户要求“现在可以进行复盘”。
- 目标：
  - 总结项目 001 的收尾经验。
  - 区分项目局部记录和全局可复用经验。
  - 更新全局复利日志，但避免写流水账。
- 效果：
  - 项目内记录了 v1 收尾状态、GitHub 推送、workflow migration 和用户偏好。
  - 全局复利日志只保留可复用做法：历史项目补档标注反推、GitHub 认证处理、完成后同步状态。
- 造成返工的模糊点：
  - README 在 workflow migration 后仍保留 `active` 和未跟踪文件提示，需要在收尾时修正。
- 下次默认改进：
  - 项目完成后检查 README、项目索引、Git 状态和 remote 是否一致。
  - 若 push 被认证挡住，优先判断是 `gh`、SSH key 还是 PAT 问题，再给用户最短路径。
- 是否写入全局复利日志：是，已写入“Carbon Constrained Portfolio 收尾复盘”。
