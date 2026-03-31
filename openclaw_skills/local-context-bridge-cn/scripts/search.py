#!/usr/bin/env python3
"""
语义搜索封装，带重试逻辑和错误处理

用法:
    python scripts/search.py "2024 预算" --top_k 5
    python scripts/search.py "采购政策" --top_k 3 --max_retries 3

返回:
    JSON 格式搜索结果，包含 content、metadata、score 字段
"""

import subprocess
import json
import sys
import time
import argparse


def search(query: str, top_k: int = 5, max_retries: int = 2):
    """
    执行语义搜索，带重试逻辑
    
    Args:
        query: 搜索关键词
        top_k: 返回结果数量
        max_retries: 最大重试次数
    
    Returns:
        dict: 搜索结果列表
    
    Raises:
        Exception: 搜索失败时抛出异常
    """
    for i in range(max_retries + 1):
        try:
            cmd = ['cbridge', 'search', query, '--top_k', str(top_k)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 尝试解析 JSON 输出
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # 如果是纯文本输出，包装成统一格式
                    return {
                        'results': [{'content': result.stdout, 'metadata': {'source': 'cli_output'}}],
                        'query': query
                    }
            
            # 命令执行失败，记录错误
            error_msg = result.stderr or f"Command failed with returncode {result.returncode}"
            raise Exception(error_msg)
            
        except (subprocess.TimeoutExpired, Exception) as e:
            if i == max_retries:
                raise Exception(f"Search failed after {max_retries} retries: {str(e)}")
            time.sleep(1)
    
    return None


def main():
    parser = argparse.ArgumentParser(description='ContextBridge 语义搜索')
    parser.add_argument('query', type=str, help='搜索关键词')
    parser.add_argument('--top_k', type=int, default=5, help='返回结果数量 (默认：5)')
    parser.add_argument('--max_retries', type=int, default=2, help='最大重试次数 (默认：2)')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    
    args = parser.parse_args()
    
    try:
        results = search(args.query, args.top_k, args.max_retries)
        
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            # 人类可读格式输出
            if not results or 'results' not in results:
                print("❌ 未找到相关结果")
                return
            
            print(f"🔍 搜索：{args.query}")
            print(f"📊 找到 {len(results['results'])} 个结果\n")
            
            for i, item in enumerate(results['results'], 1):
                content = item.get('content', '')[:500]  # 限制显示长度
                source = item.get('metadata', {}).get('source', '未知来源')
                score = item.get('score', 0)
                
                print(f"[{i}] 📄 来源：{source} (相关度：{score:.2f})")
                print(f"    {content}...")
                print()
                
    except Exception as e:
        print(f"❌ 搜索失败：{str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
