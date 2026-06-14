"""Vector storage service backed by Supabase pgvector.

Replaces the previous SQLite-based vector store with a production-grade
PostgreSQL vector extension, suitable for serverless deployments (Vercel).
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import asyncpg

from app.core.config import settings

logger = logging.getLogger("codeguru.rag.vector")

# SQL to ensure the pgvector extension and table exist (idempotent)
_INIT_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS vector_chunks (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL,
    document_id UUID NOT NULL,
    filename TEXT NOT NULL,
    page INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding vector(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vector_chunks_user_id ON vector_chunks (user_id);
CREATE INDEX IF NOT EXISTS idx_vector_chunks_document_id ON vector_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_vector_chunks_embedding ON vector_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
"""


def _get_pool() -> asyncpg.Pool:
    """Create a lightweight connection pool for vector operations."""
    # Use the raw PostgreSQL URL (not asyncpg://) since asyncpg expects postgresql://
    dsn = settings.SQLALCHEMY_DATABASE_URI
    if "+asyncpg" in dsn:
        dsn = dsn.replace("postgresql+asyncpg://", "postgresql://")
    elif dsn.startswith("postgres://"):
        dsn = dsn.replace("postgres://", "postgresql://", 1)
    return asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5)


class VectorService:
    """PostgreSQL pgvector-backed vector storage for RAG embeddings.

    Uses asyncpg directly for efficient serverless-compatible connections.
    Embeddings are stored as pgvector columns with cosine similarity search.
    """

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _ensure_pool(self) -> asyncpg.Pool:
        """Lazy-initialize the connection pool on first use."""
        if self._pool is None:
            self._pool = _get_pool()
            async with self._pool.acquire() as conn:
                await conn.execute(_INIT_SQL)
            logger.info("pgvector connection pool initialized")
        return self._pool

    async def add_chunks(
        self,
        user_id: Any,
        document_id: Any,
        filename: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """Index text chunks with their embeddings into pgvector."""
        pool = await self._ensure_pool()
        user_id_str = str(user_id)
        doc_id_str = str(document_id)

        async with pool.acquire() as conn:
            records = []
            for chunk, emb in zip(chunks, embeddings):
                chunk_id = f"{doc_id_str}_{chunk['chunk_index']}"
                emb_str = "[" + ",".join(str(v) for v in emb) + "]"
                records.append((
                    chunk_id,
                    user_id_str,
                    doc_id_str,
                    filename,
                    chunk["page"],
                    chunk["chunk_index"],
                    chunk["text"],
                    emb_str,
                ))

            await conn.executemany(
                """
                INSERT INTO vector_chunks (id, user_id, document_id, filename, page, chunk_index, text, embedding)
                VALUES ($1, $2::uuid, $3::uuid, $4, $5, $6, $7, $8::vector)
                ON CONFLICT (id) DO UPDATE SET
                    text = EXCLUDED.text,
                    embedding = EXCLUDED.embedding
                """,
                records,
            )

        logger.info(f"Indexed {len(records)} chunks in pgvector for document {doc_id_str}")

    async def query_similar_chunks(
        self,
        user_id: Any,
        query_embedding: List[float],
        k: int = 4,
    ) -> List[Dict[str, Any]]:
        """Find the k most similar chunks using cosine distance."""
        pool = await self._ensure_pool()
        emb_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, text, filename, page, chunk_index, document_id,
                       1 - (embedding <=> $1::vector) AS similarity
                FROM vector_chunks
                WHERE user_id = $2::uuid
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                emb_str,
                str(user_id),
                k,
            )

        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "text": row["text"],
                "metadata": {
                    "document_id": str(row["document_id"]),
                    "user_id": str(user_id),
                    "filename": row["filename"],
                    "page": row["page"],
                    "chunk_index": row["chunk_index"],
                },
                "distance": 1.0 - row["similarity"],
            })

        return results

    async def delete_document_vectors(self, document_id: Any) -> None:
        """Remove all vector chunks associated with a document."""
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM vector_chunks WHERE document_id = $1::uuid",
                str(document_id),
            )
        logger.info(f"Deleted vectors for document {document_id} from pgvector")

    async def close(self) -> None:
        """Close the connection pool gracefully."""
        if self._pool:
            await self._pool.close()
            self._pool = None
