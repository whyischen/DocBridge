# OpenClaw skill

官方文档：https://docs.openclaw.ai/tools/skills#skills

## 1. 什么是 Skill？

Skill 本质上是一个独立的文件夹，核心是一个 SKILL.md 文件。它通过自然语言指令和简单的 YAML 配置，教会大语言模型（LLM）在什么场景下该如何使用工具、执行特定工作流，而无需编写繁琐的代码逻辑。

## 如何定义 SKILL.md

由顶部的 YAML 元数据 (Frontmatter) 和下方的 Markdown 指令 (Body) 组成。
```markdown
---
name: hello_world
description: 当用户需要打招呼、问候或测试时调用此技能。
emoji: 👋
---
# Hello World Skill

当用户请求问候时，请使用内置的 `bash` 或 `echo` 工具输出以下内容：
"你好！这是来自你自定义 OpenClaw 技能的问候！"

## 注意事项
- 保持回答简短、热情。
- 只有在用户明确要求问候时才触发。
```


