from __future__ import annotations
import logging
from typing import List

logger = logging.getLogger("codeguru.rag.embedding")


class EmbeddingService:
    """Service to compute BGE embeddings for text chunks and queries using sentence-transformers."""
    
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy-load the BGE model as a singleton."""
        if cls._model is None:
            logger.info("Initializing BGE embedding model: BAAI/bge-small-en-v1.5")
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        return cls._model

    def embed_query(self, text: str) -> List[float]:
        """Generate normalized embedding for a search query (includes query instruction prefix)."""
        model = self.get_model()
        # BGE queries require this instruction prefix for optimal similarity retrieval
        prefix = "Represent this sentence for searching relevant passages: "
        embedding = model.encode(prefix + text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized embeddings for text chunks."""
        if not texts:
            return []
        model = self.get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return [emb.tolist() for emb in embeddings]
