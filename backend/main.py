from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables, engine
from models import Base
from services.import_service import load_init_data
from sqlalchemy.orm import Session

from routers import sprint, tasks, members, standup, retro, agent, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    with Session(engine) as db:
        load_init_data(db)
    yield


app = FastAPI(
    title="Sprint Agent Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sprint.router)
app.include_router(tasks.router)
app.include_router(members.router)
app.include_router(standup.router)
app.include_router(retro.router)
app.include_router(agent.router)
app.include_router(settings.router)
