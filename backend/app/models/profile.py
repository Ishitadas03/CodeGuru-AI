import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class Profile(Base, TimestampMixin):
    """User profile database model holding non-sensitive details."""
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    bio: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )
    skills: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=list
    )

    # Relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile"
    )

    def __repr__(self) -> str:
        return f"<Profile first_name={self.first_name} last_name={self.last_name}>"
