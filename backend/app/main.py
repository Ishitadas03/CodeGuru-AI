from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import CodeGuruException
from app.api.v1.router import api_router
from app.middleware.rate_limit import limiter
from app.middleware.logging_middleware import LoggingMiddleware, logger
from app.database.session import engine
from app.database.base import Base
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI startup and shutdown operations."""
    logger.info("Initializing CodeGuru AI Application context...")
    # Automatically initialize SQLite database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Tearing down CodeGuru AI Application context...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up slowapi rate limiter configuration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
# Allow credentials, requests from local developments or specific frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging and Correlation-ID middleware
app.add_middleware(LoggingMiddleware)


# Global CodeGuru exception handler mapping custom exceptions directly to JSON responses
@app.exception_handler(CodeGuruException)
async def codeguru_exception_handler(request: Request, exc: CodeGuruException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Global unhandled error caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."}
    )


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["monitoring"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


# Include V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
