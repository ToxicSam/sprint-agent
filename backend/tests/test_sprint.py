"""Tests for Sprint routes."""

import pytest
from datetime import date

from schemas import SprintCreate, TaskCreate
import crud


class TestSprint:
    """Group all Sprint endpoint tests."""

    async def test_create_sprint(self, client):
        """POST /api/sprint should create a new sprint."""
        payload = {
            "name": "New Sprint",
            "goal": "Sprint goal",
            "start_date": str(date.today()),
            "end_date": None,
            "status": "active",
        }
        response = await client.post("/api/sprint", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Sprint"
        assert data["goal"] == "Sprint goal"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data

    async def test_get_active_sprint(self, client, sample_sprint):
        """GET /api/sprint should return the active sprint."""
        response = await client.get("/api/sprint")
        assert response.status_code == 200
        data = response.json()
        assert data is not None
        assert data["id"] == sample_sprint.id
        assert data["name"] == sample_sprint.name
        assert data["status"] == "active"

    async def test_get_active_sprint_none(self, client):
        """GET /api/sprint should return null when there is no active sprint."""
        response = await client.get("/api/sprint")
        assert response.status_code == 200
        data = response.json()
        assert data is None

    async def test_update_sprint(self, client, sample_sprint):
        """PUT /api/sprint/{id} should update the sprint."""
        payload = {"name": "Updated Sprint Name", "goal": "Updated goal"}
        response = await client.put(f"/api/sprint/{sample_sprint.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Sprint Name"
        assert data["goal"] == "Updated goal"
        assert data["id"] == sample_sprint.id

    async def test_update_sprint_not_found(self, client):
        """PUT /api/sprint/{id} should 404 for a missing sprint."""
        payload = {"name": "Does Not Matter"}
        response = await client.put("/api/sprint/nonexistent-id", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    async def test_delete_sprint(self, client, sample_sprint):
        """DELETE /api/sprint/{id} should delete the sprint."""
        response = await client.delete(f"/api/sprint/{sample_sprint.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True

        # Verify it is gone
        get_resp = await client.get("/api/sprint")
        assert get_resp.status_code == 200
        assert get_resp.json() is None

    async def test_delete_sprint_not_found(self, client):
        """DELETE /api/sprint/{id} should 404 for a missing sprint."""
        response = await client.delete("/api/sprint/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Sprint not found"

    async def test_get_sprint_stats(self, client, db_session, sample_sprint):
        """GET /api/sprint/{id}/stats should return sprint statistics."""
        # Create tasks in various statuses via CRUD for precise control
        crud.create_task(
            db_session,
            TaskCreate(
                title="Task Done",
                sprint_id=sample_sprint.id,
                assignee_id=None,
                status="done",
                story_points=8.0,
            ),
        )
        crud.create_task(
            db_session,
            TaskCreate(
                title="Task Todo",
                sprint_id=sample_sprint.id,
                assignee_id=None,
                status="todo",
                story_points=3.0,
            ),
        )

        response = await client.get(f"/api/sprint/{sample_sprint.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "todo" in data
        assert "done" in data
        assert "progress" in data
        assert "paused" in data
        assert "total_story_points" in data
        assert "completed_story_points" in data
        assert "remaining_story_points" in data
        assert "completion_rate" in data
        assert "members_active" in data
