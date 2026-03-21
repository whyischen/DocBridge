import logging
from typing import List, Dict, Any
from rich.console import Console
from core.interfaces.search_runtime import ISearchRuntime
from core.i18n import t

logger = logging.getLogger(__name__)
console = Console(stderr=True)

class QMDRuntime(ISearchRuntime):
    def __init__(self, config):
        self.endpoint = config.get("qmd", {}).get("endpoint", "http://localhost:9791")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        self.config = config
        self.client = None
        self.collection = None
        self._initialized = False
        
        # 延迟初始化 ChromaDB，避免解释器关闭时的竞态条件
        logger.info("⚙️ QMD runtime configured for embedded mode (lazy initialization)")
    
    def _ensure_initialized(self):
        """延迟初始化 ChromaDB，在第一次使用时调用"""
        if self._initialized:
            return
        
        try:
            logger.info("⚙️ Initializing embedded QMD engine (based on ChromaDB)...")
            from core.utils.model_downloader import ensure_chroma_model
            ensure_chroma_model()
            
            import chromadb
            from chromadb.config import Settings
            import os
            from pathlib import Path
            
            workspace_dir = Path(os.path.expanduser(self.config.get("workspace_dir", "~/.cbridge/workspace")))
            db_path = workspace_dir / "qmd_embedded"
            db_path.mkdir(parents=True, exist_ok=True)
            
            # Configure ChromaDB to use our custom models directory
            models_dir = Path.home() / ".cbridge" / "models"
            
            # Use new Chroma client initialization with Settings
            settings = Settings(
                is_persistent=True,
                persist_directory=str(db_path),
                anonymized_telemetry=False,
            )
            
            self.client = chromadb.Client(settings)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            self._initialized = True
        except Exception as e:
            console.print(f"[bold red]Failed to initialize embedded QMD: {e}[/bold red]")
            logger.error(f"QMD initialization error: {e}", exc_info=True)
            raise

    def upsert(self, collection_name: str, doc_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        try:
            self._ensure_initialized()
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            text = payload.pop("text", "")
            self.collection.upsert(
                documents=[text],
                metadatas=[payload],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error upserting document {doc_id}: {e}", exc_info=True)
            return False

    def upsert_batch(self, collection_name: str, doc_ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]) -> bool:
        try:
            self._ensure_initialized()
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            
            texts = []
            clean_payloads = []
            for p in payloads:
                # payload might be original object or copy, safest to make a copy
                p_copy = p.copy()
                texts.append(p_copy.pop("text", ""))
                clean_payloads.append(p_copy)
                
            self.collection.upsert(
                documents=texts,
                metadatas=clean_payloads,
                ids=doc_ids
            )
            return True
        except Exception as e:
            logger.error(f"Error bulk upserting documents: {e}", exc_info=True)
            return False

    def delete_by_uri(self, collection_name: str, uri: str) -> bool:
        try:
            self._ensure_initialized()
            if not self.collection:
                logger.error("Collection not initialized")
                return False
            self.collection.delete(where={"uri": uri})
            return True
        except Exception as e:
            logger.error(f"Error deleting document with uri {uri}: {e}", exc_info=True)
            return False

    def hybrid_search(self, collection_name: str, query_text: str, top_k: int = 5, where: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            self._ensure_initialized()
            if not self.collection:
                logger.error("Collection not initialized")
                return []

            query_args = {
                "query_texts": [query_text],
                "n_results": top_k
            }
            if where:
                query_args["where"] = where

            results = self.collection.query(**query_args)
            
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    # ChromaDB returns distances (lower = more similar)
                    # Convert to similarity score (higher = more similar)
                    distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 1.0
                    # Convert distance to similarity: 1 / (1 + distance)
                    # This maps: distance 0 -> similarity 1.0, distance ∞ -> similarity 0.0
                    similarity = 1.0 / (1.0 + distance)
                    
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": similarity,
                        "distance": distance  # Keep original distance for debugging
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching: {e}", exc_info=True)
            return []

    def get_all_metadatas(self, collection_name: str) -> List[Dict[str, Any]]:
        try:
            self._ensure_initialized()
            if not self.collection:
                logger.error("Collection not initialized")
                return []
            results = self.collection.get(include=["metadatas"])
            if results and "metadatas" in results and results["metadatas"]:
                return [meta for meta in results["metadatas"] if meta]
        except Exception as e:
            logger.error(f"Error getting metadatas from ChromaDB: {e}", exc_info=True)
        return []
