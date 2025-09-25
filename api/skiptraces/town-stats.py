import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db_connector import DatabaseConnector

def handler(request, response):
    """
    Vercel Function for getting town skip trace stats
    GET /api/skiptraces/town-stats?town=Middletown
    """
    # Enable CORS
    response.status_code = 200
    response.headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return response

    # Get town parameter
    town = request.args.get('town')
    if not town:
        response.status_code = 400
        return json.dumps({'error': 'Town parameter is required'})

    try:
        # Initialize database connection
        db = DatabaseConnector()

        # Get stats
        stats = db.get_town_skip_trace_stats(town)

        return json.dumps(stats)

    except Exception as e:
        response.status_code = 500
        return json.dumps({'error': str(e)})