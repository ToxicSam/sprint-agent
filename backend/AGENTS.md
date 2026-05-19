# Backend Agent Guide

## OVERVIEW
FastAPI + SQLAlchemy 2.0 + SQLite backend for Sprint Agent. No auth, no migrations, zero-mock seeding.

## STRUCTURE
```
backend/
├── main.py              # App factory, lifespan, CORS, router mount
├── database.py          # SQLite engine (WAL mode, check_same_thread=False)
├── models.py            # 8 SQLAlchemy declarative tables
├── schemas.py           # Pydantic v2 request/response models
├── crud.py              # Module-level DB operations
├── routers/             # 7 API route modules
│   ├── sprint.py
│   ├── tasks.py
│   ├── members.py
│   ├── standup.py
│   ├── retro.py
│   ├── agent.py
│   └── settings.py
├── services/
│   ├── import_service.py   # init.json seeding on empty DB
│   ├── export_service.py   # JSON export logic
│   └── agent_service.py    # Regex-based intent classification
└── data/
    └── init.json          # Zero-Mock seed data (required)
```

## WHERE TO LOOK
| Task | File |
|------|------|
| Add a new API endpoint | `routers/*.py` + `schemas.py` |
| Add a DB table | `models.py` + `schemas.py` + `crud.py` |
| Modify seed data | `data/init.json` |
| Change startup behavior | `main.py` lifespan handler |
| Fix agent chat logic | `services/agent_service.py` |

## CONVENTIONS
- **SQLAlchemy 2.0**: Use `Mapped[T]` and `mapped_column()`. All PKs are UUID strings.
- **Pydantic v2**: `XBase` (common), `XCreate` (POST), `XUpdate` (PATCH, all Optional), `XResponse` (adds `id`, `created_at`, `ConfigDict(from_attributes=True)`).
- **CRUD**: Module-level functions, `(db: Session, ...)` first. Updates use `exclude_unset=True` + `setattr` loop.
- **JSON text fields**: `blocked_by` (Task) and `context` (AgentMessage) are raw JSON strings, not native JSON columns.
- **Error handling**: Return `HTTPException(status_code=404)` uniformly for missing entities.
- **No Alembic**: Schema created via `Base.metadata.create_all()` in lifespan. If you change models, existing DBs need manual migration or reset.

## ANTI-PATTERNS
- Do not add auth middleware. The app is intentionally unauthenticated.
- Do not use auto-increment integers for IDs. UUID strings only.
- Do not store sensitive data in `init.json` or rely on CORS in production.
- Do not call `db.commit()` inside CRUD functions that only read.
