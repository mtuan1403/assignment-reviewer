from typing import List, Optional, Dict, Any
import math
import re
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk

logger = get_logger(__name__)


class LightweightTFIDFEmbedder:
    """
    Fast, deterministic offline vectorizer that doesn't require internet or pre-downloaded weights.
    Used seamlessly when sentence-transformers weights are not cached locally.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed_text(self, text: str) -> List[float]:
        tokens = re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text.lower())
        if not tokens:
            return [0.0] * self.dim

        vec = [0.0] * self.dim
        for token in tokens:
            idx = hash(token) % self.dim
            vec[idx] += 1.0

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def __call__(self, input: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in input]


class ChromaVectorStore:
    def __init__(self, persist_directory: Optional[Path] = None):
        self.persist_dir = persist_directory or settings.vector_store_dir
        self.client = None
        self._embedding_fn = None
        self._init_store()

    def _init_store(self):
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"Initialized ChromaDB persistent client at: {self.persist_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB PersistentClient: {e}")
            raise e

        # Initialize embedding function
        if settings.EMBEDDING_PROVIDER == "sentence-transformers":
            try:
                from chromadb.utils import embedding_functions

                self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=settings.EMBEDDING_MODEL
                )
                logger.info(f"Using SentenceTransformerEmbeddingFunction ({settings.EMBEDDING_MODEL})")
            except Exception as e:
                logger.warning(
                    f"Could not load local sentence-transformers model ({e}). "
                    f"Falling back to deterministic lightweight embedder."
                )
                self._embedding_fn = LightweightTFIDFEmbedder()
        else:
            self._embedding_fn = LightweightTFIDFEmbedder()

    def _get_collection(self, review_id: str):
        collection_name = f"review_{re.sub(r'[^a-zA-Z0-9_-]', '_', review_id)}"
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def index_chunks(self, review_id: str, chunks: List[DocumentChunk]) -> int:
        if not chunks:
            return 0

        collection = self._get_collection(review_id)

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "page": c.page,
                "section": c.section,
                "document_type": c.document_type.value,
                "token_count": c.token_count,
            }
            for c in chunks
        ]

        # Upsert in batches of 100
        batch_size = 100
        total = len(chunks)
        for i in range(0, total, batch_size):
            end = min(i + batch_size, total)
            collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end],
            )

        logger.info(f"Successfully indexed {total} chunks into collection for review {review_id}.")
        return total

    def query_similar(
        self,
        review_id: str,
        query_text: str,
        top_k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        collection = self._get_collection(review_id)
        count = collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)

        query_args: Dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": actual_k,
        }
        if filter_metadata:
            query_args["where"] = filter_metadata

        results = collection.query(**query_args)

        retrieved: List[DocumentChunk] = []
        if results and "ids" in results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0] if "documents" in results and results["documents"] else []
            metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []

            for i, chunk_id in enumerate(ids):
                meta = metas[i] if i < len(metas) else {}
                doc_text = docs[i] if i < len(docs) else ""
                doc_type_val = meta.get("document_type", DocumentType.STUDENT_DRAFT.value)

                retrieved.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_type=DocumentType(doc_type_val),
                        page=int(meta.get("page", 1)),
                        section=str(meta.get("section", "General")),
                        text=doc_text,
                        token_count=int(meta.get("token_count", len(doc_text.split()))),
                    )
                )

        return retrieved

    def get_all_chunks(self, review_id: str) -> List[DocumentChunk]:
        collection = self._get_collection(review_id)
        results = collection.get()
        chunks: List[DocumentChunk] = []

        if results and "ids" in results and results["ids"]:
            for i, chunk_id in enumerate(results["ids"]):
                meta = results["metadatas"][i] if "metadatas" in results and results["metadatas"] else {}
                text = results["documents"][i] if "documents" in results and results["documents"] else ""
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_type=DocumentType(meta.get("document_type", DocumentType.STUDENT_DRAFT.value)),
                        page=int(meta.get("page", 1)),
                        section=str(meta.get("section", "General")),
                        text=text,
                        token_count=int(meta.get("token_count", len(text.split()))),
                    )
                )

        chunks.sort(key=lambda c: (c.page, c.chunk_id))
        return chunks

    def delete_collection(self, review_id: str):
        collection_name = f"review_{re.sub(r'[^a-zA-Z0-9_-]', '_', review_id)}"
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted vector collection {collection_name}")
        except Exception as e:
            logger.warning(f"Could not delete collection {collection_name}: {e}")
