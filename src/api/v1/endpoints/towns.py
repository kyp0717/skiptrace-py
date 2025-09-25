"""
Connecticut Towns API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from api.v1.schemas.town import Town, TownCreate, TownValidation, CountyInfo
from api.v1.schemas.common import APIResponse
from api.dependencies import get_db
from db_connector import DatabaseConnector
from ct_town_scraper import CTTownScraper

router = APIRouter()


@router.get("/", response_model=List[Town])
async def list_towns(
    county: Optional[str] = Query(None, description="Filter by county"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    List all Connecticut towns with optional county filter
    """
    try:
        if county:
            towns = db.get_towns_by_county(county)
        else:
            towns = db.get_all_ct_towns()

        return towns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counties", response_model=List[CountyInfo])
async def list_counties(
    db: DatabaseConnector = Depends(get_db)
):
    """
    List all Connecticut counties with town counts
    """
    try:
        # Get all towns
        all_towns = db.get_all_ct_towns()

        # Group by county
        counties_dict = {}
        for town in all_towns:
            county = town['county']
            if county not in counties_dict:
                counties_dict[county] = []
            counties_dict[county].append(town['town'])

        # Create response
        counties_info = []
        for county, towns in sorted(counties_dict.items()):
            counties_info.append(CountyInfo(
                county=county,
                town_count=len(towns),
                towns=sorted(towns)
            ))

        return counties_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-county/{county}")
async def get_towns_by_county(
    county: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get all towns in a specific county
    """
    try:
        towns = db.get_towns_by_county(county)
        if not towns:
            raise HTTPException(status_code=404, detail=f"County '{county}' not found")

        return {
            "county": county,
            "towns": [t['town'] for t in towns],
            "total": len(towns)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_towns(
    q: str = Query(..., min_length=2, description="Search query"),
    db: DatabaseConnector = Depends(get_db)
):
    """
    Fuzzy search for Connecticut towns
    """
    try:
        # Get all towns
        all_towns = db.get_all_ct_towns()

        # Perform fuzzy search
        q_lower = q.lower()
        matches = []

        for town in all_towns:
            town_name = town['town'].lower()
            if q_lower in town_name or town_name.startswith(q_lower):
                matches.append(town)

        # Sort by relevance (exact match first, then starts with, then contains)
        def sort_key(town):
            town_name = town['town'].lower()
            if town_name == q_lower:
                return 0
            elif town_name.startswith(q_lower):
                return 1
            else:
                return 2

        matches.sort(key=sort_key)

        return {
            "query": q,
            "matches": matches[:10],  # Limit to top 10 matches
            "total": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/{town_name}", response_model=TownValidation)
async def validate_town(
    town_name: str,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Validate if a town name is a valid Connecticut town
    """
    try:
        # Get all towns for validation
        all_towns = db.get_all_ct_towns()

        # Create scraper instance for validation
        scraper = CTTownScraper()
        scraper.towns_data = [(t['town'], t['county']) for t in all_towns]

        # Validate town
        is_valid = scraper.validate_town(town_name)
        county = scraper.get_county_for_town(town_name) if is_valid else None

        # Get suggestions if not valid
        suggestions = []
        if not is_valid:
            town_lower = town_name.lower()
            for town in all_towns[:50]:  # Check first 50 towns for suggestions
                if town_lower in town['town'].lower():
                    suggestions.append(town['town'])
                if len(suggestions) >= 5:
                    break

        return TownValidation(
            town=town_name,
            is_valid=is_valid,
            county=county,
            suggestions=suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/populate", response_model=APIResponse)
async def populate_towns(
    db: DatabaseConnector = Depends(get_db)
):
    """
    Populate or refresh Connecticut towns data from scraper
    """
    try:
        # Check if already populated
        existing = db.get_all_ct_towns()
        if existing:
            return APIResponse(
                success=False,
                message=f"Towns table already populated with {len(existing)} towns. Use refresh endpoint to update."
            )

        # Scrape towns
        scraper = CTTownScraper()
        towns_data = scraper.scrape_towns_and_counties()

        if not towns_data:
            raise HTTPException(status_code=500, detail="Failed to scrape towns data")

        # Populate database
        inserted = db.populate_ct_towns(towns_data)

        return APIResponse(
            success=True,
            message=f"Successfully populated {inserted} Connecticut towns"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=APIResponse)
async def refresh_towns(
    db: DatabaseConnector = Depends(get_db)
):
    """
    Refresh Connecticut towns data (clear and repopulate)
    """
    try:
        # Clear existing data
        db.clear_ct_towns()

        # Scrape towns
        scraper = CTTownScraper()
        towns_data = scraper.scrape_towns_and_counties()

        if not towns_data:
            raise HTTPException(status_code=500, detail="Failed to scrape towns data")

        # Populate database
        inserted = db.populate_ct_towns(towns_data)

        return APIResponse(
            success=True,
            message=f"Successfully refreshed with {inserted} Connecticut towns"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))