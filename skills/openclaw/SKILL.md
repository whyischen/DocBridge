---
name: ContextBridge
description: 本地文档知识库管理 | Local document knowledge base management for AI agents. Provides semantic search, real-time file monitoring, and HTTP API for context retrieval.
metadata:
  emoji: 📚
  requires:
    - cbridge (CLI tool)
    - Python 3.10+
  platforms:
    - macOS
    - Linux
    - Windows
  languages:
    - zh (Chinese)
    - en (English)
---

# ContextBridge Skill

ContextBridge 是一个轻量级本地知识库工具，为 AI Agent 提供文档语义搜索和上下文检索能力。支持实时监控文件变化、自动索引、多语言界面。

## 🎯 核心功能

### 安装检测

```bash
which cbridge
```

- **已安装**: 返回路径 (如 `/opt/homebrew/bin/cbridge`)
- **未安装**: 无输出或返回 `command not found`

### 三种安装方式

#### 1. pip 安装 (推荐)
```bash
pip install cbridge-agent
```

#### 2. Homebrew 安装 (macOS)
```bash
brew install cbridge
```

#### 3. 源码安装
```bash
git clone https://github.com/whyischen/context-bridge.git
cd context-bridge
pip install -e .
```

### 初始化配置

```bash
cbridge init
```

**交互式配置项:**
- **语言选择**: `zh` (中文) / `en` (English)
- **运行模式**: 
  - `embedded` (内嵌模式，默认) - 使用内置向量数据库
  - `external` (外部模式) - 连接外部 OpenViking/QMD 服务
- **工作区目录**: 默认 `~/.cbridge/workspace`

**初始化流程:**
1. 检测并停止现有服务
2. 交互式配置
3. 自动启动后台监控服务
4. 创建示例文档

### 启动服务

#### 启动文件监控 (Watcher)
```bash
# 后台启动 (默认)
cbridge start

# 前台启动 (调试用)
cbridge start --foreground
```

#### 启动 API 服务
```bash
# 后台启动 API 服务 (默认端口 9790)
cbridge serve

# 指定端口和主机
cbridge serve --port 9790 --host 127.0.0.1

# 前台启动
cbridge serve --foreground
```

**注意:** `cbridge serve` 会自动停止运行中的 `watcher` 进程，因为 API 服务已包含文件监控功能。

### 语言配置

```bash
# 切换为中文
cbridge lang zh

# Switch to English
cbridge lang en
```

## ⚙️ 配置管理

### 查看配置

```bash
cbridge config
```

显示配置文件路径 (`~/.cbridge/config.yaml`) 及内容。

### 管理监控目录

#### 列出监控目录
```bash
cbridge watch list
```

#### 添加监控目录
```bash
# 添加到监控并立即索引
cbridge watch add /path/to/documents

# 仅添加到监控列表，不立即索引 (后台执行时索引)
cbridge watch add /path/to/documents --no-index

# 静默模式
cbridge watch add /path/to/documents --quiet

# 后台执行索引 (立即返回)
cbridge watch add /path/to/documents --background
```

**支持的文件格式:**
- 文档：`.pdf`, `.docx`, `.doc`, `.pptx`, `.ppt`
- 表格：`.xlsx`, `.xls`, `.csv`
- 文本：`.md`, `.txt`, `.text`

#### 移除监控目录
```bash
# 移除并清理向量数据
cbridge watch remove /path/to/documents

# 仅从监控列表移除，保留向量数据
cbridge watch remove /path/to/documents --skip-cleanup

# 等待清理完成 (默认后台执行)
cbridge watch remove /path/to/documents --wait
```

### 性能调优

配置文件位置：`~/.cbridge/config.yaml`

**低性能设备配置示例:**
```yaml
watcher:
  performance_mode: low  # low | balanced | high
  poll_interval: 10      # 轮询间隔 (秒)
  debounce_seconds: 5    # 防抖时间 (秒)
  max_file_size_mb: 10   # 最大文件大小 (MB)
  max_queue_size: 100    # 任务队列大小
  worker_threads: 1      # Worker 线程数
```

**性能模式说明:**
- **low**: 最保守设置，适合资源受限设备
  - 轮询间隔：≥10 秒
  - 防抖时间：≥5 秒
  - 最大文件：≤10MB
  - 队列大小：≤100
  - 线程数：1

- **balanced** (默认): 平衡性能和资源占用
  - 轮询间隔：≥5 秒
  - 防抖时间：≥3 秒
  - 最大文件：≤50MB
  - 队列大小：≤500
  - 线程数：≤2

- **high**: 高性能模式，使用配置文件中的值

## 🔍 搜索功能

### HTTP API 搜索

**端点:** `POST /api/v1/search`

**请求格式:**
```json
{
  "query": "搜索关键词",
  "top_k": 5,
  "min_score": 0.5
}
```

**参数说明:**
- `query` (必填): 搜索查询文本
- `top_k` (可选): 返回结果数量，默认 5
- `min_score` (可选): 最低相似度阈值 (0.0-1.0)，默认 0.5

