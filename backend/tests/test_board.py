"""Tests for Board aggregation and Health routes."""

import pytest

import crud
from schemas import TaskCreate


class TestBoard:
    """Group all Board and Health endpoint tests."""

    async def test_get_board(self, client, db_session, sample_sprint, sample_member):
        """GET /api/board should return aggregated board data."""
        # Create a task for the sprint
        crud.create_task(
            db_session,
            TaskCreate(
                title="Board Task",
                sprint_id=sample_sprint.id,
                assignee_id=sample_member.id,
                status="progress",
            ),
        )

        response = await client.get("/api/board")
        assert response.status_code == 200
        data = response.json()

        assert "sprint" in data
        assert "members" in data
        assert "tasks" in data

        # Sprint should be the active one
        assert data["sprint"] is not None
        assert data["sprint"]["id"] == sample_sprint.id
        assert data["sprint"]["name"] == sample_sprint.name

        # Should include members
        assert isinstance(data["members"], list)
        assert len(data["members"]) >= 1

        # Should include tasks for the active sprint
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) >= 1
        task_titles = [t["title"] for t in data["tasks"]]
        assert "Board Task" in task_titles

    async def test_get_board_no_active_sprint(self, client):
        """GET /api/board should handle no active sprint gracefully."""
        response = await client.get("/api/board")
        assert response.status_code == 200
        data = response.json()
        assert data["sprint"] is None
        assert data["members"] == []
        assert data["tasks"] == []

    async def test_health_check(self, client):
        """GET /api/health should return ok status."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
