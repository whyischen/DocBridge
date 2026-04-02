"""
分块策略管理器接口
用于管理和演进分割算法的抽象层
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type


class IChunkStrategy(ABC):
    """分块策略接口"""
    
    @abstractmethod
    def split(self, text: str, **kwargs) -> List[str]:
        """
        执行分块操作
        
        Args:
            text: 输入文本
            **kwargs: 策略特定的参数
            
        Returns:
            chunks 列表
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取策略名称"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """获取策略版本"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取策略元数据
        
        Returns:
            包含策略信息的字典，如：
            {
                "name": "paragraph",
                "version": "1.0.0",
                "description": "按段落分割",
                "parameters": {
                    "chunk_size": {"type": "int", "default": 800},
                    "chunk_overlap": {"type": "int", "default": 150}
                }
            }
        """
        pass
    
    def extract_l0_abstract(self, filename: str, content: str) -> str:
        """
        提取 L0 摘要（可选实现，策略特定）
        
        Args:
            filename: 文件名
            content: 文档内容
            
        Returns:
            L0 摘要字符串
            
        Note:
            默认实现使用通用启发式提取器
            子类可以重写以提供策略特定的提取逻辑
        """
        from core.utils.text_extractor import HeuristicExtractor
        return HeuristicExtractor.extract_l0_abstract(filename, content)
    
    def extract_l1_outline(self, content: str) -> str:
        """
        提取 L1 大纲（可选实现，策略特定）
        
        Args:
            content: 文档内容
            
        Returns:
            L1 大纲字符串
            
        Note:
            默认实现使用通用启发式提取器
            子类可以重写以提供策略特定的提取逻辑
        """
        from core.utils.text_extractor import HeuristicExtractor
        return HeuristicExtractor.extract_l1_outline(content)


class IChunkStrategyManager(ABC):
    """分块策略管理器接口"""
    
    @abstractmethod
    def get_strategy(self, strategy_name: str) -> IChunkStrategy:
        """
        获取指定名称的分块策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            IChunkStrategy 实例
            
        Raises:
            ValueError: 如果策略不存在
        """
        pass
    
    @abstractmethod
    def register_strategy(self, name: str, strategy: IChunkStrategy) -> None:
        """
        注册新的分块策略
        
        Args:
            name: 策略名称
            strategy: 策略实例
        """
        pass
    
    @abstractmethod
    def register_strategy_class(self, name: str, strategy_class: Type[IChunkStrategy]) -> None:
        """
        注册策略类（延迟实例化）
        
        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        pass
    
    @abstractmethod
    def list_strategies(self) -> List[str]:
        """列出所有可用的策略"""
        pass
    
    @abstractmethod
    def get_default_strategy(self) -> str:
        """获取默认策略名称"""
        pass
    
    @abstractmethod
    def set_default_strategy(self, strategy_name: str) -> None:
        """设置默认策略"""
        pass
    
    @abstractmethod
    def get_strategy_metadata(self, strategy_name: str) -> Dict[str, Any]:
        """获取策略的元数据"""
        pass
