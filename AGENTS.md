# Sprint Agent — Agent Guide

This file contains everything an AI coding agent needs to know to work effectively on the Sprint Agent project. All information here is derived from the actual codebase, not assumptions.

---

## Project Overview

Sprint Agent is a full-stack Scrum management tool with an AI agent assistant. It is designed around the philosophy of eliminating friction from daily Scrum workflows.

- **Frontend**: React 19 + TypeScript (strict mode) + Vite 7 + Tailwind CSS v3 + shadcn/ui
- **Backend**: FastAPI + SQLAlchemy 2.0 + SQLite + Pydantic v2, running on Python 3.12
- **Deployment**: Docker Compose (backend + nginx frontend), or static hosting of the frontend build

The project follows a **Zero-Mock Data** philosophy: instead of shipping with hardcoded demo data, the backend seeds itself from `backend/data/init.json` on first startup if the database is empty. This makes the app production-ready from the first launch.

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19 | UI framework |
| TypeScript | ~5.9.3 | Type safety (strict mode enabled) |
| Vite | 7 | Build tool and dev server |
| Tailwind CSS | 3.4.19 | Utility-first styling |
| shadcn/ui | latest | Accessible UI primitives (Radix-based) |
| @dnd-kit | latest | Drag-and-drop (Kanban board) |
| TanStack Table | v8 | Standup batch-edit table |
| Zustand | v5 | Global state management |
| react-router-dom | v7 | Hash-based client routing |
| date-fns | v4 | Date manipulation |
| sonner | v2 | Toast notifications |
| recharts | v2 | Charts |
| lucide-react | latest | Icons |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Runtime |
| FastAPI | 0.109.0 | Async API framework |
| SQLAlchemy | 2.0.25 | ORM |
| Pydantic | 2.5.3 | Validation and serialization |
| SQLite | 3.x | Embedded database |
| Uvicorn | 0.27.0 | ASGI server |
| Alembic | 1.13.1 | Migrations (available in deps but unused) |
| python-multipart | 0.0.6 | File uploads |
| httpx | 0.26.0 | HTTP client |
| python-dateutil | 2.8.2 | Date parsing |

---

## Project Structure

```
sprint-agent/
├── backend/                      # FastAPI backend
│   ├── main.py                   # App factory, lifespan, CORS, router mounting
│   ├── database.py               # SQLAlchemy engine + session factory
│   ├── models.py                 # 8 SQLAlchemy ORM tables
│   ├── schemas.py                # Pydantic v2 request/response models
│   ├── crud.py                   # Database CRUD operations
│   ├── requirements.txt          # Python dependencies
│   ├── routers/                  # 7 API route modules
│   │   ├── sprint.py
│   │   ├── tasks.py
│   │   ├── members.py
│   │   ├── standup.py
│   │   ├── retro.py
│   │   ├── agent.py
│   │   └── settings.py
│   ├── services/                 # Business logic layer
│   │   ├── import_service.py     # init.json seeding on startup
│   │   ├── export_service.py     # JSON export logic
│   │   └── agent_service.py      # Rule-based intent classification + context builder
│   └── data/
│       └── init.json             # Zero-Mock seed data (required)
├── frontend/                     # React + TypeScript frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts            # base: './', port 3000, @ alias
│   ├── tailwind.config.js        # Custom design tokens + dark mode
│   ├── tsconfig.app.json         # Strict mode, ES2022, JSX react-jsx
│   ├── eslint.config.js          # Flat config, TS + React hooks + refresh
│   ├── postcss.config.js         # Tailwind + autoprefixer
│   ├── components.json           # shadcn/ui config (style: new-york, baseColor: slate)
│   └── src/
│       ├── main.tsx              # Entry point (HashRouter, no StrictMode)
│       ├── App.tsx               # Route definitions
│       ├── index.css             # Tailwind directives + CSS variables
│       ├── pages/                # Route-level pages
│       │   ├── Dashboard.tsx     # Kanban board with DnD
│       │   ├── Planning.tsx      # Sprint planning
│       │   ├── Standup.tsx       # Excel-like batch-edit table
│       │   ├── Retro.tsx         # Retro scoring + voting
│       │   ├── Settings.tsx      # Import/export, config, team
│       │   └── Login.tsx         # Role selection screen
│       ├── components/           # Reusable components
│       │   ├── Layout.tsx        # Page shell (sidebar, navbar, agent panel)
│       │   ├── Navbar.tsx
│       │   ├── Sidebar.tsx
│       │   ├── BottomBar.tsx
│       │   ├── AgentPanel.tsx    # Docked AI chat panel
│       │   ├── TaskCard.tsx
│       │   ├── KanbanColumn.tsx
│       │   ├── SprintHeader.tsx
│       │   ├── SlideOver.tsx     # Task detail editor
│       │   ├── InlineTaskCreator.tsx
│       │   └── ui/               # ~50 shadcn/ui primitives
│       ├── store/
│       │   └── index.ts          # Single Zustand store with persist middleware
│       ├── types/
│       │   └── index.ts          # All TypeScript interfaces and enums
│       ├── api/                  # API client layer
│       │   ├── client.ts         # Smart fetch wrapper + offline localStorage fallback
│       │   ├── sprint.ts
│       │   ├── tasks.ts
│       │   ├── members.ts
│       │   ├── standup.ts
│       │   ├── retro.ts
│       │   ├── agent.ts
│       │   └── index.ts          # Re-exports
│       ├── hooks/
│       │   ├── use-mobile.ts
│       │   └── useKeyboardNavigation.ts
│       └── lib/
│           └── utils.ts          # cn() utility (clsx + tailwind-merge)
├── docs/                         # Detailed documentation
│   ├── API.md                    # Full REST API reference
│   ├── ARCHITECTURE.md           # System architecture diagrams
│   ├── BACKEND.md                # Backend specifics and conventions
│   ├── CHANGELOG.md              # Version history
│   ├── DATA_FORMAT.md            # init.json schema spec
│   ├── DEPLOY.md                 # Deployment guide
│   ├── FRONTEND.md               # Frontend architecture
│   ├── PUBLISH.md                # Release guide
│   ├── USAGE.md                  # End-user manual
│   └── UX_DESIGN.md              # UX principles and testing methodology
├── scripts/
│   └── test_framework.py         # Multi-agent UX simulation framework
├── docker-compose.yml            # Backend + nginx frontend
├── Dockerfile                    # Python 3.12-slim backend image
├── requirements.txt              # Root-level Python deps (same as backend/)
└── README.md                     # Human-facing quick start and overview
```

