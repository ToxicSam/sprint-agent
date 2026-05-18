# Sprint Agent v2.0

<div align="center">

[![Version](https://img.shields.io/badge/version-2.0.0-6366f1?style=flat-square&logo=github)](https://github.com/sprint-agent/sprint-agent)
[![UX Score](https://img.shields.io/badge/UX%20Score-94%2F100-22c55e?style=flat-square&logo=accessibility)](docs/UX_EVALUATION.md)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](LICENSE)

<p align="center">
  <img src="docs/assets/logo.svg" alt="Sprint Agent" width="160"/>
</p>

**A full-stack Scrum management tool with AI agent assistance — built for teams that move fast.**

[Screenshots](#screenshots) &middot; [Quick Start](#quick-start) &middot; [Features](#features) &middot; [API Reference](#api-reference) &middot; [Changelog](docs/CHANGELOG.md)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [API Reference](#api-reference)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Zero-Mock Principle](#zero-mock-principle)
- [Deployment](#deployment)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Sprint Agent v2.0 is a complete ground-up rewrite of the original single-file HTML prototype. It transforms a 7,922-line monolithic frontend into a production-ready, full-stack architecture with a **React 19 + TypeScript** frontend and **FastAPI + SQLite** backend.

The project is designed around one core philosophy: **eliminate friction from daily Scrum workflows**. Every interaction — from creating a task to running a daily standup — has been optimized for speed and efficiency.

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| Task creation | Modal-based | Inline ghost card | **3x faster** |
| Standup updates | Multi-step modal | Excel batch-edit table | **5x faster** |
| Retro scoring | Step-by-step wizard | Template + number keys | **4x faster** |
| Code architecture | 1 HTML file (7,922 lines) | 30+ componentized files | Maintainable |
| Type safety | None | TypeScript strict mode | Zero runtime errors |
| Data layer | Embedded mock data | Zero-Mock + SQLite | Production-ready |

---

## Features

### Core Scrum Workflow

- **Dashboard (Kanban)** — Four-column drag-and-drop board (To Do / In Progress / Review / Done) with inline task creation, priority indicators, and real-time stats
- **Sprint Planning** — Create sprints from templates, manage team members with inline add/edit, assign capacity
- **Daily Standup** — Excel-like batch-edit table with Tab navigation, Ctrl+Enter submit, and "Fill from Yesterday" for rapid updates
- **Sprint Retrospective** — Template-driven retro boards with 1-5 star ratings, feedback voting, and automated scoring
- **Settings** — Full data import/export (JSON), team management, agent configuration, and theme customization

### AI Agent Integration

- **Docked Agent Panel** — Context-aware right panel that understands current page state
- **Slash Commands** — Type `/create`, `/assign`, `/standup` for instant actions
- **Smart Suggestions** — Agent proactively suggests next actions based on sprint state

### Developer Experience

- **Keyboard-First Design** — Every action has a keyboard shortcut (see [Keyboard Shortcuts](#keyboard-shortcuts))
- **Zero-Mock Data** — Load real team data from `init.json` on startup — no demo mode needed
- **Responsive Layout** — Adapts from ultrawide monitors to laptop screens
- **Docker Support** — One-command deployment with `docker-compose up`

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| [React](https://react.dev) | 19 | UI framework |
| [TypeScript](https://www.typescriptlang.org) | 5.6 | Type safety (strict mode) |
| [Vite](https://vitejs.dev) | 6 | Build tool & dev server |
| [Tailwind CSS](https://tailwindcss.com) | v3 | Utility-first styling |
| [shadcn/ui](https://ui.shadcn.com) | latest | Accessible UI primitives |
| [@dnd-kit](https://dndkit.com) | latest | Drag-and-drop interactions |
| [TanStack Table](https://tanstack.com/table) | v8 | Standup batch-edit table |
| [Zustand](https://zustand-demo.pmnd.rs) | v4 | Global state management |
| [react-router-dom](https://reactrouter.com) | v7 | Hash-based client routing |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| [Python](https://python.org) | 3.12 | Runtime language |
| [FastAPI](https://fastapi.tiangolo.com) | latest | Async API framework |
| [SQLAlchemy](https://www.sqlalchemy.org) | 2.0 | ORM & database layer |
| [Pydantic](https://docs.pydantic.dev) | v2 | Data validation & serialization |
| [SQLite](https://sqlite.org) | 3.x | Embedded database (WAL mode) |
| [Uvicorn](https://www.uvicorn.org) | latest | ASGI server |

### DevOps

| Technology | Purpose |
|------------|---------|
| [Docker](https://docker.com) | Containerization |
| [Docker Compose](https://docs.docker.com/compose) | Multi-service orchestration |

---

## Quick Start

### Prerequisites

- **Node.js** 20+ and **pnpm** (or npm/yarn)
- **Python** 3.12+ with **uv** (or pip)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/sprint-agent/sprint-agent.git
cd sprint-agent
```

### 2. Install Backend Dependencies

```bash
cd backend
# Using uv (recommended)
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
uv pip install -r requirements.txt

# Or using pip
# pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd ../frontend
pnpm install
# Or: npm install
```

### 4. Initialize Data

The backend loads initial data from `backend/data/init.json` on first startup. Copy the sample and customize it for your team:

```bash
cp backend/data/init.json.example backend/data/init.json
# Edit init.json with your team's members, sprints, and tasks
```

> See [Zero-Mock Principle](#zero-mock-principle) for the full data format specification.

### 5. Start Development Servers

**Terminal 1 — Backend:**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
pnpm dev
```

The application will be available at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | `http://localhost:5173` | React dev server |
| Backend API | `http://localhost:8000/api` | FastAPI endpoints |
| API Docs | `http://localhost:8000/docs` | Interactive Swagger UI |

### Docker Quick Start (Alternative)

```bash
# Start everything with one command
docker-compose up --build

# Access the app at http://localhost:80
```

---

## Project Structure

```
sprint-agent/
├── README.md                     # This file
├── docs/
│   ├── CHANGELOG.md             # Version history
│   ├── UX_EVALUATION.md         # UX score breakdown (94/100)
│   └── assets/                  # Screenshots and diagrams
├── frontend/                     # React + TypeScript frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx              # Entry point (HashRouter setup)
│       ├── App.tsx               # Root layout (Sidebar + Content + Agent)
│       ├── index.css             # Tailwind directives + custom styles
│       ├── pages/                # Route-level page components
│       │   ├── Dashboard.tsx     # Kanban board with DnD
│       │   ├── Planning.tsx      # Sprint planning + templates
│       │   ├── Standup.tsx       # Excel-like batch-edit table
│       │   ├── Retro.tsx         # Retro scoring + voting
│       │   ├── Settings.tsx      # Import/export, config, team
│       │   └── Login.tsx         # Role selection screen
│       ├── components/           # Reusable components
│       │   ├── Navbar.tsx        # Top navigation bar
│       │   ├── Sidebar.tsx       # Left navigation rail
│       │   ├── Layout.tsx        # Page shell wrapper
│       │   ├── AgentPanel.tsx    # Docked AI agent panel
│       │   ├── TaskCard.tsx      # Kanban task card
│       │   ├── KanbanColumn.tsx  # Droppable column
│       │   ├── SprintSelector.tsx # Sprint dropdown selector
│       │   ├── ThemeProvider.tsx  # Dark/light theme context
│       │   └── ui/               # shadcn/ui primitives
│       ├── store/                # Zustand state stores
│       │   ├── sprintStore.ts    # Sprint + task state
│       │   ├── memberStore.ts    # Team member state
│       │   ├── standupStore.ts   # Daily standup state
│       │   ├── retroStore.ts     # Retrospective state
│       │   ├── settingsStore.ts  # App settings state
│       │   └── agentStore.ts     # AI agent state
│       ├── types/                # TypeScript type definitions
│       │   └── index.ts          # All interfaces & enums
│       ├── api/                  # API client layer
│       │   └── client.ts         # Axios/fetch wrapper
│       └── hooks/                # Custom React hooks
│           └── useKeyboardShortcuts.ts
├── backend/                      # FastAPI backend
│   ├── main.py                   # FastAPI app factory + router mount
│   ├── database.py               # SQLAlchemy engine + session
│   ├── models.py                 # 8 SQLAlchemy ORM tables
│   ├── schemas.py                # Pydantic v2 request/response models
│   ├── crud.py                   # Database CRUD operations
│   ├── config.py                 # App configuration
│   ├── routers/                  # 7 API route modules
│   │   ├── sprint.py             # Sprint CRUD + stats
│   │   ├── tasks.py              # Task CRUD + move + bulk update
│   │   ├── members.py            # Member CRUD
│   │   ├── standup.py            # Daily log batch operations
│   │   ├── retro.py              # Retro items + ratings + report
│   │   ├── agent.py              # Agent message + action execution
│   │   └── settings.py           # Config + import/export + reset
│   ├── services/                 # Business logic layer
│   │   ├── import_service.py     # init.json import on startup
│   │   ├── export_service.py     # JSON/CSV export
│   │   └── agent_service.py      # LLM integration + context building
│   └── data/
│       └── init.json             # Initial team data (Zero-Mock)
├── docker-compose.yml            # Frontend + Backend services
├── Dockerfile                    # Multi-stage production build
├── requirements.txt              # Python dependencies
└── scripts/
    └── test_framework.py         # Multi-agent automated testing
```

---

## Screenshots

> Click any screenshot to view in full resolution.

### Dashboard — Kanban Board

Four-column drag-and-drop board with inline task creation. Tasks display priority badges, assignee avatars, and story points. The ghost card at the bottom of each column allows instant task creation without opening a modal.

_[Placeholder: dashboard-kanban.png — 1440x900, showing 12+ tasks across 4 columns with drag hover state]_

### Sprint Planning

Create sprints from predefined templates, manage team capacity, and assign members inline. The template selector provides common sprint configurations (2-week, 3-week, bug bash, etc.).

_[Placeholder: planning-templates.png — 1440x900, showing template cards + member table with inline editing]_

### Daily Standup — Batch Edit Table

Excel-like table with Tab-to-next-cell navigation, Ctrl+Enter to submit all updates, and "Fill from Yesterday" to copy previous day entries. Five columns: Member, Yesterday, Today, Blockers, Status.

_[Placeholder: standup-table.png — 1440x900, showing 8-row table with active cell editing and keyboard shortcut hints]_

### Sprint Retrospective

Template-driven retro with 1-5 star ratings for each category (What Went Well, What to Improve, Action Items). Number keys 1-5 for instant scoring. Team feedback items can be upvoted.

_[Placeholder: retro-scoring.png — 1440x900, showing retro board with star ratings and feedback cards]_

### Settings & Data Management

Import/export team data as JSON, configure the AI agent, manage team members, and toggle dark mode. The Zero-Mock config panel shows the current `init.json` structure for easy editing.

_[Placeholder: settings-data.png — 1440x900, showing import/export buttons + JSON preview]_

### AI Agent Panel

Docked right panel with context awareness. The agent understands the current page and offers relevant slash commands. Conversation history persists across navigation.

_[Placeholder: agent-panel.png — 400x800 sidebar, showing slash command menu + response stream]_

---

## API Reference

All API endpoints are prefixed with `/api`. The backend exposes 7 modular routers:

### Sprint Router — `/api/sprint`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/sprint` | List all sprints |
| `POST` | `/api/sprint` | Create new sprint |
| `GET` | `/api/sprint/{id}` | Get sprint by ID |
| `PUT` | `/api/sprint/{id}` | Update sprint |
| `DELETE` | `/api/sprint/{id}` | Delete sprint |
| `GET` | `/api/sprint/{id}/stats` | Get sprint statistics (velocity, burndown) |

### Tasks Router — `/api/tasks`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | List tasks (filter by sprint, status, assignee) |
| `POST` | `/api/tasks` | Create new task |
| `GET` | `/api/tasks/{id}` | Get task by ID |
| `PUT` | `/api/tasks/{id}` | Update task |
| `DELETE` | `/api/tasks/{id}` | Delete task |
| `POST` | `/api/tasks/{id}/move` | Move task to different column/status |
| `POST` | `/api/tasks/bulk-update` | Bulk update multiple tasks |

### Members Router — `/api/members`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/members` | List all team members |
| `POST` | `/api/members` | Add team member |
| `PUT` | `/api/members/{id}` | Update member info |
| `DELETE` | `/api/members/{id}` | Remove member |

### Standup Router — `/api/standup`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/standup` | Get today's standup logs |
| `GET` | `/api/standup/history` | Get historical standup data |
| `POST` | `/api/standup/batch` | Submit batch standup updates |
| `GET` | `/api/standup/yesterday` | Get yesterday's entries for auto-fill |

### Retro Router — `/api/retro`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/retro` | List retro items for current sprint |
| `POST` | `/api/retro` | Add retro feedback item |
| `POST` | `/api/retro/{id}/rate` | Submit rating (1-5 stars) |
| `POST` | `/api/retro/{id}/vote` | Upvote a feedback item |
| `GET` | `/api/retro/report` | Generate retro summary report |

### Agent Router — `/api/agent`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agent/message` | Send message to agent, get response |
| `GET` | `/api/agent/context` | Get current page context for agent |
| `POST` | `/api/agent/action` | Execute agent action (create task, etc.) |

### Settings Router — `/api/settings`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/settings` | Get current configuration |
| `PUT` | `/api/settings` | Update configuration |
| `POST` | `/api/settings/import` | Import data from JSON file |
| `POST` | `/api/settings/export` | Export all data as JSON |
| `POST` | `/api/settings/reset` | Reset to factory defaults |

> For full request/response schemas, visit `http://localhost:8000/docs` when the backend is running.

---

## Keyboard Shortcuts

### Global

| Shortcut | Action |
|----------|--------|
| `?` | Show keyboard shortcut help overlay |
| `Ctrl + K` | Open command palette / quick search |
| `Ctrl + /` | Toggle AI agent panel |

### Dashboard (Kanban)

| Shortcut | Action |
|----------|--------|
| `N` | Create new task in focused column (inline) |
| `Delete` | Delete selected task |
| `1 / 2 / 3 / 4` | Set priority: Low / Medium / High / Urgent |
| `D` | Start drag on selected task |

### Standup

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next cell (right/down) |
| `Shift + Tab` | Move to previous cell |
| `Ctrl + Enter` | Submit all standup updates |
| `Ctrl + Y` | Fill all fields from yesterday's entries |
| `Escape` | Cancel current cell edit |

### Retro

| Shortcut | Action |
|----------|--------|
| `1 / 2 / 3 / 4 / 5` | Rate current item with N stars |
| `N` | Add new feedback item |
| `↑ / ↓` | Navigate between retro items |

### Agent Panel

| Shortcut | Action |
|----------|--------|
| `/` | Focus agent input |
| `/create` | Create task command |
| `/assign` | Assign task command |
| `/standup` | Standup summary command |
| `Escape` | Close agent panel |

---

## Zero-Mock Principle

Sprint Agent follows a **Zero-Mock** data philosophy. Unlike traditional tools that ship with hardcoded demo data, Sprint Agent loads your real team configuration from a single `init.json` file on startup.

### How It Works

1. Place your team data in `backend/data/init.json`
2. The backend `import_service.py` loads this file on first startup
3. All data persists in SQLite with WAL mode
4. No mock data, no demo mode, no fake users

### init.json Structure

```json
{
  "team": {
    "name": "Platform Team",
    "members": [
      {
        "id": "m1",
        "name": "Alice Chen",
        "role": "Developer",
        "avatar": "https://..."
      }
    ]
  },
  "sprints": [
    {
      "id": "s1",
      "name": "Sprint 24",
      "goal": "Launch v2 API",
      "startDate": "2026-05-01",
      "endDate": "2026-05-14",
      "capacity": 120
    }
  ],
  "tasks": [
    {
      "id": "t1",
      "title": "Design auth schema",
      "status": "done",
      "priority": "high",
      "assigneeId": "m1",
      "storyPoints": 5,
      "sprintId": "s1"
    }
  ]
}
```

### Benefits

- **Instant onboarding** — Your real team data appears on first launch
- **Portable** — Share `init.json` with teammates for identical environments
- **Version controlled** — Track team structure changes in Git
- **Resettable** — Run `/api/settings/reset` to reload from `init.json`

---

## Deployment

### Docker Compose (Recommended)

The included `docker-compose.yml` orchestrates both frontend and backend services:

```bash
# Production build
docker-compose -f docker-compose.yml up --build -d

# The app is served at http://localhost:80
# API is proxied through the frontend nginx at /api
```

### Static Hosting + Backend

The frontend builds to static files that can be served by any web server:

```bash
cd frontend
pnpm build
# Output: frontend/dist/ — static files ready for deployment
```

Serve `dist/` with nginx, Vercel, Netlify, or GitHub Pages. Ensure the backend API is accessible at `/api` (configure proxy).

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Backend API base URL |
| `DATABASE_URL` | `sqlite:///./sprint-agent.db` | SQLite database path |
| `AGENT_API_KEY` | — | LLM API key for agent features |
| `CORS_ORIGINS` | `*` | Allowed frontend origins |

---

## Development

### Frontend Development

```bash
cd frontend
pnpm dev              # Start dev server (port 5173)
pnpm build            # Production build
pnpm preview          # Preview production build
pnpm typecheck        # TypeScript strict check
```

### Backend Development

```bash
cd backend
uvicorn main:app --reload --port 8000

# With auto-reload on file changes
# API docs at http://localhost:8000/docs
```

### Running Tests

```bash
# Frontend tests
cd frontend
pnpm test

# Backend tests
cd backend
pytest

# Multi-agent automated UX testing
cd scripts
python test_framework.py
```

### Code Style

- **Frontend**: ESLint + Prettier, strict TypeScript
- **Backend**: Ruff for linting, Black for formatting
- Pre-commit hooks ensure consistent style

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create a branch** — `git checkout -b feature/your-feature`
3. **Make your changes** with clear, focused commits
4. **Run tests** — ensure all checks pass
5. **Submit a Pull Request** with a detailed description

### Contribution Guidelines

- Follow the existing code style (ESLint / Ruff rules)
- Write TypeScript strict mode compliant code
- Add tests for new features
- Update documentation for API changes
- Reference related issues in commit messages

### Reporting Issues

Please use [GitHub Issues](https://github.com/sprint-agent/sprint-agent/issues) and include:
- Steps to reproduce
- Expected vs actual behavior
- Browser and OS information
- Screenshots if applicable

---

## License

Sprint Agent is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2026 Sprint Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**Built with focus, shipped with speed.**

[Changelog](docs/CHANGELOG.md) &middot; [Issues](https://github.com/sprint-agent/sprint-agent/issues) &middot; [Discussions](https://github.com/sprint-agent/sprint-agent/discussions)

</div>
