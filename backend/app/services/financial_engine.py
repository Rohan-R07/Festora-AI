from decimal import ROUND_HALF_UP, Decimal
from typing import List

from app.models.models import BudgetCategory
from app.schemas.event import BudgetSummary

TWO_PLACES = Decimal("0.01")

def round_money(val: Decimal) -> Decimal:
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

class FinancialEngine:
    @staticmethod
    def calculate_budget_summary(total_budget: Decimal, categories: List[BudgetCategory]) -> BudgetSummary:
        """
        Deterministic, floating-point-free financial calculation for event budgets.
        Calculates:
        - Total allocated across all categories
        - Contingency allocated
        - Total estimated expenses
        - Total actual expenses
        - Remaining budget
        - Overspending detection and amount
        """
        total_allocated = Decimal("0.00")
        contingency_allocated = Decimal("0.00")
        total_estimated = Decimal("0.00")
        total_actual = Decimal("0.00")

        for cat in categories:
            total_allocated += cat.allocated_amount
            if cat.is_contingency:
                contingency_allocated += cat.allocated_amount

            for exp in cat.expenses:
                total_estimated += exp.estimated_amount
                if exp.actual_amount is not None:
                    total_actual += exp.actual_amount

        # Reconcile unallocated
        unallocated = total_budget - total_allocated

        # Effective spend is actual where entered, or estimated if pending
        effective_spend = Decimal("0.00")
        for cat in categories:
            for exp in cat.expenses:
                if exp.actual_amount is not None:
                    effective_spend += exp.actual_amount
                else:
                    effective_spend += exp.estimated_amount

        remaining = total_budget - effective_spend
        is_overspent = remaining < Decimal("0.00")
        overspent_amount = abs(remaining) if is_overspent else Decimal("0.00")

        return BudgetSummary(
            total_budget=round_money(total_budget),
            total_allocated=round_money(total_allocated),
            unallocated_amount=round_money(unallocated),
            total_estimated=round_money(total_estimated),
            total_actual=round_money(total_actual),
            remaining_budget=round_money(remaining),
            overspent_amount=round_money(overspent_amount),
            is_overspent=is_overspent,
            contingency_allocated=round_money(contingency_allocated)
        )

    @staticmethod
    def reconcile_allocations(total_budget: Decimal, percentages: List[Decimal]) -> List[Decimal]:
        """
        Reconciles list of percentage allocations so their sum in currency units exactly equals total_budget,
        eliminating fractional cent rounding drifts.
        """
        allocations = []
        accumulated = Decimal("0.00")

        for i, pct in enumerate(percentages):
            if i == len(percentages) - 1:
                # Last category absorbs residual rounding difference
                final_alloc = total_budget - accumulated
                allocations.append(round_money(final_alloc))
            else:
                alloc = round_money(total_budget * (pct / Decimal("100.00")))
                allocations.append(alloc)
                accumulated += alloc

        return allocations

