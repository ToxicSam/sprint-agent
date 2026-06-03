# P0: Frontend-Backend API Alignment Design

## Problem

The sprint-agent frontend and backend have drifted apart. Multiple frontend API modules call endpoints that don't exist in the backend, and several pages (AgentPanel, Standup, Retro) use mock/simulated data instead of real API calls. This makes core features non-functional.

## Scope

This design covers P0 issues only: aligning API contracts and replacing mock data with real calls. It also includes the database path fix as it blocks end-to-end functionality.

Out of scope: architecture refactoring (God Object splitting), security hardening (auth/CORS), type system unification (blocked_by), and P2/P3 issues.

## Unified API Contract

### Sprint

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/sprint | Get current active sprint |
| POST | /api/sprint | Create a sprint |
| PATCH | /api/sprint/{id} | Update a sprint (was PUT) |
| DELETE | /api/sprint/{id} | Delete a sprint |

### Members

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/members | List members |
| POST | /api/members | Create a member |
| PATCH | /api/members/{id} | Update a member (was PUT) |
| DELETE | /api/members/{id} | Delete a member |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/tasks?sprint_id=X | List tasks for a sprint |
| POST | /api/tasks | Create a task |
| PATCH | /api/tasks/{id} | Update a task (was PUT) |
| PATCH | /api/tasks/{id}/move | Move task to different status |
| DELETE | /api/tasks/{id} | Delete a task |

### Standup (Daily Logs)

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/standup?sprint_id=X | Get daily logs for a sprint |
| GET | /api/standup/today?sprint_id=X | Get today's log (new endpoint) |
| POST | /api/standup | Create or update a daily log |

### Retro

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/retro/{sprint_id} | Get retro items for a sprint |
| POST | /api/retro | Create a retro item |
| POST | /api/retro/vote | Vote on a retro item |
| DELETE | /api/retro/{item_id} | Delete a retro item (new endpoint) |

### Agent

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/agent/chat | Send a message (was /agent/message) |
| GET | /api/agent/history | Get chat history (was /agent/messages) |
| DELETE | /api/agent/history | Clear chat history (new endpoint) |

### Board (aggregate)

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/board | Get sprint + members + tasks in one call |

### Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/export | Export all data |
| POST | /api/import | Import data |

## Implementation Details

### Backend Changes

1. **`routers/sprint.py`**: Change `@router.put("/{sprint_id}")` to `@router.patch("/{sprint_id}")`

2. **`routers/members.py`**: Change `@router.put("/{member_id}")` to `@router.patch("/{member_id}")`

3. **`routers/tasks.py`**: Change `@router.put("/{task_id}")` to `@router.patch("/{task_id}")`

4. **`routers/standup.py`**: Add `GET /api/standup/today` endpoint that filters by sprint_id and current date

5. **`routers/retro.py`**: Add `DELETE /api/retro/{item_id}` endpoint

6. **`routers/agent.py`**:
   - Rename route `POST /message` to `POST /chat`
   - Rename route `GET /messages` to `GET /history`
   - Add `DELETE /history` endpoint that clears agent_messages for the sprint

7. **`database.py`**: Replace hardcoded `/tmp/sprint_agent.db` with `os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./sprint_agent.db")`

8. **`main.py`**: Align `db_path` check in lifespan with the actual database path from `database.py`

### Frontend Changes

1. **`api/tasks.ts`**: Add `moveTask(id, status)` calling `PATCH /api/tasks/{id}/move`

2. **`api/standup.ts`**: Change paths to `/api/standup`, add `getTodayLogs(sprintId)` calling `GET /api/standup/today?sprint_id=X`

3. **`api/retro.ts`**: Change paths to `/api/retro/{sprintId}` (GET), `/api/retro` (POST), `/api/retro/vote` (POST vote). Add `deleteRetroItem(itemId)` calling `DELETE /api/retro/{itemId}`

4. **`api/agent.ts`**: Change `sendMessage` path to `/api/agent/chat`, `getHistory` to `/api/agent/history`, add `clearHistory()` calling `DELETE /api/agent/history`

5. **`components/AgentPanel.tsx`**:
   - Remove hardcoded random response array (lines 36-50)
   - Import and call `sendMessage` from `api/agent.ts`
   - Import and call `getHistory` on mount to load existing conversation
   - Add loading state during API call
   - Add error handling for failed requests

6. **`pages/Standup.tsx`**:
   - Remove `setTimeout` mock in submit handler (line 366)
   - Call `createDailyLog` from `api/standup.ts` on submit
   - Call `getDailyLogs` on page mount to load existing logs
   - Handle API errors with toast notifications

7. **`pages/Retro.tsx`**:
   - Remove localStorage read/write for retro data (lines 407-424)
   - Call `getRetroItems(sprintId)` on page mount
   - Call `createRetroItem` when adding items
   - Call `voteRetroItem` on vote
   - Call `deleteRetroItem` on delete
   - Handle API errors

8. **`pages/Settings.tsx` (Data tab)**:
   - Export: call `GET /api/export` instead of reading localStorage
   - Import: call `POST /api/import` instead of writing to localStorage

### Database Path Fix

**`backend/database.py`**:
```python
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./sprint_agent.db"
)
engine = create_async_engine(DATABASE_URL, echo=False)
```

**`backend/main.py`**:
Align the lifespan `db_path` check to use the same path as `database.py`. Extract the path to a shared constant or import from database module.

## Risk Assessment

- **PATCH vs PUT**: Changing HTTP method is a breaking change for any existing API consumers. Since there are no external consumers yet, this is safe.
- **Agent rename**: Renaming `/message` to `/chat` and `/messages` to `/history` is purely internal, no external impact.
- **New DELETE endpoints**: Additive only, no breaking changes.
- **Mock removal**: Removing mock data may expose backend bugs that were hidden. Each page should be tested end-to-end after the change.
- **Database path change**: Existing databases at `/tmp/sprint_agent.db` will not be found after the change. Document migration step: copy existing DB to `./sprint_agent.db`.

## Testing Plan

1. Start backend, verify all endpoints respond with correct methods
2. Start frontend, navigate to each page, verify network tab shows correct API calls
3. Test AgentPanel: send a message, verify response from LLM
4. Test Standup: submit a daily log, verify it persists
5. Test Retro: create item, vote, delete, verify all operations work
6. Test Settings Data tab: export data, import data, verify round-trip
7. Test board: verify drag-and-drop task move calls correct endpoint
