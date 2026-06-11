import uuid
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class Submission(Base, TimestampMixin):
    """Database model storing user code submissions before analysis."""
    __tablename__ = "submissions"

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
    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    code: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Relationships
    reviews: Mapped[list["CodeReview"]] = relationship(
        "CodeReview",
        back_populates="submission",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Submission id={self.id} language={self.language} user_id={self.user_id}>"
