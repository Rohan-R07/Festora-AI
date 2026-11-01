from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.schemas.ai_plan import GeneratedPlanSchema
from app.services.ai_planner import AIPlannerAdapter


@pytest.mark.asyncio
async def test_csv_injection_sanitization(client):
    future_date = (datetime.now(UTC) + timedelta(days=20)).isoformat()
    # Attempt CSV Formula Injection via title and vendor names
    resp = await client.post("/api/v1/events", json={
        "title": "=cmd|' /C calc'!A0",
        "event_type": "birthday",
        "event_date": future_date,
        "location": "@SUM(1+1)",
        "guest_count": 25,
        "total_budget": 2000.00,
        "currency": "USD"
    })
    assert resp.status_code == 201
    event_id = resp.json()["id"]

    # Export CSV and verify dangerous trigger characters are escaped with leading quote
    csv_resp = await client.get(f"/api/v1/events/{event_id}/export/csv")
    assert csv_resp.status_code == 200
    csv_text = csv_resp.text
    assert "'=cmd|' /C calc'!A0" in csv_text
    assert "'@SUM(1+1)" in csv_text

@pytest.mark.asyncio
async def test_html_export_xss_protection(client):
    future_date = (datetime.now(UTC) + timedelta(days=20)).isoformat()
    # Attempt Stored XSS injection via title and location
    resp = await client.post("/api/v1/events", json={
        "title": "<script>alert('xss')</script>",
        "event_type": "wedding",
        "event_date": future_date,
        "location": "<img src=x onerror=alert(1)>",
        "guest_count": 50,
        "total_budget": 5000.00,
        "currency": "USD"
    })
    assert resp.status_code == 201
    event_id = resp.json()["id"]

    html_resp = await client.get(f"/api/v1/events/{event_id}/export/html")
    assert html_resp.status_code == 200
    html_text = html_resp.text
    # Must NOT contain raw unescaped script tag
    assert "<script>alert('xss')</script>" not in html_text
    assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in html_text

@pytest.mark.asyncio
async def test_unauthorized_token_rejection(client):
    resp = await client.get("/api/v1/events", headers={"Authorization": "Bearer invalid.token.signature"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_ai_planner_deterministic_fallback_when_api_missing():
    planner = AIPlannerAdapter()
    # planner has no valid Gemini key or calls deterministic fallback
    plan = await planner.generate_initial_plan(
        event_type="community",
        guest_count=100,
        total_budget=Decimal("5000.00"),
        currency="USD",
        location="Community Center",
        preferences="Eco-friendly compostable supplies"
    )
    assert isinstance(plan, GeneratedPlanSchema)
    assert plan.theme is not None
    assert len(plan.budget_allocations) > 0
