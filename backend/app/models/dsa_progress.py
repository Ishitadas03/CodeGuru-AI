import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class UserProblemProgress(Base, TimestampMixin):
    """Database model tracking user progress and codes for DSA problems."""
    __tablename__ = "user_problem_progress"

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
    problem_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )
    topic_slug: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    code: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    solved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="dsa_progresses")

    def __repr__(self) -> str:
        return f"<UserProblemProgress user_id={self.user_id} problem_id={self.problem_id} status={self.status}>"
