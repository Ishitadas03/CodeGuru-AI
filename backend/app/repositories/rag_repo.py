import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.rag import Document, ChatSession, ChatMessage


class RAGRepository(BaseRepository[Document]):
    """Repository managing Document, ChatSession, and ChatMessage database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Document, db)

    # Document operations
    async def create_document(
        self,
        *,
        user_id: uuid.UUID,
        filename: str,
        file_size: int,
        num_chunks: int
    ) -> Document:
        """Record details of a new uploaded document."""
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_size=file_size,
            num_chunks=num_chunks
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_document_by_id(self, doc_id: uuid.UUID) -> Optional[Document]:
        """Fetch document metadata by ID."""
        return await self.get(id=doc_id)

    async def get_user_documents(self, user_id: uuid.UUID) -> List[Document]:
        """Fetch all documents uploaded by a user."""
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_document(self, doc_id: uuid.UUID) -> bool:
        """Remove document metadata by ID."""
        doc = await self.get(id=doc_id)
        if doc:
            await self.db.delete(doc)
            await self.db.commit()
            return True
        return False

    # ChatSession operations
    async def create_chat_session(
        self,
        *,
        user_id: uuid.UUID,
        title: str = "New Chat"
    ) -> ChatSession:
        """Initialize a new RAG chat session."""
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_chat_session(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """Retrieve a specific chat session with its messages."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.id == session_id)
            .options(selectinload(ChatSession.messages))
        )
        return result.scalars().first()

    async def get_user_chat_sessions(self, user_id: uuid.UUID) -> List[ChatSession]:
        """Retrieve all chat sessions for a user."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_chat_session(self, session_id: uuid.UUID) -> bool:
        """Delete a chat session and all cascading messages."""
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session = result.scalars().first()
        if session:
            await self.db.delete(session)
            await self.db.commit()
            return True
        return False

    # ChatMessage operations
    async def create_chat_message(
        self,
        *,
        session_id: uuid.UUID,
        role: str,
        content: str
    ) -> ChatMessage:
        """Append a new message to a chat session."""
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def get_session_messages(self, session_id: uuid.UUID) -> List[ChatMessage]:
        """Fetch all messages within a chat session chronologically."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())
