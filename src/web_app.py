#!/usr/bin/env python3
"""
Flask Web Application for Foreclosure Skip Trace System
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from datetime import datetime
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connector import DatabaseConnector
from scraper_db_integration import ScraperDatabaseIntegration
from skip_trace_integration import SkipTraceIntegration
from case_scraper import CaseScraper

# Initialize Flask app
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Initialize database connection
db = DatabaseConnector()
scraper_integration = ScraperDatabaseIntegration()

# Routes

@app.route('/')
def index():
    """Home page - Dashboard"""
    try:
        # Get summary statistics
        stats = {
            'total_cases': 0,
            'total_defendants': 0,
            'total_skiptraces': 0,
            'towns': []
        }

        # Get all towns
        towns_query = db.client.table('cases').select('town').execute()
        unique_towns = set(row['town'] for row in towns_query.data if row['town'])
        stats['towns'] = sorted(list(unique_towns))

        # Get total counts
        cases_count = db.client.table('cases').select('id', count='exact').execute()
        stats['total_cases'] = cases_count.count if cases_count else 0

        defendants_count = db.client.table('defendants').select('id', count='exact').execute()
        stats['total_defendants'] = defendants_count.count if defendants_count else 0

        skiptraces_count = db.client.table('skiptrace').select('id', count='exact').execute()
        stats['total_skiptraces'] = skiptraces_count.count if skiptraces_count else 0

        # Get recent cases
        recent_cases = db.get_recent_cases(limit=5)

        return render_template('index.html', stats=stats, recent_cases=recent_cases)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/cases')
def cases():
    """Display all cases with filtering"""
    town = request.args.get('town', '')

    if town:
        cases = db.get_cases_by_town(town)
    else:
        response = db.client.table('cases').select('*').order('created_at', desc=True).execute()
        cases = response.data if response.data else []

    # Get skip trace status for each case
    for case in cases:
        case['has_skiptrace'] = db.has_been_skip_traced(case['docket_number'])
        defendants = db.get_defendants_by_docket(case['docket_number'])
        case['defendant_count'] = len(defendants)
        skiptraces = db.get_skiptraces_by_docket(case['docket_number'])
        case['phone_count'] = len(skiptraces)

    return render_template('cases.html', cases=cases, selected_town=town)

@app.route('/case/<docket_number>')
def case_detail(docket_number):
    """Display detailed case information"""
    case = db.get_full_case_data(docket_number, include_sandbox=True)

    if not case:
        flash(f'Case {docket_number} not found', 'error')
        return redirect(url_for('cases'))

    return render_template('case_detail.html', case=case)

@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    """Scrape cases from Connecticut Judiciary website"""
    if request.method == 'POST':
        town = request.form.get('town')
        if not town:
            flash('Please enter a town name', 'error')
            return redirect(url_for('scrape'))

        try:
            # Run the scraper
            stats = scraper_integration.scrape_and_store_cases(town)

            flash(f'Successfully scraped {stats["cases_stored"]} new cases from {town}', 'success')
            if stats['cases_skipped'] > 0:
                flash(f'Skipped {stats["cases_skipped"]} duplicate cases', 'info')
            if stats['errors']:
                for error in stats['errors'][:3]:
                    flash(f'Error: {error}', 'warning')

            return redirect(url_for('cases', town=town))
        except Exception as e:
            flash(f'Error scraping cases: {str(e)}', 'error')
            return redirect(url_for('scrape'))

    return render_template('scrape.html')

@app.route('/skip-trace/<docket_number>', methods=['POST'])
def skip_trace(docket_number):
    """Run skip trace for a specific case"""
    try:
        # Check if production or sandbox
        use_production = request.form.get('production') == 'true'
        force = request.form.get('force') == 'true'

        # Initialize skip trace
        skip_trace_int = SkipTraceIntegration(use_sandbox=not use_production)

        # Process the case
        stats = skip_trace_int.process_case_skip_trace(docket_number, force=force)

        if stats['skipped'] and not force:
            return jsonify({
                'success': False,
                'message': 'Case already skip traced. Use force option to re-process.',
                'stats': stats
            })

        return jsonify({
            'success': True,
            'message': f'Found {stats["phone_numbers_found"]} phone numbers',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/stats/<town>')
def api_town_stats(town):
    """Get statistics for a specific town"""
    try:
        stats = scraper_integration.get_town_statistics(town, include_sandbox=True)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cases')
def api_cases():
    """API endpoint for cases data"""
    town = request.args.get('town', '')
    limit = request.args.get('limit', 100, type=int)

    if town:
        cases = db.get_cases_by_town(town)[:limit]
    else:
        response = db.client.table('cases').select('*').order('created_at', desc=True).limit(limit).execute()
        cases = response.data if response.data else []

    return jsonify(cases)

@app.route('/api/case/<docket_number>')
def api_case_detail(docket_number):
    """API endpoint for detailed case data"""
    case = db.get_full_case_data(docket_number, include_sandbox=True)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    return jsonify(case)

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        if db.test_connection():
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 503

if __name__ == '__main__':
    # Check database connection on startup
    if not db.test_connection():
        print("ERROR: Cannot connect to database. Please check your .env file.")
        sys.exit(1)

    print("Starting Foreclosure Skip Trace Web Application...")
    print("Access the application at: http://localhost:5000")

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)