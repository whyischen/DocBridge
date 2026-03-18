# 修改摘要 - ContextBridge 重复索引问题修复

## 修改的文件
- `cbridge.py` - 主程序文件

## 代码变更

### 1. 新增工具函数（第 16-47 行）

在 `console = Console(stderr=True)` 之后添加：

```python
# ============================================================================
# 进程检测工具函数
# ============================================================================

def is_process_running(pid: int) -> bool:
    """检查指定 PID 的进程是否正在运行"""
    import os
    import subprocess
    
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False

def cleanup_pid_file(pid_file: Path) -> None:
    """清理无效或存在的 PID 文件"""
    if pid_file.exists():
        try:
            pid_file.unlink()
        except Exception:
            pass
```

### 2. 修改 `start()` 函数（约第 556-575 行）

在 `log_dir.mkdir(parents=True, exist_ok=True)` 之后添加：

```python
# 检测 API 服务器是否在运行（serve 模式）
serve_pid_file = Path.home() / ".cbridge" / "cbridge.pid"
if serve_pid_file.exists():
    try:
        pid = int(serve_pid_file.read_text().strip())
        if is_process_running(pid):
            console.print("[yellow]⚠️  检测到 API 服务器正在运行（PID: {}）[/yellow]".format(pid))
            console.print("[yellow]API 服务器已包含文件监控功能，无需单独启动 watcher[/yellow]")
            console.print()
            console.print("[cyan]建议：[/cyan]")
            console.print("  - 如需同时运行，请使用：[green]cbridge serve --foreground[/green]")
            console.print("  - 或先停止 API 服务器：[green]cbridge stop[/green]")
            console.print()
            if not click.confirm("是否继续启动 watcher？", default=False):
                console.print("[dim]已取消启动 watcher[/dim]")
                return
            console.print("[dim]继续启动 watcher...[/dim]")
            console.print()
    except (ValueError, FileNotFoundError):
        cleanup_pid_file(serve_pid_file)
```

### 3. 修改 `serve()` 函数（约第 681-707 行）

在函数开始处，原有的停止 serve daemon 逻辑之前添加：

```python
# Step 1: 检测并停止正在运行的 watcher 进程（start 模式）
watcher_pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
if watcher_pid_file.exists():
    try:
        pid = int(watcher_pid_file.read_text().strip())
        if is_process_running(pid):
            # 自动停止 watcher 进程
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            watcher_pid_file.unlink()
            console.print("[cyan]检测到 watcher 进程运行中，已自动停止[/cyan]")
        else:
            # 进程不存在，清理 PID 文件
            cleanup_pid_file(watcher_pid_file)
    except (ValueError, FileNotFoundError):
        cleanup_pid_file(watcher_pid_file)
    except PermissionError:
        console.print("[red]❌ 无权限停止 watcher 进程（PID: {}）[/red]".format(pid))
        sys.exit(1)

# Step 2: Stop any running serve daemon
# ... 原有代码保持不变
```

## 行为变更

### `cbridge start`
- **新增：** 检测 API 服务器是否运行
- **新增：** 如果检测到 API 服务器，显示警告并询问用户
- **保持：** 用户可以选择继续或退出

### `cbridge serve`
- **新增：** 检测 watcher 进程是否运行
- **新增：** 如果检测到 watcher，自动停止它
- **新增：** 显示日志："检测到 watcher 进程运行中，已自动停止"
- **保持：** 继续正常启动 API 服务器

## 测试命令

```bash
# 语法检查
python3 -m py_compile cbridge.py

# 运行自动化测试
python test_duplicate_indexing_fix.py

# 手动测试
cbridge stop
cbridge start
cbridge serve  # 应该自动停止 watcher
```

## 影响范围

- ✅ 向后兼容：不影响现有单独使用 start 或 serve 的用户
- ✅ 安全性：需要用户确认才继续（start 模式）
- ✅ 自动化：自动处理冲突（serve 模式）
- ✅ 跨平台：支持 Windows 和 Unix 系统
