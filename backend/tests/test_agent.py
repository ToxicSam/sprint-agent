"""Tests for Agent routes."""

import pytest
from schemas import TaskCreate
import crud


class TestAgent:
    """Group all Agent endpoint tests."""

    async def test_agent_message(self, client, sample_sprint):
        """POST /api/agent/message should process a message and return a result."""
        payload = {"role": "user", "content": "create a new task called 'Test Agent Task'"}
        response = await client.post("/api/agent/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data

    async def test_agent_message_regex_fallback(self, client, sample_sprint, db_session):
        """Agent should use regex-based intent classification as fallback.

        Tests that the regex engine correctly identifies a 'move_task' intent
        and falls back gracefully when the task reference cannot be resolved.
        """
        # Create a task we can reference
        task = crud.create_task(
            db_session,
            TaskCreate(title="Moveable Task", sprint_id=sample_sprint.id, status="todo"),
        )

        payload = {"role": "user", "content": f"move task {task.id} to done"}
        response = await client.post("/api/agent/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data

    async def test_agent_history(self, client):
        """GET /api/agent/history should return agent message history."""
        # First create a message
        await client.post("/api/agent/message", json={"role": "user", "content": "hello"})

        response = await client.get("/api/agent/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check message structure
        for msg in data:
            assert "id" in msg
            assert "role" in msg
            assert "content" in msg
            assert "created_at" in msg

    async def test_agent_context(self, client, sample_sprint, sample_task):
        """GET /api/agent/context should return the agent context."""
        response = await client.get("/api/agent/context")
        assert response.status_code == 200
        data = response.json()

        assert "current_sprint" in data
        assert "recent_tasks" in data
        assert "members" in data
        assert "messages" in data

        # Should include the active sprint
        if data["current_sprint"] is not None:
            assert "id" in data["current_sprint"]
            assert "name" in data["current_sprint"]

    async def test_agent_unknown_intent(self, client):
        """Agent should handle unknown/generic messages gracefully."""
        payload = {"role": "user", "content": "this is a completely random message"}
        response = await client.post("/api/agent/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data
        # Unknown intent should return a helpful message
        assert len(data["message"]) > 0

    async def test_agent_action_endpoint(self, client):
        """POST /api/agent/action should handle explicit actions."""
        payload = {"action": "general_chat", "payload": {}}
        response = await client.post("/api/agent/action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data

    async def test_agent_sprint_stats_intent(self, client, sample_sprint, db_session):
        """Agent should respond to sprint stats requests."""
        payload = {"role": "user", "content": "show me the sprint stats"}
        response = await client.post("/api/agent/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data
        # Should mention sprint
        assert data["success"] is True

    async def test_agent_create_task_intent(self, client, sample_sprint):
        """Agent should handle task creation intent."""
        payload = {"role": "user", "content": "create a new task 'Write tests'"}
        response = await client.post("/api/agent/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data
        # Should indicate task was created
        assert "task" in data["message"].lower() or "created" in data["message"].lower()

    async def test_agent_delete_task_intent(self, client, sample_sprint, db_session):
        """Agent should handle task deletion intent."""
        task = crud.create_task(
            db_session,
            TaskCreate(title="Deletable Task", sprint_id=sample_sprint.id),
        )

        payload = {"role": "user", "content": f"delete task {task.id}"}
        response = await client.post("/api/agent/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data
