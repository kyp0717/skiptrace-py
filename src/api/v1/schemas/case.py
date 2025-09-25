"""
Case Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CaseBase(BaseModel):
    """Base case schema"""
    case_name: str = Field(..., description="Name of the case")
    docket_number: str = Field(..., description="Unique docket number")
    docket_url: Optional[str] = Field(None, description="URL to case details")
    town: Optional[str] = Field(None, description="Town where case is filed")


class CaseCreate(CaseBase):
    """Schema for creating a case"""
    pass


class CaseUpdate(BaseModel):
    """Schema for updating a case"""
    case_name: Optional[str] = None
    docket_url: Optional[str] = None
    town: Optional[str] = None


class Case(CaseBase):
    """Complete case schema with database fields"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseWithDefendants(Case):
    """Case with associated defendants"""
    defendants: List[dict] = []
    defendant_count: int = 0


class CaseSearchResult(BaseModel):
    """Case search result"""
    cases: List[Case]
    total: int
    query: str