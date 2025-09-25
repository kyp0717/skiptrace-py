"""
Common Pydantic schemas
"""

from typing import List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None
    status_code: int = 400

class BulkOperationResult(BaseModel):
    """Result of bulk operations"""
    total: int
    successful: int
    failed: int
    errors: List[str] = []