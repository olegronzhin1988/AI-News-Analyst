# conftest.py - test fixtures

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from database import Base, get_db

# Test database
TEST_DATABASE_URL= "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession)

# Create in-memory SQLite tables before tests and drop them after
@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    
# Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Drop all tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Create session and pass to test
@pytest.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

# creates client and switches get_db for test db
@pytest.fixture(scope="function")
async def client( db_session: AsyncSession):

# dependency override
    async def override_get_db():
        yield db_session

# Create client with ASGI transport for FastAPI testing
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# Clean up the override    
    app.dependency_overrides.clear()