import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User database model holding core authentication parameters."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    subscription_tier: Mapped[str] = mapped_column(
        String(50),
        default="free",
        nullable=False
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # 1:1 Relationship with Profile
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Relationship to Revocable Sessions
    sessions: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User email={self.email} is_active={self.is_active}>"