**响应格式:**
```json
{
  "results": [
    {
      "content": "匹配的文档内容...",
      "metadata": {
        "source": "filename.pdf"
      },
      "score": 0.85
    }
  ]
}
```

**示例 (curl):**
```bash
curl -X POST http://localhost:9790/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ContextBridge 功能", "top_k": 5}'
```

### CLI 搜索

```bash
# 基本搜索
cbridge search "关键词"

# 指定返回数量
cbridge search "关键词" --top-k 10

# 设置相似度阈值
cbridge search "关键词" --threshold 0.7

# 关闭关键词重排序
cbridge search "关键词" --no-rerank

# 简化输出 (不显示详细解释)
cbridge search "关键词" --no-explain
```

**搜索特性:**
- **语义检索**: 基于向量相似度
- **关键词重排序**: 默认启用，提升关键词匹配度高的结果
- **可解释性**: 显示语义分数、关键词匹配数、综合得分

### 最佳实践

#### 1. 关键词提取
- 使用 2-5 个核心关键词
- 避免过长句子
- 示例：✅ "ContextBridge 安装配置" ❌ "我想知道怎么安装和配置 ContextBridge"

#### 2. 迭代搜索
```bash
# 第一次：宽泛搜索
cbridge search "安装"

# 第二次：细化搜索
cbridge search "安装 pip homebrew"

# 第三次：精确搜索
cbridge search "pip install cbridge-agent"
```

#### 3. 调整阈值
- 高阈值 (0.7-0.9): 精确匹配，结果少但准确
- 中阈值 (0.5-0.7): 平衡模式 (默认)
- 低阈值 (0.3-0.5): 宽泛搜索，结果多但需筛选

## 🛠️ 故障排查

### 服务状态检查

```bash
# 查看运行状态
cbridge status
```

**输出示例:**
```
📊 ContextBridge Status:
  Language: en
  Mode: embedded
  Workspace: /Users/ekko/.cbridge/workspace
✅ Watcher: Running (PID 62621)
⚠️  API Server: Not running
```

### 日志查看

```bash
# 查看最后 50 行日志
cbridge logs

# 查看最后 N 行
cbridge logs -n 100

# 实时跟踪日志 (类似 tail -f)
cbridge logs -f

# 退出跟踪：Ctrl+C
```

**日志文件位置:**
- Watcher 日志：`~/.cbridge/logs/cbridge-watcher.log`
- API 服务日志：`~/.cbridge/logs/cbridge-serve.log`

### 健康检查

```bash
# HTTP API 健康检查
curl http://localhost:9790/api/v1/health
```

**响应:**
```json
{"status": "healthy", "service": "ContextBridge API"}
```

### 常见问题 (FAQ)

#### 1. `cbridge: command not found`
**原因:** 未安装或 PATH 未配置  
**解决:**
```bash
# 检查安装
which cbridge

# 重新安装
pip install cbridge-agent

# 或添加到 PATH (macOS)
export PATH="$HOME/.local/bin:$PATH"
```

#### 2. 服务启动失败：端口被占用
**原因:** 9790 端口已被其他进程占用  
**解决:**
```bash
# 查看占用端口的进程
lsof -i :9790

# 停止现有服务
cbridge stop

# 或指定其他端口
cbridge serve --port 9791
```

#### 3. 索引失败：文件格式不支持
**原因:** 尝试索引不支持的文件格式  
**解决:**
- 检查支持格式：`.pdf`, `.docx`, `.xlsx`, `.md`, `.txt` 等
- 查看错误日志：`cbridge logs -f`
- 转换文件格式为支持的类型

#### 4. 搜索结果为空
**原因:** 
- 文档未索引
- 搜索阈值过高
- 关键词不匹配

**解决:**
```bash
# 检查监控目录
cbridge watch list

# 手动触发索引
cbridge index

# 降低阈值
cbridge search "关键词" --threshold 0.3

# 查看是否有文档
cbridge search "" --threshold 0.0
```

#### 5. 服务自动停止
**原因:** 
- 系统资源不足
- 配置文件错误
- PID 文件损坏

**解决:**
```bash
# 清理 PID 文件
rm ~/.cbridge/cbridge.pid
rm ~/.cbridge/cbridge_watcher.pid

# 重新初始化
cbridge init

# 检查配置
cbridge config
```

#### 6. 低性能设备卡顿
**原因:** 默认配置对资源占用较高  
**解决:**
```yaml
# 编辑 ~/.cbridge/config.yaml
watcher:
  performance_mode: low
  worker_threads: 1
  max_file_size_mb: 10
```

#### 7. 外部模式连接失败
**原因:** OpenViking/QMD 服务未启动  
**解决:**
```bash
# 检查外部服务状态
curl http://localhost:9780  # OpenViking
curl http://localhost:9791  # QMD

# 切换回内嵌模式
cbridge init
# 选择模式时输入：embedded
```

