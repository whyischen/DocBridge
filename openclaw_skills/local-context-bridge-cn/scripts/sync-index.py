#!/usr/bin/env python3
"""
强制同步 ContextBridge 索引

用途:
- 确保最新文件被索引
- 修复索引不一致问题
- 添加新文件后立即生效

用法:
    python scripts/sync-index.py
    
返回:
    索引同步结果报告
"""

import subprocess
import sys
import time
from datetime import datetime


def sync_index():
    """
    执行索引同步
    
    Returns:
        bool: 同步是否成功
    """
    print("🔄 开始重建索引...")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 执行索引命令
        result = subprocess.run(
            ['cbridge', 'index'],
            capture_output=True,
            text=True,
            timeout=300  # 索引可能耗时较长，设置 5 分钟超时
        )
        
        # 输出结果
        if result.returncode == 0:
            print("✅ 索引重建成功")
            if result.stdout:
                print("\n📋 详细输出:")
                print(result.stdout)
            return True
        else:
            print("❌ 索引重建失败")
            if result.stderr:
                print(f"\n错误信息:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 索引超时（超过 5 分钟）")
        print("   可能原因：文档数量过多或单个文件过大")
        print("   建议：检查 ~/.cbridge/config.yaml 中的 exclude_patterns")
        return False
    except Exception as e:
        print(f"❌ 执行异常：{str(e)}")
        return False


def main():
    print("=" * 60)
    print("🌉 ContextBridge 索引同步")
    print("=" * 60)
    print()
    
    success = sync_index()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 索引同步完成，现在可以搜索最新文档")
        sys.exit(0)
    else:
        print("⚠️  索引同步失败，请检查上述错误信息")
        print("\n建议操作:")
        print("  1. 检查 cbridge 服务状态：cbridge status")
        print("  2. 查看日志：cbridge logs")
        print("  3. 检查监控目录：cbridge watch list")
        sys.exit(1)


if __name__ == '__main__':
    main()
