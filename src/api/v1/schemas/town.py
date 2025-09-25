"""
Town Pydantic schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TownBase(BaseModel):
    """Base town schema"""
    town: str = Field(..., description="Town name")
    county: str = Field(..., description="County name")


class TownCreate(TownBase):
    """Schema for creating a town"""
    pass


class Town(TownBase):
    """Complete town schema with database fields"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TownValidation(BaseModel):
    """Town validation result"""
    town: str
    is_valid: bool
    county: Optional[str] = None
    suggestions: List[str] = []


class CountyInfo(BaseModel):
    """County information"""
    county: str
    town_count: int
    towns: List[str]