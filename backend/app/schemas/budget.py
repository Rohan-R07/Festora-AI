from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BudgetCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    allocated_amount: Decimal = Field(..., ge=Decimal("0.00"))
    is_contingency: bool = False

class BudgetCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    allocated_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    is_contingency: Optional[bool] = None

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    estimated_amount: Decimal = Field(..., ge=Decimal("0.00"))
    actual_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    is_paid: bool = False
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None

class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    estimated_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    actual_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    is_paid: Optional[bool] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None

