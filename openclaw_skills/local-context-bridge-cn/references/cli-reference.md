# CLI 完整命令参考

---

## 初始化配置

| 命令 | 说明 |
|------|------|
| `cbridge init` | 初始化工作区，生成 `~/.cbridge/config.yaml` |
| `cbridge lang zh` | 切换 CLI 语言为中文 |
| `cbridge lang en` | 切换 CLI 语言为英文 |

---

## 目录管理

| 命令 | 说明 |
|------|------|
| `cbridge watch add <path>` | 添加监控目录 |
| `cbridge watch remove <path>` | 移除监控目录 |
| `cbridge watch list` | 查看所有监控目录 |

---

## 索引管理

| 命令 | 说明 |
|------|------|
| `cbridge index` | 手动重建索引 |
| `cbridge status` | 查看服务状态 |
| `cbridge logs` | 查看服务日志 |

---

## 搜索

| 命令 | 说明 |
|------|------|
| `cbridge search <query>` | 语义搜索文档 |
| `cbridge search <query> --top_k 10` | 指定返回结果数量 |

---

## 服务控制

| 命令 | 说明 |
|------|------|
| `cbridge start` | 启动后台服务（含监控 +API） |
| `cbridge stop` | 停止服务 |
| `cbridge restart` | 重启服务 |

---

## 配置文件

编辑 `~/.cbridge/config.yaml`：

```yaml
workspace_dir: ~/.cbridge/workspace
watch_dirs:
  - /path/to/documents
exclude_patterns:
  - "**/node_modules/**"
  - "**/.git/**"
language: zh
```

### 性能优化（低配设备）

```bash
export CB_MAX_CONCURRENT_FILES=2
export CB_EMBEDDING_BATCH_SIZE=4
export CB_DISABLE_WATCHER=true
```
