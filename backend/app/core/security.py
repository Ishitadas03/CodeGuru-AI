# backend/app/core/security.py
"""JWT token management, password hashing, and security utilities.

Provides symmetric HS256 JWT signing (upgradeable to RS256 with key pair config),
bcrypt password hashing with configurable cost factor, and password strength validation.
"""
from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger("codeguru.security")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a bcrypt hash.

    Returns False on any error rather than propagating exceptions,
    preventing timing oracle attacks.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError) as exc:
        logger.warning("Password verification error: %s", type(exc).__name__)
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with the configured cost factor."""
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_COST_FACTOR)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def validate_password_strength(password: str) -> list[str]:
    """Validate password strength. Returns a list of weakness descriptions.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    weaknesses: list[str] = []

    if len(password) < 8:
        weaknesses.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        weaknesses.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        weaknesses.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        weaknesses.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", password):
        weaknesses.append("Password must contain at least one special character.")

    return weaknesses


def create_access_token(
    subject: Any,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Generate a JWT access token.

    Args:
        subject: The token subject (typically user UUID).
        expires_delta: Custom expiry duration. Defaults to config value.
        extra_claims: Additional JWT claims to embed.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: Any,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a JWT refresh token.

    Refresh tokens use a longer expiry and are stored in the database
    to support revocation and rotation.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> Optional[str]:
    """Decode and verify a JWT token.

    Returns the subject (user ID) if valid, None otherwise.
    Checks both signature validity and token type claim.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_type = payload.get("type")
        if token_type != expected_type:
            logger.debug("Token type mismatch: expected=%s, got=%s", expected_type, token_type)
            return None

        subject: Optional[str] = payload.get("sub")
        if subject is None:
            logger.debug("Token missing 'sub' claim")
            return None

        return subject
    except JWTError as exc:
        logger.debug("JWT verification failed: %s", str(exc))
        return None


def decode_token_payload(token: str) -> Optional[dict[str, Any]]:
    """Decode a JWT token and return the full payload dict.

    Returns None if the token is invalid or expired.
    Useful for extracting claims like 'jti' for token blacklisting.
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        logger.debug("JWT decode failed: %s", str(exc))
        return None
