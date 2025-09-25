"""
Scraper API endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from api.v1.schemas.common import APIResponse
from api.dependencies import get_db
from db_connector import DatabaseConnector
from scraper_db_integration import ScraperDatabaseIntegration
from ct_town_scraper import CTTownScraper
import uuid

router = APIRouter()


class ScrapeRequest(BaseModel):
    """Request to scrape a town"""
    town: str = Field(..., description="Town to scrape")
    store_in_db: bool = Field(True, description="Store results in database")


class ScrapeJobStatus(BaseModel):
    """Scrape job status"""
    job_id: str
    status: str
    town: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    cases_found: Optional[int] = None
    error: Optional[str] = None


# In-memory job storage (in production, use Redis or database)
scrape_jobs = {}


def run_scrape_task(job_id: str, town: str, store_in_db: bool):
    """Background task to run scraping"""
    try:
        scrape_jobs[job_id]['status'] = 'running'

        if store_in_db:
            # Use database integration
            integration = ScraperDatabaseIntegration()
            stats = integration.scrape_and_store_cases(town)

            scrape_jobs[job_id]['status'] = 'completed'
            scrape_jobs[job_id]['completed_at'] = datetime.now()
            scrape_jobs[job_id]['cases_found'] = stats['cases_found']
        else:
            # Just scrape without storing
            from case_scraper import CaseScraper
            scraper = CaseScraper()
            cases = scraper.scrape_cases(town)

            scrape_jobs[job_id]['status'] = 'completed'
            scrape_jobs[job_id]['completed_at'] = datetime.now()
            scrape_jobs[job_id]['cases_found'] = len(cases)

    except Exception as e:
        scrape_jobs[job_id]['status'] = 'failed'
        scrape_jobs[job_id]['completed_at'] = datetime.now()
        scrape_jobs[job_id]['error'] = str(e)


@router.post("/scrape", response_model=ScrapeJobStatus)
async def start_scraping(
    scrape_request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Start a scraping job for a town
    """
    try:
        # Validate town
        ct_towns = db.get_all_ct_towns()
        scraper = CTTownScraper()
        scraper.towns_data = [(t['town'], t['county']) for t in ct_towns]

        if not scraper.validate_town(scrape_request.town):
            raise HTTPException(status_code=400, detail=f"'{scrape_request.town}' is not a valid Connecticut town")

        # Create job
        job_id = str(uuid.uuid4())
        job = {
            'job_id': job_id,
            'status': 'pending',
            'town': scrape_request.town,
            'started_at': datetime.now(),
            'completed_at': None,
            'cases_found': None,
            'error': None
        }
        scrape_jobs[job_id] = job

        # Start background task
        background_tasks.add_task(
            run_scrape_task,
            job_id,
            scrape_request.town,
            scrape_request.store_in_db
        )

        return ScrapeJobStatus(**job)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=ScrapeJobStatus)
async def get_scrape_status(job_id: str):
    """
    Get the status of a scraping job
    """
    if job_id not in scrape_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return ScrapeJobStatus(**scrape_jobs[job_id])


@router.get("/history")
async def get_scrape_history(
    limit: int = 10,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Get recent scraping history
    """
    try:
        # Get recent scrape jobs from memory (last N jobs)
        recent_jobs = sorted(
            scrape_jobs.values(),
            key=lambda x: x['started_at'],
            reverse=True
        )[:limit]

        # Also get some stats from database
        response = db.client.table('cases').select("town, created_at").order(
            'created_at', desc=True
        ).limit(100).execute()

        # Group by town
        town_stats = {}
        if response.data:
            for case in response.data:
                town = case.get('town', 'Unknown')
                if town not in town_stats:
                    town_stats[town] = 0
                town_stats[town] += 1

        return {
            "recent_jobs": recent_jobs,
            "town_statistics": town_stats,
            "total_jobs_tracked": len(scrape_jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape-town")
async def scrape_single_town(
    request: ScrapeRequest,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Synchronously scrape a single town and store in database
    """
    try:
        # Validate town
        ct_towns = db.get_all_ct_towns()
        scraper = CTTownScraper()
        scraper.towns_data = [(t['town'], t['county']) for t in ct_towns]

        if not scraper.validate_town(request.town):
            raise HTTPException(status_code=400, detail=f"'{request.town}' is not a valid Connecticut town")

        # Run scraping synchronously
        integration = ScraperDatabaseIntegration()
        stats = integration.scrape_and_store_cases(request.town)

        return {
            "message": f"Successfully scraped {request.town}",
            "cases_found": stats['cases_found'],
            "new_cases": stats['cases_stored'],
            "existing_cases": stats['cases_skipped']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape-all-towns", response_model=APIResponse)
async def scrape_all_towns(
    background_tasks: BackgroundTasks,
    counties: Optional[list] = None,
    db: DatabaseConnector = Depends(get_db)
):
    """
    Start scraping all Connecticut towns (or specific counties)
    WARNING: This will take a long time and create many jobs
    """
    try:
        # Get all towns
        all_towns = db.get_all_ct_towns()

        # Filter by counties if specified
        if counties:
            all_towns = [t for t in all_towns if t['county'] in counties]

        if not all_towns:
            raise HTTPException(status_code=400, detail="No towns found for specified counties")

        # Create jobs for each town
        job_ids = []
        for town_data in all_towns:
            job_id = str(uuid.uuid4())
            job = {
                'job_id': job_id,
                'status': 'pending',
                'town': town_data['town'],
                'started_at': datetime.now(),
                'completed_at': None,
                'cases_found': None,
                'error': None
            }
            scrape_jobs[job_id] = job
            job_ids.append(job_id)

            # Add background task
            background_tasks.add_task(
                run_scrape_task,
                job_id,
                town_data['town'],
                True  # Store in database
            )

        return APIResponse(
            success=True,
            message=f"Started scraping {len(job_ids)} towns",
            data={"job_ids": job_ids, "town_count": len(job_ids)}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))