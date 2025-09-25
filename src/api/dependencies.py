"""
Shared dependencies for FastAPI endpoints
"""

from typing import Optional
from fastapi import Query
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_connector import DatabaseConnector


def get_db() -> DatabaseConnector:
    """Get database connection"""
    return DatabaseConnector()


class PaginationParams:
    """Common pagination parameters"""
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
    ):
        self.skip = skip
        self.limit = limit


class SearchParams:
    """Common search parameters"""
    def __init__(
        self,
        q: Optional[str] = Query(None, description="Search query"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")
    ):
        self.q = q
        self.sort_by = sort_by
        self.sort_order = sort_order