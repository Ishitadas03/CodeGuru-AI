import uuid
from sqlalchemy import String, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    """Database model storing uploaded document metadata."""
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    num_chunks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} user_id={self.user_id}>"


class ChatSession(Base, TimestampMixin):
    """Database model representing a RAG chat session."""
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Chat"
    )

    # Relationships
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at.asc()"
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} title={self.title} user_id={self.user_id}>"


class ChatMessage(Base, TimestampMixin):
    """Database model representing a message in a RAG chat session."""
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} session_id={self.session_id} role={self.role}>"
