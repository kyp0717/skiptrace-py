"""
Skip Traces API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from api.v1.schemas.skiptrace import SkipTrace, SkipTraceCreate, SkipTraceResult, SkipTraceCostSummary
from api.v1.schemas.common import PaginatedResponse, APIResponse
from api.dependencies import get_db, PaginationParams
from db_connector import DatabaseConnector
from skip_trace_integration import SkipTraceIntegration

router = APIRouter()


@router.post("/lookup", response_model=SkipTraceResult)
async def perform_skip_trace(
    trace_request: SkipTraceCreate,
    background_tasks: BackgroundTasks,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Perform a skip trace lookup for an address
    """
    try:
        # Verify case exists
        case = db.get_case_by_docket(trace_request.docket_number)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Initialize skip trace integration
        skip_trace = SkipTraceIntegration()

        # Parse address (simplified for now)
        address_parts = trace_request.address.split(',')
        if len(address_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid address format")

        address_dict = {
            'street': address_parts[0].strip(),
            'city': address_parts[1].strip() if len(address_parts) > 1 else '',
            'state': address_parts[2].strip() if len(address_parts) > 2 else 'CT',
            'zip': address_parts[3].strip() if len(address_parts) > 3 else ''
        }

        # Perform skip trace
        result = skip_trace.perform_skip_trace(
            docket_number=trace_request.docket_number,
            addresses=[address_dict],
            use_sandbox=trace_request.use_sandbox
        )

        if result['success']:
            return SkipTraceResult(
                docket_number=trace_request.docket_number,
                phones_found=result.get('phone_numbers', []),
                source="sandbox" if trace_request.use_sandbox else "production",
                cost=result.get('cost', 0.07),
                success=True
            )
        else:
            return SkipTraceResult(
                docket_number=trace_request.docket_number,
                phones_found=[],
                source="sandbox" if trace_request.use_sandbox else "production",
                cost=0,
                success=False,
                error=result.get('error', 'Skip trace failed')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=PaginatedResponse[SkipTrace])
async def get_skip_trace_history(
    pagination: PaginationParams = Depends(),
    docket_number: Optional[str] = Query(None, description="Filter by docket number"),
    source: Optional[str] = Query(None, description="Filter by source (sandbox/production)"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get skip trace history with optional filtering
    """
    try:
        # Build query
        query = db.client.table('skiptrace').select("*")

        if docket_number:
            query = query.eq('docket_number', docket_number)
        if source:
            query = query.eq('source', source)

        # Order by created_at descending
        query = query.order('created_at', desc=True)

        response = query.execute()
        traces = response.data if response.data else []

        # Apply pagination
        total = len(traces)
        paginated_traces = traces[pagination.skip:pagination.skip + pagination.limit]

        return PaginatedResponse(
            items=paginated_traces,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_more=(pagination.skip + pagination.limit) < total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-defendant/{defendant_id}")
async def get_skip_traces_by_defendant(
    defendant_id: int,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get all skip traces for a specific defendant
    """
    try:
        # Get defendant to find docket number
        response = db.client.table('defendants').select("docket_number").eq('id', defendant_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Defendant not found")

        docket_number = response.data[0]['docket_number']

        # Get skip traces
        traces_response = db.client.table('skiptrace').select("*").eq(
            'docket_number', docket_number
        ).execute()
        traces = traces_response.data if traces_response.data else []

        return {
            "defendant_id": defendant_id,
            "docket_number": docket_number,
            "skip_traces": traces,
            "total": len(traces)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/town-stats/{town}")
async def get_town_skip_trace_stats(
    town: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get skip trace statistics for a specific town
    Returns total cases found, traced cases, and untraced cases
    """
    try:
        stats = db.get_town_skip_trace_stats(town)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/town-batch")
async def perform_town_batch_skip_trace(
    request: dict,
    background_tasks: BackgroundTasks,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Perform skip trace for all untraced cases in a town
    """
    town = request.get('town')
    if not town:
        raise HTTPException(status_code=400, detail="Town is required")

    try:
        # Get all cases for the town
        cases = db.get_cases_by_town(town)
        if not cases:
            raise HTTPException(status_code=404, detail=f"No cases found for town: {town}")

        # Initialize skip trace integration
        skip_trace = SkipTraceIntegration()

        # Track results
        processed = 0
        skipped = 0
        failed = 0

        for case in cases:
            docket_number = case['docket_number']

            # Check if already skip traced
            existing_traces = db.get_skiptraces_by_docket(docket_number)
            if existing_traces:
                skipped += 1
                continue

            # Get defendant addresses for this case
            defendants = db.get_defendants_by_docket(docket_number)
            if not defendants:
                failed += 1
                continue

            addresses = []
            for defendant in defendants:
                if defendant.get('address'):
                    addresses.append({
                        'street': defendant['address'],
                        'city': defendant.get('town', ''),
                        'state': defendant.get('state', 'CT'),
                        'zip': defendant.get('zip', '')
                    })

            if addresses:
                # Perform skip trace
                result = skip_trace.perform_skip_trace(
                    docket_number=docket_number,
                    addresses=addresses,
                    use_sandbox=False
                )

                if result['success']:
                    processed += 1
                else:
                    failed += 1
            else:
                failed += 1

        return {
            "town": town,
            "total_cases": len(cases),
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "message": f"Skip trace batch completed for {town}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs", response_model=SkipTraceCostSummary)
async def get_skip_trace_costs(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get skip trace cost summary
    """
    try:
        # Get all skip traces
        query = db.client.table('skiptrace').select("source")

        # Add date filters if provided
        if start_date:
            query = query.gte('created_at', start_date)
        if end_date:
            query = query.lte('created_at', end_date)

        response = query.execute()
        traces = response.data if response.data else []

        # Calculate costs
        total_lookups = len(traces)
        sandbox_lookups = sum(1 for t in traces if t.get('source') == 'sandbox')
        production_lookups = total_lookups - sandbox_lookups

        # Assuming $0.07 per production lookup, $0 for sandbox
        total_cost = production_lookups * 0.07
        average_cost = total_cost / total_lookups if total_lookups > 0 else 0

        return SkipTraceCostSummary(
            total_lookups=total_lookups,
            sandbox_lookups=sandbox_lookups,
            production_lookups=production_lookups,
            total_cost=total_cost,
            average_cost_per_lookup=average_cost
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{skip_trace_id}", response_model=APIResponse)
async def delete_skip_trace(
    skip_trace_id: int,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Delete a skip trace record
    """
    try:
        # Check if skip trace exists
        response = db.client.table('skiptrace').select("*").eq('id', skip_trace_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Skip trace not found")

        # Delete skip trace
        db.client.table('skiptrace').delete().eq('id', skip_trace_id).execute()

        return APIResponse(
            success=True,
            message=f"Skip trace {skip_trace_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))