import os
import json
import sqlite3
import asyncio
import logging
from typing import Any, Dict, List

logger = logging.getLogger("codeguru.rag.vector")


class VectorService:
    """SQLite-based lightweight vector store to bypass compilation issues with ChromaDB on Windows."""

    def __init__(self, persist_directory: str = "./db/chromadb", client: Any = None) -> None:
        # We map persist_directory to db_path for SQLite backend
        self.persist_directory = os.path.abspath(persist_directory)
        os.makedirs(self.persist_directory, exist_ok=True)
        self.db_path = os.path.join(self.persist_directory, "vector_store.db")
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_chunks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON vector_chunks (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_id ON vector_chunks (document_id)")
            conn.commit()

    def _add_chunks_sync(
        self,
        user_id_str: str,
        doc_id_str: str,
        filename: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for chunk, emb in zip(chunks, embeddings):
                idx = chunk["chunk_index"]
                chunk_id = f"{doc_id_str}_{idx}"
                emb_json = json.dumps(emb)
                cursor.execute("""
                    INSERT OR REPLACE INTO vector_chunks 
                    (id, user_id, document_id, filename, page, chunk_index, text, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (chunk_id, user_id_str, doc_id_str, filename, chunk["page"], idx, chunk["text"], emb_json))
            conn.commit()
        logger.info(f"Indexed {len(chunks)} chunks in SQLite vector store for document {doc_id_str}")

    async def add_chunks(
        self,
        user_id: Any,
        document_id: Any,
        filename: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> None:
        """Asynchronously index chunks and embeddings in SQLite vector store."""
        await asyncio.to_thread(
            self._add_chunks_sync,
            str(user_id),
            str(document_id),
            filename,
            chunks,
            embeddings
        )

    def _query_similar_chunks_sync(
        self,
        user_id_str: str,
        query_embedding: List[float],
        k: int
    ) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, text, filename, page, chunk_index, document_id, embedding
                FROM vector_chunks
                WHERE user_id = ?
            """, (user_id_str,))
            rows = cursor.fetchall()

        if not rows:
            return []

        scored_chunks = []
        for row in rows:
            chunk_id, text, filename, page, chunk_index, doc_id, emb_json = row
            emb = json.loads(emb_json)
            
            # Cosine similarity for normalized vectors is simply the dot product
            dot_product = sum(q * e for q, e in zip(query_embedding, emb))
            distance = 1.0 - dot_product
            
            scored_chunks.append({
                "id": chunk_id,
                "text": text,
                "metadata": {
                    "document_id": doc_id,
                    "user_id": user_id_str,
                    "filename": filename,
                    "page": page,
                    "chunk_index": chunk_index
                },
                "distance": distance
            })

        scored_chunks.sort(key=lambda x: x["distance"])
        return scored_chunks[:k]

    async def query_similar_chunks(
        self,
        user_id: Any,
        query_embedding: List[float],
        k: int = 4
    ) -> List[Dict[str, Any]]:
        """Asynchronously query SQLite vector store for similar chunks belonging to the user."""
        return await asyncio.to_thread(
            self._query_similar_chunks_sync,
            str(user_id),
            query_embedding,
            k
        )

    def _delete_document_vectors_sync(self, doc_id_str: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vector_chunks WHERE document_id = ?", (doc_id_str,))
            conn.commit()
        logger.info(f"Deleted all vectors for document {doc_id_str} from SQLite vector store")

    async def delete_document_vectors(self, document_id: Any) -> None:
        """Asynchronously remove all vectors associated with a document."""
        await asyncio.to_thread(self._delete_document_vectors_sync, str(document_id))
