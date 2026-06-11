import uuid
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base, TimestampMixin


class AIUsageRecord(Base, TimestampMixin):
    """Database model storing token usage metrics and cost tracking for AI operations."""
    __tablename__ = "ai_usage_records"

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
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    output_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    estimated_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    def __repr__(self) -> str:
        return f"<AIUsageRecord user_id={self.user_id} model={self.model} cost={self.estimated_cost}>"
