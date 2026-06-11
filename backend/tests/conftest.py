import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.main import app

# Override settings database URI to point to an in-memory SQLite test database
TEST_SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///:memory:"
settings.SQLALCHEMY_DATABASE_URI = TEST_SQLALCHEMY_DATABASE_URI

test_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def init_test_db():
    """Create database tables and clean up on teardown."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a testing database session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide a test client authenticated against the FastAPI app, overriding get_db."""
    async def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
