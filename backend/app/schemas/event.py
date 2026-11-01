from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

VALID_EVENT_TYPES = {"wedding", "birthday", "college", "community"}
VALID_CURRENCIES = {"USD", "EUR", "GBP", "INR", "CAD", "AUD"}

class EventBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    event_type: str = Field(..., description="wedding, birthday, college, community")
    event_date: datetime
    timezone: str = Field(default="UTC", max_length=50)
    location: str = Field(..., min_length=2, max_length=255)
    guest_count: int = Field(..., gt=0, le=50000)
    total_budget: Decimal = Field(..., gt=0, le=Decimal("100000000.00"))
    currency: str = Field(default="USD", max_length=10)
    preferences: Optional[str] = Field(default=None, max_length=5000)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_EVENT_TYPES:
            raise ValueError(f"Event type must be one of {list(VALID_EVENT_TYPES)}")
        return clean

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_CURRENCIES:
            raise ValueError(f"Currency must be one of {list(VALID_CURRENCIES)}")
        return clean

    @field_validator("total_budget")
    @classmethod
    def validate_budget(cls, v: Decimal) -> Decimal:
        if v <= Decimal("0"):
            raise ValueError("Budget must be strictly positive")
        return v.quantize(Decimal("0.01"))

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    event_date: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    guest_count: Optional[int] = Field(None, gt=0, le=50000)
    total_budget: Optional[Decimal] = Field(None, gt=0, le=Decimal("100000000.00"))
    preferences: Optional[str] = Field(None, max_length=5000)
    theme: Optional[str] = Field(None, max_length=255)
    concept_summary: Optional[str] = Field(None, max_length=5000)

class ExpenseResponse(BaseModel):
    id: str
    category_id: str
    title: str
    estimated_amount: Decimal
    actual_amount: Optional[Decimal]
    is_paid: bool
    paid_date: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True

class BudgetCategoryResponse(BaseModel):
    id: str
    event_id: str
    name: str
    allocated_amount: Decimal
    is_contingency: bool
    expenses: List[ExpenseResponse] = []

    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    id: str
    event_id: str
    title: str
    description: Optional[str]
    due_date: datetime
    priority: str
    status: str
    dependency_id: Optional[str]
    completed_at: Optional[datetime]
    is_overdue: bool = False

    class Config:
        from_attributes = True

class VendorResponse(BaseModel):
    id: str
    event_id: str
    category: str
    name: str
    contact_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    quoted_amount: Optional[Decimal]
    status: str
    is_ai_suggested: bool
    notes: Optional[str]

    class Config:
        from_attributes = True

class BudgetSummary(BaseModel):
    total_budget: Decimal
    total_allocated: Decimal
    unallocated_amount: Decimal
    total_estimated: Decimal
    total_actual: Decimal
    remaining_budget: Decimal
    overspent_amount: Decimal
    is_overspent: bool
    contingency_allocated: Decimal

class EventDetailResponse(EventBase):
    id: str
    user_id: str
    theme: Optional[str]
    concept_summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    budget_categories: List[BudgetCategoryResponse] = []
    tasks: List[TaskResponse] = []
    vendors: List[VendorResponse] = []
    budget_summary: Optional[BudgetSummary] = None

    class Config:
        from_attributes = True

