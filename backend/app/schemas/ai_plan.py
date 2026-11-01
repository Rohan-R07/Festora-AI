from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class GeneratedBudgetItem(BaseModel):
    category: str = Field(..., description="Category name, e.g. Venue, Catering, Decor")
    allocated_percentage: Decimal = Field(..., ge=0, le=100, description="Percentage of total budget")
    is_contingency: bool = False
    suggested_expenses: List[str] = []

class GeneratedTaskItem(BaseModel):
    title: str
    description: Optional[str] = None
    days_before_event: int = Field(..., ge=0, description="Number of days before the event this task should be completed")
    priority: str = Field(default="medium", description="low, medium, high, critical")

class GeneratedVendorItem(BaseModel):
    category: str
    suggested_role_description: str
    estimated_budget_share: Optional[Decimal] = None

class GeneratedScheduleItem(BaseModel):
    time_offset_or_hour: str = Field(..., description="e.g. '09:00 AM' or 'T - 2 hours'")
    activity: str
    description: Optional[str] = None

class GeneratedPlanSchema(BaseModel):
    theme: str
    concept_summary: str
    personalized_ideas: List[str]
    budget_allocations: List[GeneratedBudgetItem]
    tasks: List[GeneratedTaskItem]
    vendor_categories: List[GeneratedVendorItem]
    event_day_schedule: List[GeneratedScheduleItem]
    risks_and_mitigations: List[str]

class PlanRevisionRequest(BaseModel):
    prompt: str = Field(..., min_length=2, max_length=1000)

class PlanRevisionResponse(BaseModel):
    message_id: str
    explanation: str
    proposed_changes: Optional[GeneratedPlanSchema] = None

