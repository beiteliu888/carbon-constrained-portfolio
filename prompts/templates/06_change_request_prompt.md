# 06_change_request_prompt

用途：项目进行中发现问题、想改研究逻辑或整体框架时，让 Codex 先分类并草拟 Change Request，不直接改代码。

```text
我在项目中发现一个问题。请先不要改代码。

请读取项目 README、AGENTS.md、notes/project_log.md、notes/prompt_log.md、notes/change_log.md 和当前相关输出，帮我判断这是哪类问题：
1. 实现 bug
2. 研究逻辑问题
3. 架构框架问题
4. prompt/沟通问题

请输出一个 Change Request 草稿，包含：
- 发现的问题
- 变更类型
- 影响范围
- 建议处理方式
- 是否需要先回 GPT 讨论
- 是否需要保留 v1 并新增 v2 输出
- Codex 后续执行建议

如果你判断这是研究逻辑或架构问题，请只输出计划和 Change Request，不要修改代码。
```
