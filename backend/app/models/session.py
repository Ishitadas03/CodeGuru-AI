import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class RefreshToken(Base, TimestampMixin):
    """Database model to track active and revoked JWT refresh tokens."""
    __tablename__ = "refresh_tokens"

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
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True,
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions"
    )

    def __repr__(self) -> str:
        return f"<RefreshToken user_id={self.user_id} is_revoked={self.is_revoked}>"
