#!/usr/bin/env python3
"""
Run the FastAPI application
"""

import uvicorn
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting Skip Trace Database API")
    print("="*60)
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("📊 Alternative Docs: http://localhost:8000/redoc")
    print("🏥 Health Check: http://localhost:8000/health")
    print("\nPress CTRL+C to stop the server\n")

    # Run the FastAPI app
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )