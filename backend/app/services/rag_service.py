import uuid
import logging
from typing import Any, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.rag_repo import RAGRepository
from app.services.pdf_service import PDFService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.ai.router import AIRouter
from app.ai.prompts.rag_prompts import RAG_SYSTEM_INSTRUCTION, RAG_USER_PROMPT
from app.models.rag import Document, ChatSession, ChatMessage

logger = logging.getLogger("codeguru.rag.service")


class RAGService:
    """Orchestrator coordinating text extraction, embedding, vector storage, and RAG chat generation."""

    def __init__(self) -> None:
        self.pdf_service = PDFService()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.ai_router = AIRouter()

    async def upload_document(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        filename: str,
        file_bytes: bytes
    ) -> Document:
        """Parse, chunk, embed, index, and record a new PDF document."""
        logger.info(f"Processing PDF upload '{filename}' for user: {user_id}")
        
        # 1. Extract text and page numbers
        pages = self.pdf_service.extract_text_from_pdf(file_bytes)
        
        # 2. Chunk text
        chunks = self.pdf_service.chunk_pages(pages)
        if not chunks:
            raise ValueError("No text could be extracted from the uploaded PDF.")
        
        # 3. Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.embed_documents(chunk_texts)
        
        # 4. Save metadata to SQL DB
        repo = RAGRepository(db)
        doc = await repo.create_document(
            user_id=user_id,
            filename=filename,
            file_size=len(file_bytes),
            num_chunks=len(chunks)
        )
        
        # 5. Index chunks in pgvector
        await self.vector_service.add_chunks(
            user_id=user_id,
            document_id=doc.id,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings
        )
        
        return doc

    async def delete_document(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        document_id: uuid.UUID
    ) -> bool:
        """Delete document metadata and remove its indexed vectors from pgvector."""
        repo = RAGRepository(db)
        doc = await repo.get_document_by_id(document_id)
        if not doc or doc.user_id != user_id:
            return False

        # Remove from ChromaDB first
        await self.vector_service.delete_document_vectors(document_id)
        
        # Remove metadata from SQL
        return await repo.delete_document(document_id)

    async def query_chat(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        message_content: str
    ) -> Tuple[ChatMessage, List[Dict[str, Any]]]:
        """Submit query, retrieve relevant contexts, call LLM with grounding, and save message thread."""
        repo = RAGRepository(db)
        
        # Verify session ownership
        session = await repo.get_chat_session(session_id)
        if not session or session.user_id != user_id:
            raise PermissionError("User does not have access to this chat session.")

        # 1. Save user query in SQL DB
        user_msg = await repo.create_chat_message(
            session_id=session_id,
            role="user",
            content=message_content
        )

        # 2. Embed the query
        query_embedding = self.embedding_service.embed_query(message_content)

        # 3. Retrieve similar chunks from pgvector
        similar_chunks = await self.vector_service.query_similar_chunks(
            user_id=user_id,
            query_embedding=query_embedding,
            k=4
        )

        # 4. Format context blocks
        context_parts = []
        sources = []
        for chunk in similar_chunks:
            meta = chunk.get("metadata", {})
            fname = meta.get("filename", "unknown")
            page = meta.get("page", 1)
            
            context_parts.append(
                f"Source: {fname} (Page {page})\n"
                f"Content: {chunk.get('text', '')}"
            )
            
            sources.append({
                "filename": fname,
                "page": page,
                "score": float(chunk.get("distance", 1.0))
            })

        context_str = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant document context found."

        # 5. Format prompt and call Gemini via router
        prompt = RAG_USER_PROMPT.format(
            context=context_str,
            query=message_content
        )

        try:
            response_text, model_used = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                system_instruction=RAG_SYSTEM_INSTRUCTION,
                schema=None,
                complexity="simple"
            )
        except Exception as e:
            logger.error(f"Failed to generate RAG answer via AI router: {e}", exc_info=True)
            response_text = "I encountered an error generating an answer. Please check if services are available."

        # 6. Save assistant answer in SQL DB
        assistant_msg = await repo.create_chat_message(
            session_id=session_id,
            role="assistant",
            content=response_text
        )

        return assistant_msg, sources
