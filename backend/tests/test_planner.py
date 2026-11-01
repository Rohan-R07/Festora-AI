from decimal import Decimal

import pytest

from app.services.deterministic_planner import DeterministicFallbackPlanner


@pytest.mark.parametrize("event_type", ["wedding", "birthday", "college", "community", "corporate_unknown"])
def test_deterministic_planner_generates_valid_schema(event_type):
    plan = DeterministicFallbackPlanner.generate_plan(
        event_type=event_type,
        guest_count=100,
        total_budget=Decimal("15000.00"),
        location="Central Park, NY",
        preferences="Eco-friendly decor"
    )

    assert plan.theme is not None
    assert len(plan.theme) > 0
    assert len(plan.personalized_ideas) > 0
    assert len(plan.budget_allocations) > 0
    assert len(plan.tasks) > 0
    assert len(plan.vendor_categories) > 0
    assert len(plan.event_day_schedule) > 0
    assert len(plan.risks_and_mitigations) > 0

    # Ensure allocations sum to 100%
    total_pct = sum(b.allocated_percentage for b in plan.budget_allocations)
    assert total_pct == Decimal("100.0")

    # Verify task ordering days before event
    for t in plan.tasks:
        assert t.days_before_event >= 0
        assert t.priority in {"low", "medium", "high", "critical"}

