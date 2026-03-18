# OpenClaw 集成指南 (Skill 模式)

ContextBridge 可以作为原生 Skill 无缝集成到 OpenClaw 中。通过提供一个简单的 `SKILL.md` 文件，你可以赋予 OpenClaw 智能体瞬间读取和搜索本地文档的能力。

## 架构设计：为什么选择 SKILL.md？

OpenClaw 是一个强大的多渠道 AI 网关，它使用独特的基于 Prompt 的 Skill 系统。与编写复杂的 Node.js 或 Python 插件不同，OpenClaw 允许你使用简单的 Markdown 文件 (`SKILL.md`) 来定义 Skill。

1. **零代码集成**：你不需要编写任何集成代码。`SKILL.md` 文件只是告诉 AI *如何* 使用其现有的工具（如 `exec` 或 `bash`）与 ContextBridge 对话。
2. **原生兼容性**：这种方法利用了 OpenClaw 内置的工具执行能力，确保了最大的兼容性和稳定性。
3. **Token 极致优化**：AI 永远不会将整篇文档塞入 Prompt。它通过 API 接口只获取最相关的文本块（Chunks），极大节省 Token 并提高回答准确率。

---

## 第一步：安装 ContextBridge

### 重要：清理旧版本

如果你之前安装过 ContextBridge，用户目录中的旧版本可能会覆盖新版本，导致功能异常（如国际化不生效）。请先执行清理：

```bash
# 删除用户目录中的旧版本
rm -f ~/Library/Python/*/lib/python/site-packages/cbridge.py
rm -rf ~/Library/Python/*/lib/python/site-packages/cbridge_agent*
```

### 安装方式（三选一）

#### 方式一：pip 安装（推荐）

```bash
pip install cbridge-agent
```

#### 方式二：Homebrew 安装

```bash
brew install cbridge-agent
```

#### 方式三：源码安装

```bash
git clone https://github.com/whyischen/context-bridge.git
cd context-bridge
pip install -e .
```

### 语言配置

ContextBridge 支持中英文界面切换：

```bash
# 切换为中文
cbridge lang zh

# 切换为英文
cbridge lang en
```

---

## 第二步：初始化与配置

### 初始化工作区

```bash
cbridge init
```

跟随交互式向导完成工作区配置（默认路径为 `~/ContextBridge_Workspace`）。

### 添加监控目录

告诉 ContextBridge 你的文档存放在哪里：

```bash
cbridge watch add /你的/文档/路径
```

### 性能优化配置（低性能设备）

如果你的设备性能有限，可以通过环境变量调整配置：

```bash
# 减少同时处理的文件数量
export CB_MAX_CONCURRENT_FILES=2

# 使用更小的向量批次
export CB_EMBEDDING_BATCH_SIZE=4

# 禁用实时监听（改为手动索引）
export CB_DISABLE_WATCHER=true
```

### 排除目录配置

某些目录（如 `node_modules`、`.git`）不应该被索引。在 `cbridge init` 时配置排除目录，或手动编辑配置文件：

```yaml
# ~/.config/cbridge/config.yaml
exclude_patterns:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/__pycache__/**"
  - "**/*.tmp"
  - "**/dist/**"
  - "**/build/**"
```

---

## 第三步：启动 API 服务

在接入 OpenClaw 之前，你需要让 ContextBridge 在后台运行并提供 API 服务。

```bash
# 启动 API 服务（默认绑定 127.0.0.1:9790）
cbridge serve
```

或者同时启动监控服务和 API 服务：

```bash
# 启动完整服务（监控 + API）
cbridge start
```

启动后，ContextBridge 会同时做两件事：
1. 启动 FastAPI 服务器，监听 `http://127.0.0.1:9790`。
2. 在后台启动 Smart Folder Watcher，实时监控你的本地文件夹变更。

你可以通过访问 `http://127.0.0.1:9790/docs` 查看完整的 API 文档（Swagger UI）。

