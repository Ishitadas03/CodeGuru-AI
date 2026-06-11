import uuid
from sqlalchemy import Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class CodeReview(Base, TimestampMixin):
    """Database model storing structured code review feedback and refactoring recommendations."""
    __tablename__ = "code_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    issues: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    refactored_code: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    has_bugs: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    bugs: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    static_analysis: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        default=dict
    )

    # Relationships
    submission: Mapped["Submission"] = relationship(
        "Submission",
        back_populates="reviews"
    )

    def __repr__(self) -> str:
        return f"<CodeReview id={self.id} score={self.score} has_bugs={self.has_bugs}>"
