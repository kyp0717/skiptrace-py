"""
Defendants API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from api.v1.schemas.defendant import Defendant, DefendantCreate, DefendantUpdate, DefendantWithSkipTraces
from api.v1.schemas.common import PaginatedResponse, APIResponse
from api.dependencies import get_db, PaginationParams
from db_connector import DatabaseConnector

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[Defendant])
async def list_defendants(
    pagination: PaginationParams = Depends(),
    docket_number: Optional[str] = Query(None, description="Filter by docket number"),
    town: Optional[str] = Query(None, description="Filter by town"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    List all defendants with optional filtering and pagination
    """
    try:
        # Build query
        query = db.client.table('defendants').select("*")

        if docket_number:
            query = query.eq('docket_number', docket_number)
        if town:
            query = query.eq('town', town)

        response = query.execute()
        defendants = response.data if response.data else []

        # Apply pagination
        total = len(defendants)
        paginated_defendants = defendants[pagination.skip:pagination.skip + pagination.limit]

        return PaginatedResponse(
            items=paginated_defendants,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_more=(pagination.skip + pagination.limit) < total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-case/{docket_number}")
async def get_defendants_by_case(
    docket_number: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get all defendants for a specific case
    """
    try:
        defendants = db.get_defendants_by_docket(docket_number)
        return {
            "docket_number": docket_number,
            "defendants": defendants,
            "total": len(defendants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{defendant_id}", response_model=DefendantWithSkipTraces)
async def get_defendant(
    defendant_id: int,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get a single defendant by ID with skip traces
    """
    try:
        # Get defendant
        response = db.client.table('defendants').select("*").eq('id', defendant_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Defendant not found")

        defendant = response.data[0]

        # Get associated skip traces
        skip_response = db.client.table('skiptrace').select("*").eq(
            'docket_number', defendant['docket_number']
        ).execute()
        skip_traces = skip_response.data if skip_response.data else []

        return DefendantWithSkipTraces(
            **defendant,
            skip_traces=skip_traces,
            phone_count=len(skip_traces)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Defendant)
async def create_defendant(
    defendant_data: DefendantCreate,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Create a new defendant
    """
    try:
        # Check if case exists
        case = db.get_case_by_docket(defendant_data.docket_number)
        if not case:
            raise HTTPException(status_code=400, detail="Case with this docket number does not exist")

        # Check if defendant already exists
        existing = db.get_defendant_by_docket_and_name(
            defendant_data.docket_number,
            defendant_data.name
        )
        if existing:
            raise HTTPException(status_code=400, detail="Defendant already exists for this case")

        # Create defendant
        result = db.insert_defendant(defendant_data.model_dump())
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create defendant")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{defendant_id}", response_model=Defendant)
async def update_defendant(
    defendant_id: int,
    defendant_update: DefendantUpdate,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Update a defendant by ID
    """
    try:
        # Check if defendant exists
        response = db.client.table('defendants').select("*").eq('id', defendant_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Defendant not found")

        # Update defendant
        update_data = defendant_update.model_dump(exclude_unset=True)
        if update_data:
            update_response = db.client.table('defendants').update(update_data).eq(
                'id', defendant_id
            ).execute()

            if update_response.data:
                return update_response.data[0]

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{defendant_id}", response_model=APIResponse)
async def delete_defendant(
    defendant_id: int,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Delete a defendant by ID
    """
    try:
        # Check if defendant exists
        response = db.client.table('defendants').select("*").eq('id', defendant_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Defendant not found")

        # Delete defendant
        db.client.table('defendants').delete().eq('id', defendant_id).execute()

        return APIResponse(
            success=True,
            message=f"Defendant {defendant_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))