---

## 第四步：创建 OpenClaw Skill

要集成 ContextBridge，你需要在 OpenClaw 工作区中创建一个新的 Skill。

1. 导航到你的 OpenClaw skills 目录（例如 `~/.openclaw/skills/` 或 `<workspace>/skills/`）。
2. 创建一个名为 `contextbridge` 的新文件夹。
3. 在此文件夹内，创建一个名为 `SKILL.md` 的文件。

### 完整的 SKILL.md 示例

```markdown
---
name: local-context-bridge
description: Search and retrieve information from the user's local documents, knowledge bases, policies, and historical data.
metadata: { "openclaw": { "emoji": "🌉", "requires": { "bins": ["curl"] } } }
---

# Local ContextBridge Knowledge Base

This skill allows OpenClaw to search and retrieve information from your local documents (PDF, Word, Excel, Markdown, etc.) using the ContextBridge API.

## 🛠️ PREREQUISITES & INSTALLATION

If you haven't installed the ContextBridge software on your machine yet, follow these steps first:

### 1. Install ContextBridge
Open your terminal and run:
```bash
pip install cbridge-agent
```

### 2. Initialize & Add Documents
Initialize your workspace and tell ContextBridge which folders to index:
```bash
cbridge init
cbridge watch add /path/to/your/documents
```

### 3. Start the API Service
ContextBridge must be running in the background to serve requests:
```bash
# Start both the file watcher and the API server
cbridge start
```
*The API server runs at `http://127.0.0.1:9790` by default.*

---

## 🧠 HOW IT WORKS (For New Users)

ContextBridge acts as a "Semantic Bridge" between your files and OpenClaw:

1.  **Local Indexing**: When you add a folder, ContextBridge scans your documents (PDF, Docx, etc.) and breaks them into small, manageable text chunks.
2.  **Vectorization**: Using a **local** AI embedding model, it converts these chunks into mathematical vectors that represent their *meaning*.
3.  **Semantic Search**: When OpenClaw asks a question, it doesn't just look for exact words. It uses the API to find the most *semantically relevant* chunks from your library.
4.  **100% Private**: All parsing, embedding, and searching happen **entirely on your local machine**. Your private data is never uploaded to any cloud service.

---

## WHEN TO USE THIS SKILL (Trigger Scenarios)

**DIRECTIVE**: If the user's request involves any information that is NOT general public knowledge, you MUST query ContextBridge before answering. Do NOT hallucinate or say "I don't have access" without trying a search first.

### 1. Deep Fact Retrieval (Private Knowledge)
Trigger this when the user asks for specific numbers, names, or facts buried in their local files.
- *Examples*: "What was the total budget for the 2024 marketing campaign?", "Who was the lead engineer for Project X?", "Find the summary of the meeting from last Friday."

### 2. Policy-Based Auditing & Compliance
Trigger this when you are asked to review, verify, or check a document. 
- **CRITICAL**: You must first search for local "policies", "guidelines", "SOPs", or "standards" to establish the ground truth before performing the audit.
- *Examples*: "Does this contract follow our standard procurement policy?", "Review this PR based on our internal coding standards."

### 3. Contextual Drafting (Style & Templates)
Trigger this when the user wants to write something that should match a previous style or use a specific local template.
- *Examples*: "Draft a project proposal using our standard company template", "Write a follow-up email in the same tone as my previous client communications."

### 4. Technical Support & Internal Processes
Trigger this for "How-to" questions regarding internal tools, deployment, or onboarding.
- *Examples*: "How do I set up the local development environment?", "What are the steps for the employee onboarding process?", "How do we handle database migrations?"

## SEARCH STRATEGY (Best Practices)

