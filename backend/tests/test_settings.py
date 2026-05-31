"""Tests for Settings / Import / Export routes."""

import pytest

import crud
import schemas


class TestSettings:
    """Group all Settings endpoint tests."""

    async def test_update_config(self, client):
        """PUT /api/settings should update configuration key-value pairs."""
        payload = {"settings": {"theme": "dark", "language": "en"}}
        response = await client.put("/api/settings", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] is True

        # Verify via GET
        get_resp = await client.get("/api/settings")
        assert get_resp.status_code == 200
        settings = get_resp.json()
        assert settings.get("theme") == "dark"
        assert settings.get("language") == "en"

    async def test_export_data(self, client, db_session, sample_sprint, sample_member, sample_task):
        """GET /api/export should export all database content."""
        response = await client.get("/api/export")
        assert response.status_code == 200
        data = response.json()

        assert "sprints" in data
        assert "members" in data
        assert "tasks" in data
        assert "daily_logs" in data
        assert "retros" in data
        assert "retro_ratings" in data
        assert "agent_messages" in data
        assert "config" in data

        # Should contain our sample data
        assert len(data["sprints"]) >= 1
        sprint_ids = [s["id"] for s in data["sprints"]]
        assert sample_sprint.id in sprint_ids

        assert len(data["members"]) >= 1
        member_ids = [m["id"] for m in data["members"]]
        assert sample_member.id in member_ids

        assert len(data["tasks"]) >= 1
        task_ids = [t["id"] for t in data["tasks"]]
        assert sample_task.id in task_ids

    async def test_import_data(self, client):
        """POST /api/import should accept import data."""
        # The MVP endpoint returns a placeholder result
        payload = {
            "data": {
                "sprints": [{"name": "Imported Sprint"}],
                "members": [],
                "tasks": [],
            }
        }
        response = await client.post("/api/import", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "inserted" in data
        assert "errors" in data
