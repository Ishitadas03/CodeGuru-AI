"""Embedding service using OpenAI embeddings API.

Replaces the local sentence-transformers BGE model with OpenAI's text-embedding-3-small,
which is serverless-friendly and avoids the 2GB+ model download on cold starts.
"""
from __future__ import annotations

import logging
from typing import List

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger("codeguru.rag.embedding")

# OpenAI text-embedding-3-small produces 1536-dim vectors by default.
# We use 384 dims to match the pgvector column and reduce storage costs.
EMBEDDING_DIM = 384


class EmbeddingService:
    """Compute text embeddings via OpenAI's embedding API.

    Falls back gracefully if the API key is not configured, returning
    zero vectors so downstream code doesn't crash during development.
    """

    _client: OpenAI | None = None

    @classmethod
    def _get_client(cls) -> OpenAI | None:
        if cls._client is None:
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not set — embeddings will return zero vectors")
                return None
            cls._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return cls._client

    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a search query."""
        client = self._get_client()
        if client is None:
            return [0.0] * EMBEDDING_DIM

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=EMBEDDING_DIM,
        )
        return response.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of text chunks."""
        if not texts:
            return []

        client = self._get_client()
        if client is None:
            return [[0.0] * EMBEDDING_DIM for _ in texts]

        # OpenAI supports batch embedding (up to 2048 per request)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
            dimensions=EMBEDDING_DIM,
        )
        return [item.embedding for item in response.data]