---

## Build and Run Commands

### Development

**Backend**
```bash
cd backend
# Create virtual environment (project root has .venv already)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- API docs: `http://localhost:8000/docs`
- Health check: `GET http://localhost:8000/api/health`

**Frontend**
```bash
cd frontend
npm install
npm run dev       # http://localhost:3000 (vite.config.ts sets port 3000)
```
- `npm run build` — TypeScript check + Vite production build → `frontend/dist/`
- `npm run lint` — ESLint check
- `npm run preview` — Preview production build

### Docker Compose (Production)

```bash
docker compose up --build -d
```
- Frontend (nginx): `http://localhost:3000`
- Backend API: `http://localhost:8000`
- The frontend `dist/` folder is mounted into nginx; you must build the frontend first.

---

## Database Architecture

SQLite file (`./sprint_agent.db` from backend working dir) with WAL mode (`check_same_thread=False`).

All primary keys are UUID strings (`default=lambda: str(uuid.uuid4())`). There are 8 tables:

| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| `sprints` | Sprint definitions | 1:N tasks, daily_logs, retros, retro_ratings |
| `members` | Team members | 1:N tasks, daily_logs |
| `tasks` | Scrum tasks | N:1 sprint, N:1 member (assignee) |
| `daily_logs` | Standup entries | N:1 sprint, N:1 member |
| `retros` | Retro feedback items | N:1 sprint |
| `retro_ratings` | Dimension ratings (1-5) | N:1 sprint |
| `agent_messages` | Chat history | Standalone |
| `config` | Key-value settings | Standalone |

**Important**: There is no Alembic migration setup. Schema is created via `Base.metadata.create_all()` on every startup in the lifespan handler. `blocked_by` (Task) and `context` (AgentMessage) are stored as raw JSON text strings, not native JSON columns.

---

## API Architecture

Seven routers are mounted in `main.py` without additional path prefixes (each router defines its own):

| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| sprint | `/api/sprint` | CRUD + stats |
| tasks | `/api/tasks` | CRUD + move + bulk-update + blockers |
| members | `/api/members` | CRUD |
| standup | `/api/standup` | Get logs, batch submit, yesterday lookup |
| retro | `/api/retro` | Items, vote, rate, report |
| agent | `/api/agent` | Message, history, action, context |
| settings | `/api` | Settings, import, export, reset, health |

CORS is currently configured with `allow_origins=["*"]` (development only).

There is **no authentication middleware** in the backend.

---

## Code Style Guidelines

### Frontend

