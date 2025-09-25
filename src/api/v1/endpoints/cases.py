"""
Cases API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from api.v1.schemas.case import Case, CaseCreate, CaseUpdate, CaseWithDefendants
from api.v1.schemas.common import PaginatedResponse, APIResponse
from api.dependencies import get_db, PaginationParams
from db_connector import DatabaseConnector

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[Case])
async def list_cases(
    pagination: PaginationParams = Depends(),
    town: Optional[str] = Query(None, description="Filter by town"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    List all cases with optional filtering and pagination
    """
    try:
        # Get cases based on filter
        if town:
            cases = db.get_cases_by_town(town)
        else:
            # Get all cases (with pagination in mind)
            response = db.client.table('cases').select("*").execute()
            cases = response.data if response.data else []

        # Apply pagination
        total = len(cases)
        paginated_cases = cases[pagination.skip:pagination.skip + pagination.limit]

        return PaginatedResponse(
            items=paginated_cases,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_more=(pagination.skip + pagination.limit) < total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_cases(
    q: str = Query(..., description="Search query"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    Search cases by case name or docket number
    """
    try:
        # Search in case_name and docket_number
        response = db.client.table('cases').select("*").or_(
            f"case_name.ilike.%{q}%,docket_number.ilike.%{q}%"
        ).execute()

        cases = response.data if response.data else []
        return {
            "cases": cases,
            "total": len(cases),
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-town/{town}")
async def get_cases_by_town(
    town: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get all cases for a specific town
    """
    try:
        cases = db.get_cases_by_town(town)
        return {
            "town": town,
            "cases": cases,
            "total": len(cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{docket_number}", response_model=CaseWithDefendants)
async def get_case(
    docket_number: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get a single case by docket number with defendants
    """
    try:
        case = db.get_case_by_docket(docket_number)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Get associated defendants
        defendants = db.get_defendants_by_docket(docket_number)

        return CaseWithDefendants(
            **case,
            defendants=defendants,
            defendant_count=len(defendants)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Case)
async def create_case(
    case_data: CaseCreate,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Create a new case
    """
    try:
        # Check if case already exists
        existing = db.get_case_by_docket(case_data.docket_number)
        if existing:
            raise HTTPException(status_code=400, detail="Case with this docket number already exists")

        # Create case
        result = db.insert_case(case_data.model_dump())
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create case")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{docket_number}", response_model=Case)
async def update_case(
    docket_number: str,
    case_update: CaseUpdate,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Update a case by docket number
    """
    try:
        # Check if case exists
        existing = db.get_case_by_docket(docket_number)
        if not existing:
            raise HTTPException(status_code=404, detail="Case not found")

        # Update case
        update_data = case_update.model_dump(exclude_unset=True)
        if update_data:
            response = db.client.table('cases').update(update_data).eq(
                'docket_number', docket_number
            ).execute()

            if response.data:
                return response.data[0]

        return existing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{docket_number}", response_model=APIResponse)
async def delete_case(
    docket_number: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Delete a case by docket number
    """
    try:
        # Check if case exists
        existing = db.get_case_by_docket(docket_number)
        if not existing:
            raise HTTPException(status_code=404, detail="Case not found")

        # Delete case (cascade will handle defendants and skiptraces)
        response = db.client.table('cases').delete().eq(
            'docket_number', docket_number
        ).execute()

        return APIResponse(
            success=True,
            message=f"Case {docket_number} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))