#### 8. 语言切换不生效
**原因:** 配置文件未正确保存  
**解决:**
```bash
# 手动切换语言
cbridge lang zh

# 验证配置
cat ~/.cbridge/config.yaml | grep language

# 重启服务
cbridge stop
cbridge start
```

## 📖 使用场景

### 1. 信息检索 (Q&A)

**场景:** 快速查找文档中的信息

```bash
# 搜索特定主题
cbridge search "如何配置 OpenViking"

# 查找代码示例
cbridge search "Python API 调用示例"

# 查找错误解决方案
cbridge search "连接失败 错误处理"
```

**最佳实践:**
- 使用问题关键词而非完整句子
- 结合 `--top-k` 获取多个参考
- 使用 `--explain` 查看匹配详情

### 2. 文档审计

**场景:** 检查文档完整性和一致性

```bash
# 列出所有索引的文档
cbridge watch list

# 查看索引状态
cbridge status

# 重新索引所有文档
cbridge index
```

**审计流程:**
1. 检查监控目录是否完整
2. 验证索引文档数量
3. 搜索关键文档确认索引质量
4. 定期运行 `cbridge index` 清理幽灵数据

### 3. 基于上下文的写作

**场景:** AI Agent 写作时检索相关背景资料

**HTTP API 调用示例 (Python):**
```python
import requests

def search_context(query: str, top_k: int = 5):
    response = requests.post(
        "http://localhost:9790/api/v1/search",
        json={"query": query, "top_k": top_k}
    )
    return response.json()["results"]

# 使用示例
results = search_context("ContextBridge 架构设计")
for r in results:
    print(f"来源：{r['metadata']['source']}")
    print(f"内容：{r['content'][:200]}...")
```

**写作流程:**
1. 确定写作主题关键词
2. 调用 API 检索相关上下文
3. 将检索结果作为 AI 的参考背景
4. 基于上下文生成内容

### 4. 故障排查和 SOP

**场景:** 快速查找问题解决方案

**标准操作流程 (SOP):**

```bash
# Step 1: 检查服务状态
cbridge status

# Step 2: 查看最近日志
cbridge logs -n 100

# Step 3: 搜索相关错误
cbridge search "错误关键词"

# Step 4: 实时跟踪日志
cbridge logs -f

# Step 5: 重新索引 (如需要)
cbridge index
```

**故障排查清单:**
- [ ] 服务是否运行 (`cbridge status`)
- [ ] 日志是否有错误 (`cbridge logs`)
- [ ] 监控目录是否正确 (`cbridge watch list`)
- [ ] 配置文件是否有效 (`cbridge config`)
- [ ] API 是否可访问 (`curl http://localhost:9790/api/v1/health`)

## 🔗 附录

### 配置文件结构

```yaml
# ~/.cbridge/config.yaml
mode: embedded           # 运行模式：embedded | external
language: zh             # 语言：zh | en
workspace_dir: ~/.cbridge/workspace
watch_dirs:
  - /path/to/docs1
  - /path/to/docs2
watcher:
  performance_mode: balanced
  poll_interval: 5
  debounce_seconds: 3
  max_file_size_mb: 50
  max_queue_size: 500
  worker_threads: 2
openviking:              # 仅 external 模式
  endpoint: http://localhost:9780
  mount_path: viking://contextbridge/
qmd:                     # 仅 external 模式
  endpoint: http://localhost:9791
  collection: cb_documents
```

### API 端点完整列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/search` | POST | 语义搜索 |
| `/api/v1/watch/status` | GET | 获取监控状态 |
| `/api/v1/watch/directories` | POST | 添加监控目录 |
| `/api/v1/watch/directories` | DELETE | 移除监控目录 |
| `/api/v1/index/sync` | POST | 触发全量索引 |
| `/api/v1/health` | GET | 健康检查 |

### CLI 命令速查

```bash
# 初始化
cbridge init

# 服务管理
cbridge start [--foreground]
cbridge serve [--port 9790] [--foreground]
cbridge stop

# 监控目录
cbridge watch list
cbridge watch add <path> [--no-index] [--background]
cbridge watch remove <path> [--skip-cleanup]

# 索引
cbridge index [--path <dir>]

# 搜索
cbridge search <query> [--top-k N] [--threshold 0.5]

# 配置
cbridge config
cbridge lang zh|en

# 日志
cbridge logs [-n N] [-f]

# 状态
cbridge status

# MCP
cbridge mcp
```

### 支持的文件格式

**文档:**
- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- PowerPoint (`.pptx`, `.ppt`)

**表格:**
- Excel (`.xlsx`, `.xls`)
- CSV (`.csv`)

**文本:**
- Markdown (`.md`, `.markdown`)
- 纯文本 (`.txt`, `.text`)

---

**版本:** 1.0.0  
**最后更新:** 2026-03-19  
**代码仓库:** https://github.com/whyischen/context-bridge
