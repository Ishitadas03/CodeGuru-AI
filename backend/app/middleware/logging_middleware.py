# backend/app/middleware/logging_middleware.py
"""Structured JSON logging middleware with correlation ID propagation and request timing.

Every request is assigned a correlation ID (from header or auto-generated) that is
propagated through all log entries and returned in the response header.
"""
from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request, Response
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware

# --- Logger Configuration ---

log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt=(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(correlation_id)s %(method)s %(path)s %(status_code)s %(duration_ms)s"
    ),
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
log_handler.setFormatter(formatter)

logger = logging.getLogger("codeguru")
logger.handlers.clear()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Suppress noisy third-party loggers
for noisy_logger in ("uvicorn.access", "watchfiles.main"):
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for correlation-ID tracking, structured JSON logging, and request timing.

    Measures request duration (wall clock) and logs it alongside HTTP method,
    path, status code, and correlation ID. The correlation ID is injected into
    request.state for downstream use by exception handlers and service code.
    """

    async def dispatch(self, request: Request, call_next: object) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        # Inject correlation ID into request state for downstream access
        request.state.correlation_id = correlation_id

        try:
            response: Response = await call_next(request)  # type: ignore[arg-type]
            duration_ms = (time.perf_counter() - start_time) * 1000

            log_level = logging.INFO
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING

            logger.log(
                log_level,
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                },
            )

            # Propagate correlation ID back to the client
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-Duration-Ms"] = f"{duration_ms:.2f}"
            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Request failed with unhandled exception: %s",
                str(exc),
                exc_info=True,
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": request.client.host if request.client else "unknown",
                    "exception_type": type(exc).__name__,
                },
            )
            raise
