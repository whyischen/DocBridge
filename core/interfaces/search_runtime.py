from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISearchRuntime(ABC):
    @abstractmethod
    def upsert(self, collection_name: str, doc_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        """底层写入：插入或更新单条向量和元数据"""
        pass

    @abstractmethod
    def upsert_batch(self, collection_name: str, doc_ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]) -> bool:
        """底层写入：批量插入或更新多条向量和元数据"""
        pass

    @abstractmethod
    def delete_by_uri(self, collection_name: str, uri: str) -> bool:
        """底层删除：根据 URI 删除文档"""
        pass

    @abstractmethod
    def hybrid_search(self, collection_name: str, query_text: str, top_k: int = 5, where: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """底层检索：执行向量与关键词的混合检索"""
        pass

    @abstractmethod
    def get_all_metadatas(self, collection_name: str) -> List[Dict[str, Any]]:
        """获取所有文档的元数据"""
        pass
