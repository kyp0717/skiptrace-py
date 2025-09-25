"""
Skip Trace Pydantic schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SkipTraceBase(BaseModel):
    """Base skip trace schema"""
    defendant_id: Optional[int] = Field(None, description="Associated defendant ID")
    docket_number: str = Field(..., description="Associated case docket number")
    phone_number: str = Field(..., description="Phone number found")
    phone_type: Optional[str] = Field(None, description="Type of phone (mobile, landline, etc.)")
    source: str = Field("production", description="Source: sandbox or production")
    api_response: Optional[Dict[str, Any]] = Field(None, description="Raw API response")


class SkipTraceCreate(BaseModel):
    """Schema for creating a skip trace request"""
    docket_number: str = Field(..., description="Docket number to trace")
    address: str = Field(..., description="Address to skip trace")
    use_sandbox: bool = Field(False, description="Use sandbox API instead of production")


class SkipTrace(SkipTraceBase):
    """Complete skip trace schema with database fields"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkipTraceResult(BaseModel):
    """Result of skip trace operation"""
    docket_number: str
    phones_found: List[str]
    source: str
    cost: float
    success: bool
    error: Optional[str] = None


class SkipTraceCostSummary(BaseModel):
    """Skip trace cost summary"""
    total_lookups: int
    sandbox_lookups: int
    production_lookups: int
    total_cost: float
    average_cost_per_lookup: float