- **TypeScript strict mode is enforced** (`strict: true` in `tsconfig.app.json`).
- Use `noUnusedLocals` and `noUnusedParameters` — the compiler will error on unused variables.
- Prefer the `cn()` utility from `@/lib/utils` for conditional class merging.
- Zustand selectors should be granular to avoid re-renders: `useStore(s => s.tasks)`.
- Components use functional style with hooks.
- Path alias `@/` maps to `frontend/src/`.
- shadcn/ui components live in `components/ui/`.
- ESLint flat config extends `@eslint/js/recommended`, `typescript-eslint/recommended`, `eslint-plugin-react-hooks`, and `eslint-plugin-react-refresh`.

### Backend

- SQLAlchemy 2.0 declarative style with `Mapped` and `mapped_column`.
- Pydantic v2 schemas follow a naming convention:
  - `XBase` — common fields
  - `XCreate` — inherits XBase
  - `XUpdate` — all-optional fields for PATCH semantics
  - `XResponse` — inherits XBase, adds `id` and `created_at`, uses `ConfigDict(from_attributes=True)`
- CRUD functions are module-level (not class-based), accepting `(db: Session, ...)` as the first argument(s).
- Updates use `exclude_unset=True` and iterate with `setattr` for PATCH behavior.
- Return `HTTPException(status_code=404)` uniformly when entities are not found.

---

## Testing Instructions

**There are no traditional unit or integration test files in the repository** (no `pytest` files in `backend/`, no `.test.*` files in `frontend/src/`).

The sole testing artifact is:

- `scripts/test_framework.py` — A **Multi-Agent UX Testing Framework** that simulates multiple users (UX Officer, Scrum Master, 2 Developers) interacting with the backend in-memory. It scores workflow efficiency and outputs a JSON report.

To run it:
```bash
cd scripts
python test_framework.py
```

If you add real tests:
- Backend: `pytest` with `httpx.TestClient` or `fastapi.testclient.TestClient` is the documented intended approach.
- Frontend: The README mentions `pnpm test`, but no test runner (Vitest/Jest) is currently installed.

---

## Key Development Conventions

1. **Zero-Mock Data**: The backend seeds from `backend/data/init.json` only if the DB is empty (checked by looking for any Sprint row). Do not add mock data to the frontend code.
2. **Offline Fallback**: The frontend API client (`api/client.ts`) detects backend availability via `/api/health`. If unreachable, it falls back to a `localStorage`-based mock API so the UI remains functional.
3. **HashRouter**: The frontend uses `HashRouter` so it can be deployed as static files without server-side routing configuration.
4. **UUID Everywhere**: All entity IDs are UUID strings. Do not use auto-increment integers.
5. **Agent Service is Rule-Based**: `services/agent_service.py` uses regex for intent classification and entity extraction. It is designed to be LLM-ready in the future, but currently has no external LLM dependency.
6. **Reset Endpoint**: `POST /api/reset` drops all tables, recreates them, and reloads `init.json`. This is powerful and has no authentication guard.

---

## Security Considerations

- **No authentication**: The backend has no API keys, OAuth, or session middleware.
- **Open CORS**: `allow_origins=["*"]` is set in `main.py`. Restrict this in production.
- **Database Reset**: `POST /api/reset` destroys all data without authorization checks.
- **SQLite**: Single-file database. Back up `backend/data/` and `sprint_agent.db` regularly.
- **File Uploads**: `python-multipart` is available but verify upload endpoints do not allow path traversal if extended.
- **Environment Variables**: The backend does not currently read from a `.env` file. Configuration is stored in the `config` DB table and managed via the settings router.

---

## Deployment Notes

- The `Dockerfile` builds only the backend. The frontend must be built separately (`npm run build`) and its `dist/` folder is mounted into an `nginx:alpine` container via `docker-compose.yml`.
- The frontend build uses `base: './'` for relative paths, suitable for static hosting.
- Environment variables intended for the frontend must be prefixed with `VITE_` to be exposed at build time.

---

## Documentation References

Detailed documentation lives in `docs/`:

- `API.md` — Complete endpoint docs with curl examples
- `ARCHITECTURE.md` — System architecture and data flows
- `BACKEND.md` — Backend conventions and testing strategy
- `DATA_FORMAT.md` — `init.json` schema specification
- `DEPLOY.md` — Production deployment procedures
- `FRONTEND.md` — Frontend architecture details
- `USAGE.md` — End-user manual
- `UX_DESIGN.md` — UX principles and multi-agent testing methodology

When making changes that affect APIs, data formats, or deployment, update the corresponding file in `docs/`.
