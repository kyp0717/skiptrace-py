"""
Defendant Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class DefendantBase(BaseModel):
    """Base defendant schema"""
    name: str = Field(..., description="Defendant's name")
    docket_number: str = Field(..., description="Associated case docket number")
    address: Optional[str] = Field(None, description="Defendant's address")
    town: Optional[str] = Field(None, description="Town")
    state: Optional[str] = Field(None, description="State")
    zip: Optional[str] = Field(None, description="ZIP code")


class DefendantCreate(DefendantBase):
    """Schema for creating a defendant"""
    pass


class DefendantUpdate(BaseModel):
    """Schema for updating a defendant"""
    name: Optional[str] = None
    address: Optional[str] = None
    town: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class Defendant(DefendantBase):
    """Complete defendant schema with database fields"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DefendantWithSkipTraces(Defendant):
    """Defendant with associated skip traces"""
    skip_traces: List[dict] = []
    phone_count: int = 0