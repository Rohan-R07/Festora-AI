from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_event_with_plan_generation(client):
    event_date = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
    payload = {
        "title": "Grand Gala 2026",
        "event_type": "wedding",
        "event_date": event_date,
        "timezone": "UTC",
        "location": "Skyline Ballroom",
        "guest_count": 120,
        "total_budget": 25000.00,
        "currency": "USD",
        "preferences": "Modern minimalist"
    }
    resp = await client.post("/api/v1/events", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Grand Gala 2026"
    assert len(data["budget_categories"]) > 0
    assert len(data["tasks"]) > 0
    assert len(data["vendors"]) > 0
    assert data["budget_summary"] is not None
    assert float(data["budget_summary"]["total_budget"]) == 25000.00

@pytest.mark.asyncio
async def test_event_validation_errors(client):
    # Past date error
    past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    resp = await client.post("/api/v1/events", json={
        "title": "Bad Event",
        "event_type": "birthday",
        "event_date": past_date,
        "location": "Home",
        "guest_count": 10,
        "total_budget": 500.00,
        "currency": "USD"
    })
    assert resp.status_code == 400

    # Negative budget
    future_date = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    resp2 = await client.post("/api/v1/events", json={
        "title": "Negative Budget Event",
        "event_type": "birthday",
        "event_date": future_date,
        "location": "Home",
        "guest_count": 10,
        "total_budget": -500.00,
        "currency": "USD"
    })
    assert resp2.status_code == 422

@pytest.mark.asyncio
async def test_task_status_lifecycle_and_expense_update(client):
    future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    resp = await client.post("/api/v1/events", json={
        "title": "Milestone Birthday",
        "event_type": "birthday",
        "event_date": future_date,
        "location": "Private Lounge",
        "guest_count": 40,
        "total_budget": 3000.00,
        "currency": "USD"
    })
    event_data = resp.json()
    event_id = event_data["id"]
    task_id = event_data["tasks"][0]["id"]
    cat_id = event_data["budget_categories"][0]["id"]

    # 1. Update task to completed
    task_resp = await client.put(f"/api/v1/events/{event_id}/tasks/{task_id}", json={
        "status": "completed"
    })
    assert task_resp.status_code == 200
    updated_event = task_resp.json()
    updated_task = next(t for t in updated_event["tasks"] if t["id"] == task_id)
    assert updated_task["status"] == "completed"
    assert updated_task["completed_at"] is not None

    # 2. Add and update actual expense
    exp_resp = await client.post(f"/api/v1/events/{event_id}/categories/{cat_id}/expenses", json={
        "title": "Custom Birthday Cake",
        "estimated_amount": 250.00,
        "actual_amount": 275.00,
        "is_paid": True
    })
    assert exp_resp.status_code == 200
    event_with_exp = exp_resp.json()
    assert float(event_with_exp["budget_summary"]["total_actual"]) >= 275.00

@pytest.mark.asyncio
async def test_ownership_isolation(client):
    # Create event as User A
    reg_a = await client.post("/api/v1/auth/register", json={
        "email": "user_a@example.com",
        "password": "password_a_123",
        "full_name": "User Alpha"
    })
    token_a = reg_a.json()["access_token"]

    future_date = (datetime.now(timezone.utc) + timedelta(days=50)).isoformat()
    create_resp = await client.post("/api/v1/events", json={
        "title": "Secret Event User A",
        "event_type": "wedding",
        "event_date": future_date,
        "location": "Secret Garden",
        "guest_count": 50,
        "total_budget": 10000.00,
        "currency": "USD"
    }, headers={"Authorization": f"Bearer {token_a}"})
    event_id = create_resp.json()["id"]

    # Register User B
    reg_b = await client.post("/api/v1/auth/register", json={
        "email": "user_b@example.com",
        "password": "password_b_123",
        "full_name": "User Beta"
    })
    token_b = reg_b.json()["access_token"]

    # User B attempts to access User A's event -> 403 Forbidden
    access_attempt = await client.get(f"/api/v1/events/{event_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert access_attempt.status_code == 403

