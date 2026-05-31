"""Tests for Standup (DailyLog) routes."""

import pytest
from datetime import date, timedelta

from schemas import DailyLogCreate, DailyLogBatch
import crud


class TestStandup:
    """Group all Standup/DailyLog endpoint tests."""

    async def test_create_daily_log(self, client, sample_sprint, sample_member):
        """POST /api/standup should create a daily log."""
        payload = {
            "sprint_id": sample_sprint.id,
            "member_id": sample_member.id,
            "date": str(date.today()),
            "completed": "Did some work",
            "planned": "Do more work",
            "blockers": "None",
            "hours_spent": 6.5,
        }
        response = await client.post("/api/standup", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["sprint_id"] == sample_sprint.id
        assert data["member_id"] == sample_member.id
        assert data["completed"] == "Did some work"
        assert data["planned"] == "Do more work"
        assert data["blockers"] == "None"
        assert data["hours_spent"] == 6.5
        assert "id" in data

    async def test_create_daily_log_upsert(self, client, sample_sprint, sample_member):
        """POST /api/standup should upsert an existing log."""
        today = str(date.today())
        payload = {
            "sprint_id": sample_sprint.id,
            "member_id": sample_member.id,
            "date": today,
            "completed": "First entry",
        }
        r1 = await client.post("/api/standup", json=payload)
        assert r1.status_code == 200

        payload["completed"] = "Updated entry"
        r2 = await client.post("/api/standup", json=payload)
        assert r2.status_code == 200
        assert r2.json()["completed"] == "Updated entry"

    async def test_batch_create_logs(self, client, sample_sprint, sample_member):
        """POST /api/standup/batch should create multiple logs."""
        today = str(date.today())
        payload = {
            "logs": [
                {
                    "sprint_id": sample_sprint.id,
                    "member_id": sample_member.id,
                    "date": today,
                    "completed": "Task A",
                    "hours_spent": 4.0,
                },
                {
                    "sprint_id": sample_sprint.id,
                    "member_id": sample_member.id,
                    "date": str(date.today() - timedelta(days=1)),
                    "completed": "Task B",
                    "hours_spent": 3.0,
                },
            ]
        }
        response = await client.post("/api/standup/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 2
        assert data["updated"] == 0
        assert data["errors"] == []

    async def test_batch_create_logs_upsert(self, client, sample_sprint, sample_member):
        """POST /api/standup/batch should update existing logs."""
        today = str(date.today())
        # First create a log via API
        payload1 = {
            "sprint_id": sample_sprint.id,
            "member_id": sample_member.id,
            "date": today,
            "completed": "Original",
        }
        await client.post("/api/standup", json=payload1)

        # Now batch with updated content
        payload2 = {
            "logs": [
                {
                    "sprint_id": sample_sprint.id,
                    "member_id": sample_member.id,
                    "date": today,
                    "completed": "Updated via batch",
                }
            ]
        }
        response = await client.post("/api/standup/batch", json=payload2)
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 0
        assert data["updated"] == 1

    async def test_get_logs_by_date(self, client, sample_sprint, sample_member):
        """GET /api/standup should filter logs by date."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create logs for different dates via API
        await client.post("/api/standup", json={
            "sprint_id": sample_sprint.id,
            "member_id": sample_member.id,
            "date": str(today),
            "completed": "Today work",
        })
        await client.post("/api/standup", json={
            "sprint_id": sample_sprint.id,
            "member_id": sample_member.id,
            "date": str(yesterday),
            "completed": "Yesterday work",
        })

        # Filter by today
        response = await client.get("/api/standup", params={"date": str(today)})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        for log in data:
            assert "Today work" in log["completed"] or "Today work" == log["completed"]

        # Filter by yesterday
        resp_yest = await client.get("/api/standup", params={"date": str(yesterday)})
        assert resp_yest.status_code == 200
        data_yest = resp_yest.json()
        assert isinstance(data_yest, list)
        assert len(data_yest) >= 1
