import uuid
from sqlalchemy import String, Integer, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base, TimestampMixin


class PromptVersion(Base, TimestampMixin):
    """Database model storing versioned prompt templates for LLM instructions."""
    __tablename__ = "prompt_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    thumbs_up: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    thumbs_down: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    performance_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<PromptVersion name={self.name} version={self.version} active={self.is_active}>"
