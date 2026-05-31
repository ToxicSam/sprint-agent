"""Async SQLAlchemy database engine and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:////tmp/sprint_agent.db"

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # Enable WAL mode for better concurrent performance
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
)


async def create_tables() -> None:
    """Create all tables if they don't exist."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Async generator yielding a database session."""
    async with AsyncSessionLocal() as db:
        yield db
