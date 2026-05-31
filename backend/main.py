"""FastAPI async application with LLM-ready lifespan."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_engine, AsyncSessionLocal, create_tables
from services.import_service import load_init_data

from routers import sprint, tasks, members, standup, retro, agent, settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables + init data."""
    db_path = "./sprint_agent.db"

    if not os.path.exists(db_path):
        logger.info("Fresh database detected, creating tables...")
        await create_tables()
    else:
        logger.info("Existing database detected, ensuring tables...")
        await create_tables()

    # Load initial data if the database is empty
    async with AsyncSessionLocal() as session:
        await load_init_data(session)

    yield

    # Shutdown: dispose engine
    await async_engine.dispose()


app = FastAPI(
    title="Sprint Agent Backend",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers (paths unchanged for front-end compatibility)
app.include_router(sprint.router)
app.include_router(tasks.router)
app.include_router(members.router)
app.include_router(standup.router)
app.include_router(retro.router)
app.include_router(agent.router)
app.include_router(settings.router)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)},
    )
