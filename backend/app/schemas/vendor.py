from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

VALID_VENDOR_STATUSES = {"considering", "contacted", "quoted", "booked", "rejected"}

class VendorCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    quoted_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    status: str = Field(default="considering")
    is_ai_suggested: bool = False
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def val_vendor_status(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_VENDOR_STATUSES:
            raise ValueError(f"Status must be one of {list(VALID_VENDOR_STATUSES)}")
        return clean

class VendorUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    quoted_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    status: Optional[str] = None
    notes: Optional[str] = None

