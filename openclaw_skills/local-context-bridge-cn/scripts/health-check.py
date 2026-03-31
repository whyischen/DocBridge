#!/usr/bin/env python3
"""
ContextBridge 健康检查

检查项目:
- 服务运行状态
- 监控目录列表
- 索引新鲜度
- 配置文件存在性

用法:
    python scripts/health-check.py

返回:
    健康检查报告（文本格式）
"""

import subprocess
import os
import sys
from datetime import datetime


def run_command(cmd: list) -> tuple:
    """执行命令并返回 (stdout, stderr, returncode)"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return '', 'Command timeout', -1
    except Exception as e:
        return '', str(e), -1


def check_service_status():
    """检查服务运行状态"""
    print("🔍 检查服务状态...")
    stdout, stderr, code = run_command(['cbridge', 'status'])
    
    if code == 0:
        print("✅ 服务运行正常")
        if stdout:
            print(f"   {stdout.strip()}")
        return True
    else:
        print("❌ 服务未运行或异常")
        if stderr:
            print(f"   错误：{stderr.strip()}")
        return False


def check_watch_directories():
    """检查监控目录"""
    print("\n🔍 检查监控目录...")
    stdout, stderr, code = run_command(['cbridge', 'watch', 'list'])
    
    if code == 0 and stdout.strip():
        print("✅ 监控目录配置:")
        for line in stdout.strip().split('\n'):
            print(f"   📁 {line}")
        return True
    else:
        print("⚠️  未配置监控目录")
        print("   使用 'cbridge watch add <path>' 添加目录")
        return False


def check_config_file():
    """检查配置文件"""
    print("\n🔍 检查配置文件...")
    config_path = os.path.expanduser('~/.cbridge/config.yaml')
    
    if os.path.exists(config_path):
        print(f"✅ 配置文件存在：{config_path}")
        
        # 读取文件大小
        size = os.path.getsize(config_path)
        print(f"   文件大小：{size} 字节")
        return True
    else:
        print("❌ 配置文件不存在")
        print("   使用 'cbridge init' 初始化")
        return False


def check_index_freshness():
    """检查索引新鲜度"""
    print("\n🔍 检查索引状态...")
    workspace_dir = os.path.expanduser('~/.cbridge/workspace')
    
    if not os.path.exists(workspace_dir):
        print("⚠️  工作区目录不存在")
        return False
    
    # 查找最新的索引文件
    index_files = []
    for root, dirs, files in os.walk(workspace_dir):
        for f in files:
            if f.endswith('.db') or 'index' in f.lower():
                filepath = os.path.join(root, f)
                mtime = os.path.getmtime(filepath)
                index_files.append((filepath, mtime))
    
    if index_files:
        # 按修改时间排序
        index_files.sort(key=lambda x: x[1], reverse=True)
        latest = index_files[0]
        mtime = datetime.fromtimestamp(latest[1])
        age = datetime.now() - mtime
        
        print(f"✅ 索引文件：{latest[0]}")
        print(f"   最后更新：{mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   距今：{age}")
        
        # 如果超过 24 小时未更新，提示重建
        if age.total_seconds() > 86400:
            print("⚠️  索引可能过期，建议运行 'cbridge index' 重建")
        return True
    else:
        print("⚠️  未找到索引文件")
        print("   使用 'cbridge index' 构建索引")
        return False


def main():
    print("=" * 60)
    print("🌉 ContextBridge 健康检查")
    print("=" * 60)
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        '服务状态': check_service_status(),
        '监控目录': check_watch_directories(),
        '配置文件': check_config_file(),
        '索引状态': check_index_freshness(),
    }
    
    print("\n" + "=" * 60)
    print("📊 检查摘要")
    print("=" * 60)
    
    all_ok = True
    for item, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"{status} {item}: {'正常' if ok else '异常'}")
        if not ok:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 所有检查项通过，ContextBridge 运行正常")
        sys.exit(0)
    else:
        print("⚠️  部分检查项失败，请参考上述建议进行修复")
        sys.exit(1)


if __name__ == '__main__':
    main()
