# backend/app/core/exceptions.py
"""RFC 7807 Problem Details error responses and typed exception hierarchy.

All application exceptions extend CodeGuruException, which produces structured
JSON error responses following the Problem Details specification (RFC 7807).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class CodeGuruException(HTTPException):
    """Base exception for all CodeGuru application errors.

    Produces RFC 7807 compliant JSON error responses with:
    - type: URI identifying the error type
    - title: Short human-readable summary
    - status: HTTP status code
    - detail: Specific explanation of this occurrence
    - instance: URI of the request that generated the error
    - request_id: Correlation ID for tracing
    - timestamp: ISO 8601 timestamp
    - errors: Optional list of validation-level errors
    """

    error_type: str = "https://codeguru.ai/errors/internal-error"
    error_title: str = "Internal Server Error"

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: Optional[str] = None,
        error_title: Optional[str] = None,
        errors: Optional[list[dict[str, Any]]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self._error_type = error_type or self.__class__.error_type
        self._error_title = error_title or self.__class__.error_title
        self.errors = errors or []
        super().__init__(status_code=status_code, detail=detail, headers=headers)

    def to_problem_details(
        self,
        request_path: str = "",
        request_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Serialize this exception into an RFC 7807 Problem Details dict."""
        body: dict[str, Any] = {
            "type": self._error_type,
            "title": self._error_title,
            "status": self.status_code,
            "detail": self.detail,
            "instance": request_path,
            "request_id": request_id or str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if self.errors:
            body["errors"] = self.errors
        return body


# --- Typed Exception Classes ---


class AuthError(CodeGuruException):
    """Authentication failure: invalid credentials, expired tokens, etc."""

    error_type = "https://codeguru.ai/errors/authentication-error"
    error_title = "Authentication Error"

    def __init__(self, detail: str = "Authentication failed or insufficient permissions.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(CodeGuruException):
    """Authorization failure: user lacks required role or permission."""

    error_type = "https://codeguru.ai/errors/forbidden"
    error_title = "Forbidden"

    def __init__(self, detail: str = "Access forbidden.") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ValidationError(CodeGuruException):
    """Input validation failure with optional per-field error details."""

    error_type = "https://codeguru.ai/errors/validation-error"
    error_title = "Validation Error"

    def __init__(
        self,
        detail: str = "Invalid input data.",
        errors: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            errors=errors,
        )


class NotFoundError(CodeGuruException):
    """Requested resource does not exist."""

    error_type = "https://codeguru.ai/errors/not-found"
    error_title = "Not Found"

    def __init__(self, detail: str = "Resource not found.") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class RateLimitError(CodeGuruException):
    """Client has exceeded their rate limit allocation."""

    error_type = "https://codeguru.ai/errors/rate-limit-exceeded"
    error_title = "Rate Limit Exceeded"

    def __init__(self, detail: str = "Too many requests. Please try again later.") -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"},
        )


class AIServiceError(CodeGuruException):
    """AI provider failure after exhausting retries and fallbacks."""

    error_type = "https://codeguru.ai/errors/ai-service-error"
    error_title = "AI Service Unavailable"

    def __init__(self, detail: str = "AI service is temporarily unavailable. Please try again.") -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers={"Retry-After": "30"},
        )


class QuotaExceededError(CodeGuruException):
    """User has exhausted their usage quota for the current billing period."""

    error_type = "https://codeguru.ai/errors/quota-exceeded"
    error_title = "Quota Exceeded"

    def __init__(self, detail: str = "You have exceeded your usage quota for this billing period.") -> None:
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
        )


class SubscriptionRequiredError(CodeGuruException):
    """Feature requires a higher subscription tier."""

    error_type = "https://codeguru.ai/errors/subscription-required"
    error_title = "Subscription Required"

    def __init__(
        self,
        detail: str = "This feature requires a Pro or Team subscription.",
        required_tier: str = "pro",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            errors=[{"field": "subscription", "message": detail, "code": f"requires_{required_tier}"}],
        )


class ConflictError(CodeGuruException):
    """Resource state conflict (e.g., duplicate email, concurrent modification)."""

    error_type = "https://codeguru.ai/errors/conflict"
    error_title = "Conflict"

    def __init__(self, detail: str = "Resource conflict.") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# --- Exception Handlers for FastAPI ---


async def codeguru_exception_handler(request: Request, exc: CodeGuruException) -> JSONResponse:
    """Handle all CodeGuruException subclasses with RFC 7807 Problem Details response."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    body = exc.to_problem_details(
        request_path=str(request.url.path),
        request_id=correlation_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=body,
        headers=exc.headers or {},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions with a generic RFC 7807 Problem Details response."""
    import logging

    logger = logging.getLogger("codeguru")
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    logger.error(
        "Unhandled exception: %s",
        str(exc),
        exc_info=True,
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
        },
    )

    body = {
        "type": "https://codeguru.ai/errors/internal-error",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An unexpected server error occurred.",
        "instance": str(request.url.path),
        "request_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(status_code=500, content=body)
