# 03_codex_implementation_prompt

用途：把 Codex Brief 交给 Codex，让 Codex 按 Developer 规则创建或推进项目。

```text
请先读取 `/Users/max/Developer/AGENTS.md`、`00_全局控制台.md`、`02_项目索引.md` 和 `03_prompt_系统.md`。

基于下面的 Codex Brief，在 Developer 下创建或推进项目。

要求：
- 若是新项目，使用下一个正式项目编号，创建 `10_active/NNN_project-slug/`。
- 从 `20_templates/default_project/` 复制项目模板。
- 保存我的原始想法、GPT 研究 prompt、Codex Brief 和本实施 prompt 到项目 `prompts/`。
- 更新项目 `README.md`、`AGENTS.md`、`notes/project_log.md`、`notes/prompt_log.md`。
- 实现初版可运行原型，并保留清晰的数据格式说明。
- 加入必要测试或验证脚本。
- 生成输出表格/图表/报告时写入 `outputs/` 或 `docs/`。
- 更新 `/Users/max/Developer/02_项目索引.md`。
- 如果发现 brief 缺少关键假设，先指出并提出默认假设，不要盲目实现。

<Codex Brief>
【粘贴 Codex Brief】
</Codex Brief>
```
