"""
FastAPI main application
RESTful API for Connecticut Foreclosure Case and Skip Trace System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.v1.endpoints import cases, defendants, skiptraces, towns, scraper
from db_connector import DatabaseConnector

# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting FastAPI application...")
    # Test database connection
    db = DatabaseConnector()
    if db.test_connection():
        print("✓ Database connection successful")
    else:
        print("⚠ Database connection failed - some features may not work")
    yield
    # Shutdown
    print("Shutting down FastAPI application...")

# Create FastAPI instance
app = FastAPI(
    title="Skip Trace Database API",
    description="RESTful API for Connecticut Foreclosure Cases and Skip Trace System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(defendants.router, prefix="/api/v1/defendants", tags=["Defendants"])
app.include_router(skiptraces.router, prefix="/api/v1/skiptraces", tags=["Skip Traces"])
app.include_router(towns.router, prefix="/api/v1/towns", tags=["Towns"])
app.include_router(scraper.router, prefix="/api/v1/scraper", tags=["Scraper"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Skip Trace Database API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = DatabaseConnector()
    db_status = "healthy" if db.test_connection() else "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "services": {
            "api": "healthy",
            "database": db_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)