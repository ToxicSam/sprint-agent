"""Tests for Member routes."""

import pytest
from schemas import MemberCreate
import crud


class TestMember:
    """Group all Member endpoint tests."""

    async def test_create_member(self, client):
        """POST /api/members should create a new member."""
        payload = {"name": "Bob", "role": "designer", "capacity": 6.0}
        response = await client.post("/api/members", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Bob"
        assert data["role"] == "designer"
        assert data["capacity"] == 6.0
        assert "id" in data
        assert "created_at" in data

    async def test_list_members(self, client, sample_member):
        """GET /api/members should list all members."""
        # Create an additional member
        await client.post("/api/members", json={"name": "Bob", "role": "qa"})

        response = await client.get("/api/members")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        names = [m["name"] for m in data]
        assert "Alice" in names
        assert "Bob" in names

    async def test_update_member(self, client, sample_member):
        """PUT /api/members/{id} should update the member."""
        payload = {"name": "Alice Updated", "role": "senior_dev"}
        response = await client.put(f"/api/members/{sample_member.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Alice Updated"
        assert data["role"] == "senior_dev"
        assert data["id"] == sample_member.id

    async def test_update_member_not_found(self, client):
        """PUT /api/members/{id} should 404 for a missing member."""
        payload = {"name": "Ghost"}
        response = await client.put("/api/members/nonexistent-id", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Member not found"

    async def test_delete_member(self, client, sample_member):
        """DELETE /api/members/{id} should delete the member."""
        response = await client.delete(f"/api/members/{sample_member.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True

        # Verify it is gone
        list_resp = await client.get("/api/members")
        assert list_resp.status_code == 200
        ids = [m["id"] for m in list_resp.json()]
        assert sample_member.id not in ids

    async def test_delete_member_not_found(self, client):
        """DELETE /api/members/{id} should 404 for a missing member."""
        response = await client.delete("/api/members/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Member not found"
