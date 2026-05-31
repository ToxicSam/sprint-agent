"""Tests for Task routes."""

import pytest
from datetime import date

from schemas import TaskCreate, TaskUpdate, TaskMove, BulkTaskUpdate
import crud


class TestTask:
    """Group all Task endpoint tests."""

    async def test_create_task(self, client, sample_sprint, sample_member):
        """POST /api/tasks should create a new task."""
        payload = {
            "title": "Build API",
            "sprint_id": sample_sprint.id,
            "assignee_id": sample_member.id,
            "status": "todo",
            "priority": 1,
            "story_points": 5.0,
        }
        response = await client.post("/api/tasks", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Build API"
        assert data["sprint_id"] == sample_sprint.id
        assert data["assignee_id"] == sample_member.id
        assert data["status"] == "todo"
        assert data["story_points"] == 5.0
        assert "id" in data
        assert "created_at" in data

    async def test_list_tasks(self, client, db_session, sample_sprint, sample_member):
        """GET /api/tasks should list tasks, optionally filtered."""
        # Create multiple tasks
        crud.create_task(db_session, TaskCreate(title="Task 1", sprint_id=sample_sprint.id, assignee_id=sample_member.id, status="todo"))
        crud.create_task(db_session, TaskCreate(title="Task 2", sprint_id=sample_sprint.id, assignee_id=sample_member.id, status="done"))

        # List all
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        # Filter by status
        resp_todo = await client.get("/api/tasks", params={"status": "todo"})
        assert resp_todo.status_code == 200
        for task in resp_todo.json():
            assert task["status"] == "todo"

        # Filter by sprint_id
        resp_sprint = await client.get("/api/tasks", params={"sprint_id": sample_sprint.id})
        assert resp_sprint.status_code == 200
        for task in resp_sprint.json():
            assert task["sprint_id"] == sample_sprint.id

    async def test_update_task(self, client, sample_task):
        """PUT /api/tasks/{id} should update the task."""
        payload = {"title": "Updated Title", "status": "progress", "story_points": 8.0}
        response = await client.put(f"/api/tasks/{sample_task.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "progress"
        assert data["story_points"] == 8.0
        assert data["id"] == sample_task.id

    async def test_update_task_not_found(self, client):
        """PUT /api/tasks/{id} should 404 for a missing task."""
        payload = {"title": "Ghost"}
        response = await client.put("/api/tasks/nonexistent-id", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    async def test_delete_task(self, client, sample_task):
        """DELETE /api/tasks/{id} should delete the task."""
        response = await client.delete(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True

    async def test_delete_task_not_found(self, client):
        """DELETE /api/tasks/{id} should 404 for a missing task."""
        response = await client.delete("/api/tasks/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    async def test_move_task(self, client, sample_task):
        """POST /api/tasks/{id}/move should change task status."""
        assert sample_task.status == "todo"
        payload = {"status": "progress"}
        response = await client.post(f"/api/tasks/{sample_task.id}/move", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "progress"
        assert data["id"] == sample_task.id

    async def test_move_task_not_found(self, client):
        """POST /api/tasks/{id}/move should 404 for a missing task."""
        payload = {"status": "done"}
        response = await client.post("/api/tasks/nonexistent-id/move", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    async def test_bulk_update_tasks(self, client, db_session, sample_sprint, sample_member):
        """POST /api/tasks/bulk should update multiple tasks at once."""
        t1 = crud.create_task(db_session, TaskCreate(title="Bulk 1", sprint_id=sample_sprint.id, assignee_id=sample_member.id, status="todo"))
        t2 = crud.create_task(db_session, TaskCreate(title="Bulk 2", sprint_id=sample_sprint.id, assignee_id=sample_member.id, status="todo"))

        payload = {
            "ids": [t1.id, t2.id],
            "status": "done",
        }
        response = await client.post("/api/tasks/bulk", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 2
        assert data["errors"] == []

    async def test_bulk_update_tasks_partial_error(self, client, sample_task):
        """POST /api/tasks/bulk should report errors for missing tasks."""
        payload = {
            "ids": [sample_task.id, "fake-id"],
            "status": "done",
        }
        response = await client.post("/api/tasks/bulk", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 1
        assert len(data["errors"]) == 1
        assert "fake-id" in data["errors"][0]

    async def test_get_blockers(self, client, db_session, sample_sprint, sample_member):
        """GET /api/tasks/{id}/blockers should return blocker chain."""
        # Create a blocker task
        blocker = crud.create_task(
            db_session,
            TaskCreate(title="Blocker Task", sprint_id=sample_sprint.id, assignee_id=sample_member.id, status="paused"),
        )
        # Create a blocked task referencing the blocker
        blocked = crud.create_task(
            db_session,
            TaskCreate(
                title="Blocked Task",
                sprint_id=sample_sprint.id,
                assignee_id=sample_member.id,
                status="todo",
                blocked_by=f'["{blocker.id}"]',
            ),
        )

        response = await client.get(f"/api/tasks/{blocked.id}/blockers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == blocker.id
        assert data[0]["title"] == "Blocker Task"

    async def test_get_blockers_none(self, client, sample_task):
        """GET /api/tasks/{id}/blockers should return empty list when no blockers."""
        response = await client.get(f"/api/tasks/{sample_task.id}/blockers")
        assert response.status_code == 200
        data = response.json()
        assert data == []
