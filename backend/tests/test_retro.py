"""Tests for Retro routes."""

import pytest
from schemas import RetroCreate, RetroRatingCreate
import crud


class TestRetro:
    """Group all Retro endpoint tests."""

    async def test_create_retro_item(self, client, sample_sprint):
        """POST /api/retro should create a retro item."""
        payload = {
            "sprint_id": sample_sprint.id,
            "category": "liked",
            "item": "Great teamwork",
            "votes": 0,
        }
        response = await client.post("/api/retro", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["sprint_id"] == sample_sprint.id
        assert data["category"] == "liked"
        assert data["item"] == "Great teamwork"
        assert data["votes"] == 0
        assert "id" in data

    async def test_vote_retro(self, client, db_session, sample_sprint):
        """POST /api/retro/vote should increment votes."""
        retro = crud.create_retro(db_session, RetroCreate(
            sprint_id=sample_sprint.id,
            category="liked",
            item="Good communication",
            votes=2,
        ))

        payload = {"retro_id": retro.id}
        response = await client.post("/api/retro/vote", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["votes"] == 3
        assert data["id"] == retro.id

    async def test_vote_retro_not_found(self, client):
        """POST /api/retro/vote should 404 for a missing retro item."""
        payload = {"retro_id": "nonexistent-id"}
        response = await client.post("/api/retro/vote", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Retro item not found"

    async def test_create_rating(self, client, sample_sprint):
        """POST /api/retro/rate should create a retro rating."""
        payload = {
            "sprint_id": sample_sprint.id,
            "dimension": "velocity",
            "score": 8,
        }
        response = await client.post("/api/retro/rate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["sprint_id"] == sample_sprint.id
        assert data["dimension"] == "velocity"
        assert data["score"] == 8
        assert "id" in data

    async def test_get_retro_report(self, client, db_session, sample_sprint):
        """GET /api/retro/{sprint_id}/report should return the retro report."""
        # Create retro items
        crud.create_retro(db_session, RetroCreate(sprint_id=sample_sprint.id, category="liked", item="Good collaboration"))
        crud.create_retro(db_session, RetroCreate(sprint_id=sample_sprint.id, category="disliked", item="Too many meetings"))
        crud.create_retro(db_session, RetroCreate(sprint_id=sample_sprint.id, category="action", item="Reduce meeting time"))
        # Create ratings
        crud.create_retro_rating(db_session, RetroRatingCreate(sprint_id=sample_sprint.id, dimension="velocity", score=7))
        crud.create_retro_rating(db_session, RetroRatingCreate(sprint_id=sample_sprint.id, dimension="velocity", score=9))

        response = await client.get(f"/api/retro/{sample_sprint.id}/report")
        assert response.status_code == 200
        data = response.json()
        assert "liked" in data
        assert "disliked" in data
        assert "action_items" in data
        assert "ratings" in data
        assert "summary" in data

        # Verify content
        assert len(data["liked"]) == 1
        assert data["liked"][0]["item"] == "Good collaboration"
        assert len(data["disliked"]) == 1
        assert data["disliked"][0]["item"] == "Too many meetings"
        assert len(data["action_items"]) == 1
        assert data["action_items"][0]["item"] == "Reduce meeting time"

        # Average rating for velocity = (7+9)/2 = 8.0
        assert "velocity" in data["ratings"]
        assert data["ratings"]["velocity"] == 8.0

        # Summary should mention counts
        assert "1 liked" in data["summary"]
        assert "1 disliked" in data["summary"]
        assert "1 action items" in data["summary"]

    async def test_get_retro_items_by_sprint(self, client, db_session, sample_sprint):
        """GET /api/retro/{sprint_id} should list retro items for a sprint."""
        crud.create_retro(db_session, RetroCreate(sprint_id=sample_sprint.id, category="liked", item="Item 1"))
        crud.create_retro(db_session, RetroCreate(sprint_id=sample_sprint.id, category="liked", item="Item 2"))

        response = await client.get(f"/api/retro/{sample_sprint.id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
