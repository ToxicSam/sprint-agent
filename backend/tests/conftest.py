"""
Pytest configuration and shared fixtures for Sprint Agent backend tests.

Uses a synchronous in-memory SQLite database (the backend uses sync SQLAlchemy)
but provides an httpx.AsyncClient for async HTTP testing against the FastAPI app.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import date

# Must import the FastAPI app and dependency before overriding
from main import app
from database import get_db
from models import Base

# ---------------------------------------------------------------------------
# Engine + Session factory for the in-memory test DB
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_tables():
    """Create all tables once at the start of the test session; drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh database session for each test.

    The session is rolled back after each test so tests stay isolated.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    # Enforce foreign keys in SQLite
    session.execute(text("PRAGMA foreign_keys=ON"))

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest_asyncio.fixture
async def client(db_session):
    """Return an httpx.AsyncClient that talks to the FastAPI app.

    The get_db dependency is overridden so every endpoint uses *our*
    db_session fixture, guaranteeing test isolation.
    """

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass  # session cleanup handled by db_session fixture

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper fixtures: pre-populate common entities
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def sample_sprint(db_session):
    """Create a sample active sprint."""
    import crud
    from schemas import SprintCreate

    sprint = crud.create_sprint(
        db_session,
        SprintCreate(
            name="Test Sprint",
            goal="Test sprint goal",
            start_date=date.today(),
            status="active",
        ),
    )
    return sprint


@pytest_asyncio.fixture
async def sample_member(db_session):
    """Create a sample team member."""
    import crud
    from schemas import MemberCreate

    member = crud.create_member(
        db_session,
        MemberCreate(name="Alice", role="dev", capacity=8.0),
    )
    return member


@pytest_asyncio.fixture
async def sample_task(db_session, sample_sprint, sample_member):
    """Create a sample task linked to the sample sprint and member."""
    import crud
    from schemas import TaskCreate

    task = crud.create_task(
        db_session,
        TaskCreate(
            title="Test Task",
            sprint_id=sample_sprint.id,
            assignee_id=sample_member.id,
            status="todo",
            priority=1,
            story_points=5.0,
        ),
    )
    return task
