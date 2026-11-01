from decimal import Decimal

from app.models.models import BudgetCategory, Expense
from app.services.financial_engine import FinancialEngine


def test_financial_engine_budget_summary():
    total_budget = Decimal("10000.00")

    cat1 = BudgetCategory(name="Venue", allocated_amount=Decimal("5000.00"), is_contingency=False)
    exp1 = Expense(title="Deposit", estimated_amount=Decimal("3000.00"), actual_amount=Decimal("2800.00"))
    exp2 = Expense(title="Sound", estimated_amount=Decimal("2000.00"), actual_amount=None)
    cat1.expenses = [exp1, exp2]

    cat2 = BudgetCategory(name="Contingency", allocated_amount=Decimal("1000.00"), is_contingency=True)
    cat2.expenses = []

    summary = FinancialEngine.calculate_budget_summary(total_budget, [cat1, cat2])

    assert summary.total_budget == Decimal("10000.00")
    assert summary.total_allocated == Decimal("6000.00")
    assert summary.unallocated_amount == Decimal("4000.00")
    assert summary.contingency_allocated == Decimal("1000.00")
    assert summary.total_estimated == Decimal("5000.00")
    assert summary.total_actual == Decimal("2800.00")
    # Effective spend = 2800 (actual) + 2000 (estimated remaining) = 4800
    assert summary.remaining_budget == Decimal("5200.00")
    assert summary.is_overspent is False
    assert summary.overspent_amount == Decimal("0.00")

def test_financial_engine_overspending_flag():
    total_budget = Decimal("5000.00")
    cat = BudgetCategory(name="Catering", allocated_amount=Decimal("5000.00"), is_contingency=False)
    exp = Expense(title="Dinner", estimated_amount=Decimal("5000.00"), actual_amount=Decimal("6200.50"))
    cat.expenses = [exp]

    summary = FinancialEngine.calculate_budget_summary(total_budget, [cat])

    assert summary.is_overspent is True
    assert summary.remaining_budget == Decimal("-1200.50")
    assert summary.overspent_amount == Decimal("1200.50")

def test_reconcile_allocations_exact_cents():
    total = Decimal("1000.00")
    # Three equal slices: 33.333% each
    percentages = [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]
    allocations = FinancialEngine.reconcile_allocations(total, percentages)

    assert sum(allocations) == total
    assert len(allocations) == 3

