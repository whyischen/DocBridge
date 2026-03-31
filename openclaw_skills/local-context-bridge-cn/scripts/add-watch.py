#!/usr/bin/env python3
"""
添加目录到 ContextBridge 监控列表

用法:
    python scripts/add-watch.py /path/to/folder
    python scripts/add-watch.py .  # 添加当前目录

返回:
    添加结果报告
"""

import subprocess
import sys
import os
from pathlib import Path


def add_watch_directory(path: str) -> bool:
    """
    添加监控目录
    
    Args:
        path: 要添加的目录路径
    
    Returns:
        bool: 添加是否成功
    """
    # 转换为绝对路径
    abs_path = os.path.abspath(path)
    
    # 验证路径存在
    if not os.path.exists(abs_path):
        print(f"❌ 路径不存在：{abs_path}")
        return False
    
    if not os.path.isdir(abs_path):
        print(f"❌ 不是目录：{abs_path}")
        return False
    
    print(f"📁 添加监控目录：{abs_path}")
    print()
    
    try:
        result = subprocess.run(
            ['cbridge', 'watch', 'add', abs_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 目录添加成功")
            if result.stdout:
                print(f"\n{result.stdout}")
            
            # 提示用户重建索引
            print("\n💡 提示：运行以下命令重建索引以立即生效")
            print("   python scripts/sync-index.py")
            print("   或")
            print("   cbridge index")
            return True
        else:
            print("❌ 添加失败")
            if result.stderr:
                print(f"\n错误信息:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 命令超时")
        return False
    except Exception as e:
        print(f"❌ 执行异常：{str(e)}")
        return False


def main():
    print("=" * 60)
    print("🌉 ContextBridge 添加监控目录")
    print("=" * 60)
    print()
    
    # 检查参数
    if len(sys.argv) < 2:
        print("用法：python scripts/add-watch.py <目录路径>")
        print("\n示例:")
        print("  python scripts/add-watch.py /Users/ekko/Documents")
        print("  python scripts/add-watch.py .  # 添加当前目录")
        sys.exit(1)
    
    path = sys.argv[1]
    success = add_watch_directory(path)
    
    print()
    print("=" * 60)
    if success:
        print("🎉 目录添加完成")
        sys.exit(0)
    else:
        print("⚠️  目录添加失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
