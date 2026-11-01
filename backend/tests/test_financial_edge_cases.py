from decimal import Decimal

from app.models.models import BudgetCategory
from app.services.financial_engine import FinancialEngine


def test_financial_engine_zero_budget():
    """Validates behavior when budget is zero (no division by zero or crashing)."""
    total = Decimal("0.00")
    cat = BudgetCategory(name="Venue", allocated_amount=Decimal("0.00"), is_contingency=False)
    summary = FinancialEngine.calculate_budget_summary(total, [cat])
    assert summary.total_budget == Decimal("0.00")
    assert summary.remaining_budget == Decimal("0.00")
    assert summary.is_overspent is False

def test_financial_engine_large_numbers():
    """Validates precision arithmetic on large numbers without floating point loss."""
    total = Decimal("99999999.99")
    cat1 = BudgetCategory(name="Celebration Mega Hall", allocated_amount=Decimal("50000000.00"), is_contingency=False)
    cat2 = BudgetCategory(name="Contingency Reserve", allocated_amount=Decimal("49999999.99"), is_contingency=True)
    summary = FinancialEngine.calculate_budget_summary(total, [cat1, cat2])
    assert summary.total_allocated == Decimal("99999999.99")
    assert summary.unallocated_amount == Decimal("0.00")

def test_financial_engine_unallocated_balance_preservation():
    """Preserves deliberate unallocated balance when allocations sum to less than total budget."""
    total = Decimal("20000.00")
    cat = BudgetCategory(name="Catering", allocated_amount=Decimal("12000.00"), is_contingency=False)
    summary = FinancialEngine.calculate_budget_summary(total, [cat])
    assert summary.total_allocated == Decimal("12000.00")
    assert summary.unallocated_amount == Decimal("8000.00")
    assert summary.remaining_budget == Decimal("20000.00")