- **Extract Keywords**: Do NOT search using full conversational sentences. Extract core entities and keywords (e.g., search `"2024 marketing budget"` instead of `"What is the 2024 marketing budget?"`).
- **Iterative Searching**: If your first search returns empty or irrelevant results, try again using synonyms, broader terms, or different keywords.
- **Multiple Queries**: For complex tasks (like auditing), you may need to execute multiple `curl` commands to gather all necessary rules and context.

## HOW TO USE THE API

### 1. Search Documents
Send a POST request to `/api/v1/search` using `curl`.
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/search -H 'Content-Type: application/json' -d '{\"query\": \"2024 marketing budget\", \"top_k\": 3}'"
}
```
*The API returns a JSON array of text chunks. You MUST cite the `metadata.source` in your final answer (e.g., "According to `budget.xlsx`...").*

### 2. Manage Watched Folders
If the user asks to add or remove a folder to their knowledge base:
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/watch/directories -H 'Content-Type: application/json' -d '{\"path\": \"/absolute/path/to/folder\"}'"
}
```
To check currently watched folders:
```json
{
  "command": "curl -s http://127.0.0.1:9790/api/v1/watch/status"
}
```
```

---

## 第五步：在 OpenClaw 中启用 Skill

放置好 `SKILL.md` 文件后，你需要确保智能体被允许使用它。

1. 打开你的 OpenClaw 配置文件（例如 `~/.openclaw/openclaw.json` 或你的工作区配置）。
2. 确保将 `contextbridge` 添加到智能体的 `tools.allow` 列表中，同时包含所需的 `exec` 或 `bash` 工具（或 `group:runtime`）。

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "allow": [
            "group:runtime",
            "contextbridge"
          ]
        }
      }
    ]
  }
}
```

---

## 真实工作流演示

假设用户在 OpenClaw 中提问：**"根据最新的 Q3 财务报表，我们的营销支出是多少？"**

1. **意图识别**：OpenClaw 的 LLM 分析问题，并读取 `contextbridge` Skill 的指令。
2. **Tool Calling**：LLM 决定使用 `exec` 工具运行 `curl` 命令来请求 ContextBridge API。
3. **API 响应**：ContextBridge 瞬间返回 3 个最相关的文本块，并附带来源文件 `Q3_Report.pdf`。
4. **最终生成**：LLM 综合这些数据，生成自然语言回答给用户，并附上引用来源。

如果在对话过程中，用户修改了本地的 `Q3_Report.pdf`，ContextBridge 的后台 Watcher 会瞬间重构该文档的向量。下一秒用户再次提问时，AI 就能立刻给出基于最新修改的回答，全程无需手动干预。

---

## 故障排查

### API 连接失败

```bash
# 检查服务状态
cbridge status

# 检查 API 端口是否被占用
lsof -i :9790

# 重启服务
cbridge stop
cbridge start
```

### 搜索不到最新内容

```bash
# 检查监控状态
curl -s http://127.0.0.1:9790/api/v1/watch/status

# 强制重新索引
cbridge index
```

### 国际化问题（命令不生效）

如果 `cbridge lang zh` 等命令不生效，可能是旧版本残留导致：

```bash
# 1. 清理旧版本
rm -f ~/Library/Python/*/lib/python/site-packages/cbridge.py
rm -rf ~/Library/Python/*/lib/python/site-packages/cbridge_agent*

# 2. 重新安装
pip uninstall cbridge-agent -y
pip install cbridge-agent

# 3. 验证版本
cbridge --version
```

### 服务状态检查命令

```bash
# 查看服务运行状态
cbridge status

# 查看 API 响应
curl -s http://127.0.0.1:9790/api/v1/health

# 查看监控目录
cbridge watch list

# 查看日志
cbridge logs
```

### Curl 命令失败

确保运行 OpenClaw 的机器上安装了 `curl`（Skill 元数据中指定了 `"requires": { "bins": ["curl"] }`）。

```bash
# 检查 curl 是否安装
curl --version

# 如果未安装，使用 Homebrew 安装
brew install curl
```
