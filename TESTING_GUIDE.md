# ContextBridge 重复索引问题修复

## 问题描述
当前 `cbridge start` 和 `cbridge serve` 可以同时运行，导致文件被重复索引（watcher 线程重复工作）。

## 解决方案

### 核心原则
- 同一时间只能有一个 watcher 在运行
- serve 模式 = watcher + API 服务器
- start 模式 = 仅 watcher

### 修改内容

#### 1. 新增工具函数 (`cbridge.py` 顶部)

```python
def is_process_running(pid: int) -> bool:
    """检查指定 PID 的进程是否正在运行"""
    # 跨平台支持（Windows/Unix）
    
def cleanup_pid_file(pid_file: Path) -> None:
    """清理无效或存在的 PID 文件"""
```

#### 2. 修改 `start()` 函数

**检测逻辑：**
- 检测 `~/.cbridge/cbridge.pid`（API 服务器 PID 文件）
- 如果 API 服务器在运行：
  - 显示警告信息
  - 提供建议（使用 `cbridge serve --foreground` 或先 `cbridge stop`）
  - 用户确认后可以选择继续或退出
  - **不自动停止** API 服务器

**警告信息：**
```
⚠️  检测到 API 服务器正在运行（PID: xxx）
API 服务器已包含文件监控功能，无需单独启动 watcher

建议：
  - 如需同时运行，请使用：cbridge serve --foreground
  - 或先停止 API 服务器：cbridge stop

是否继续启动 watcher？(y/n)
```

#### 3. 修改 `serve()` 函数

**检测逻辑：**
- 检测 `~/.cbridge/cbridge_watcher.pid`（watcher PID 文件）
- 如果 watcher 在运行：
  - **自动停止** watcher 进程（发送 SIGTERM）
  - 清理 PID 文件
  - 日志记录："检测到 watcher 进程运行中，已自动停止"
- 如果 PID 文件存在但进程不存在：
  - 清理 stale PID 文件

## 测试场景

### 场景 1: 先 start 后 serve → serve 自动停止 start
```bash
# 启动 watcher
cbridge start

# 启动 serve（应该自动停止 watcher）
cbridge serve

# 预期结果：
# - 显示："检测到 watcher 进程运行中，已自动停止"
# - watcher 进程被终止
# - serve 正常启动（包含 watcher 线程）
```

### 场景 2: 先 serve 后 start → start 提示用户
```bash
# 启动 serve
cbridge serve

# 尝试启动 watcher
cbridge start

# 预期结果：
# - 显示警告信息和用户建议
# - 询问："是否继续启动 watcher？(y/n)"
# - 用户选择 n → 退出
# - 用户选择 y → 继续启动（允许高级用户强制运行）
```

### 场景 3: 正常运行（无冲突）→ 无影响
```bash
# 单独启动 watcher
cbridge start

# 或单独启动 serve
cbridge serve

# 预期结果：
# - 无警告信息
# - 正常启动
```

## 测试步骤

### 手动测试

1. **清理环境**
   ```bash
   cbridge stop
   rm -f ~/.cbridge/cbridge.pid ~/.cbridge/cbridge_watcher.pid
   ```

2. **测试场景 1**
   ```bash
   cbridge start
   sleep 2
   cbridge status  # 确认 watcher 运行
   cbridge serve
   cbridge status  # 确认 watcher 已停止，serve 运行
   ```

3. **测试场景 2**
   ```bash
   cbridge stop
   cbridge serve
   sleep 2
   cbridge status  # 确认 serve 运行
   cbridge start   # 应该显示警告
   # 输入 'n' 取消
   ```

4. **测试场景 3**
   ```bash
   cbridge stop
   cbridge start
   cbridge status  # 确认 watcher 正常运行
   cbridge stop
   ```

### 自动化测试

运行测试脚本：
```bash
cd /Users/ekko/Documents/CODE_SPACE/whyischen/context-bridge
python test_duplicate_indexing_fix.py
```

## 边界情况处理

1. **PID 文件存在但进程不存在**
   - 自动清理 stale PID 文件
   - 不影响正常启动

2. **无权限停止进程**
   - 显示错误信息
   - 退出并返回错误码

3. **Windows 平台兼容性**
   - 使用 `taskkill` 代替 `kill`
   - 使用 `CREATE_NEW_PROCESS_GROUP` 和 `DETACHED_PROCESS`

## 代码风格

- 遵循现有代码风格（中文注释 + 英文日志）
- 使用 Rich 控制台输出（彩色提示）
- 适当的错误处理和日志记录
- 跨平台支持（Windows/Unix）

## 修改文件

- `cbridge.py` - 主要修改文件
  - 新增：`is_process_running()`, `cleanup_pid_file()`
  - 修改：`start()` 函数 - 添加 API 服务器检测
  - 修改：`serve()` 函数 - 添加 watcher 检测和自动停止

## 测试脚本

- `test_duplicate_indexing_fix.py` - 自动化测试脚本
  - 测试所有三个场景
  - 自动清理环境
  - 输出测试结果汇总
