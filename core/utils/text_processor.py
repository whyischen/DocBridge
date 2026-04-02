"""
文本分割器
提供文本分割的统一接口和工具函数
"""
import re
from typing import List, Dict, Optional
from core.interfaces.chunk_strategy_manager import IChunkStrategy
from core.utils.chunk_strategy_manager import get_global_strategy_manager
from core.utils.logger import get_logger

logger = get_logger("text_processor")


# 保持原有MarkdownTextSplitter以确保向后兼容
class MarkdownTextSplitter:
    """向后兼容的 Markdown 文本分割器"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
            
        # 按可能具有语义的段落分隔符切分
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
                
            p_len = len(p)
            # 如果加上当前段落超出了 chunk_size，且当前 chunk 不为空，就把当前 chunk 存起来
            if current_length + p_len > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                # 实现简单的 overlap：尝试保留最后一个段落作为重叠内容（只要它不是太长）
                overlap = current_chunk[-1] if current_chunk and len(current_chunk[-1]) <= self.chunk_overlap else ""
                current_chunk = [overlap, p] if overlap else [p]
                current_length = sum(len(x) for x in current_chunk) + (2 if overlap else 0)
            else:
                current_chunk.append(p)
                current_length += p_len + (2 if len(current_chunk) > 1 else 0)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return chunks


def split_text(
    text: str,
    strategy: Optional[str] = None,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    **kwargs
) -> List[str]:
    """
    使用指定策略分割文本（推荐方式）
    
    Args:
        text: 输入文本
        strategy: 分割策略名称，如果为None则使用默认策略
        chunk_size: 每个 chunk 的目标字数
        chunk_overlap: chunks 之间的重叠字数
        **kwargs: 传递给特定策略的额外参数
        
    Returns:
        chunks 列表
    """
    manager = get_global_strategy_manager()
    
    # 如果未指定策略，使用默认策略
    if strategy is None:
        strategy = manager.get_default_strategy()
    
    try:
        # 合并参数
        split_kwargs = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            **kwargs
        }
        
        chunk_strategy = manager.get_strategy(strategy, **split_kwargs)
        logger.debug(f"Using chunk strategy: {strategy} (v{chunk_strategy.get_version()})")
        
        return chunk_strategy.split(text, **split_kwargs)
    except ValueError as e:
        logger.error(f"Failed to get chunk strategy: {e}")
        raise


def get_chunk_strategy(strategy: Optional[str] = None, **kwargs) -> IChunkStrategy:
    """
    获取分块策略实例
    
    Args:
        strategy: 策略名称，如果为None则使用默认策略
        **kwargs: 传递给策略构造函数的参数
        
    Returns:
        IChunkStrategy 实例
    """
    manager = get_global_strategy_manager()
    
    if strategy is None:
        strategy = manager.get_default_strategy()
    
    return manager.get_strategy(strategy, **kwargs)


def list_available_strategies() -> List[str]:
    """列出所有可用的分块策略"""
    manager = get_global_strategy_manager()
    return manager.list_strategies()


def get_strategy_metadata(strategy: Optional[str] = None) -> Dict:
    """获取策略元数据"""
    manager = get_global_strategy_manager()
    
    if strategy is None:
        strategy = manager.get_default_strategy()
    
    return manager.get_strategy_metadata(strategy)


def extract_with_strategy(
    filename: str,
    content: str,
    strategy: Optional[str] = None,
    **kwargs
) -> tuple[str, str, List[str]]:
    """
    使用指定策略提取摘要、大纲并分割文本（一站式）
    
    Args:
        filename: 文件名
        content: 文档内容
        strategy: 分割策略名称，如果为None则使用默认策略
        **kwargs: 传递给策略的参数（如 chunk_size, chunk_overlap）
        
    Returns:
        (l0_abstract, l1_outline, chunks) 元组
    """
    # 获取策略实例
    chunk_strategy = get_chunk_strategy(strategy, **kwargs)
    
    # 使用策略特定的提取方法
    l0_abstract = chunk_strategy.extract_l0_abstract(filename, content)
    l1_outline = chunk_strategy.extract_l1_outline(content)
    
    # 使用策略分割文本
    chunks = chunk_strategy.split(content, **kwargs)
    
    logger.debug(
        f"Extracted with strategy '{chunk_strategy.get_name()}': "
        f"L0={len(l0_abstract)} chars, L1={len(l1_outline)} chars, L2={len(chunks)} chunks"
    )
    
    return l0_abstract, l1_outline, chunks


def get_hybrid_splitter(chunk_size: int = 800, chunk_overlap: int = 150):
    """
    获取混合启发式分段器实例
    为了保持轻量级，默认不导入，只在需要时使用
    """
    from core.utils.hybrid_text_splitter import HybridTextSplitter
    return HybridTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


# 为了向后兼容，从 text_extractor 导入提取器
from core.utils.text_extractor import HeuristicExtractor, get_enhanced_extractor

__all__ = [
    "MarkdownTextSplitter",
    "split_text",
    "get_chunk_strategy",
    "list_available_strategies",
    "get_strategy_metadata",
    "extract_with_strategy",
    "get_hybrid_splitter",
    "HeuristicExtractor",
    "get_enhanced_extractor",
]

