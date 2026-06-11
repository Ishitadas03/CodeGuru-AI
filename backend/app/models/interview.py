import uuid
from sqlalchemy import String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class InterviewSession(Base, TimestampMixin):
    """Database model representing a mock technical interview session."""
    __tablename__ = "interview_sessions"

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
    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    messages: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    feedback: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User"
    )

    def __repr__(self) -> str:
        return f"<InterviewSession id={self.id} user_id={self.user_id} topic={self.topic} is_completed={self.is_completed}>"
