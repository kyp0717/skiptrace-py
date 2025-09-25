#!/usr/bin/env python3
"""
Main application for CT Judiciary case scraper with database integration
"""

import sys
import json
import os

# Add the src directory to Python path to handle imports correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from case_scraper import CaseScraper
from batch_api_connector import BatchAPIConnector
from scraper_db_integration import ScraperDatabaseIntegration
from db_connector import DatabaseConnector
from skip_trace_integration import SkipTraceIntegration
from ct_town_scraper import CTTownScraper


def parse_address_to_dict(address_str):
    """Parse address string into structured format for API."""
    parts = address_str.split(',')
    if len(parts) >= 2:
        street = parts[0].strip()
        remainder = parts[1].strip()

        # Split city, state, zip
        words = remainder.split()
        if len(words) >= 2:
            zip_code = words[-1]
            state = words[-2]
            city = ' '.join(words[:-2]) if len(words) > 2 else words[0]

            return {
                'street': street,
                'city': city,
                'state': state,
                'zip': zip_code
            }
    return None


def main():
    """
    Main function to orchestrate the scraping and database storage process
    """
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <town_name> [--skip-trace] [--prod] [--db]")
        print("       --skip-trace: Enable batch API phone lookup")
        print("       --prod: Use production API instead of sandbox")
        print("       --db: Store results in Supabase database")
        sys.exit(1)

    town_name = sys.argv[1]
    enable_skip_trace = '--skip-trace' in sys.argv
    use_production = '--prod' in sys.argv
    use_database = '--db' in sys.argv

    print(f"\n{'='*60}")
    print(f"CT Judiciary Case Scraper")
    print(f"{'='*60}")
    print(f"\nSearching for cases in: {town_name}")
    if enable_skip_trace:
        api_mode = "PRODUCTION" if use_production else "SANDBOX"
        print(f"Skip trace (phone lookup) enabled: YES ({api_mode})")
    if use_database:
        print(f"Database storage enabled: YES (Supabase)")
    print(f"{'-'*40}")

    try:
        # Check if using database integration
        if use_database:
            print(f"\n{'='*60}")
            print(f"Database Integration Mode")
            print(f"{'='*60}")

            # Initialize database integration
            integration = ScraperDatabaseIntegration()

            # Test database connection
            db = DatabaseConnector()
            if not db.test_connection():
                print("ERROR: Could not connect to database")
                print("Please check your Supabase credentials in .env file")
                sys.exit(1)

            print("✓ Database connection successful")

            # Check and populate CT towns if needed
            print("\nChecking Connecticut towns database...")
            ct_towns = db.get_all_ct_towns()
            if not ct_towns:
                print("⚠ CT towns table is empty. Populating...")
                town_scraper = CTTownScraper()
                towns_data = town_scraper.scrape_towns_and_counties()
                if towns_data:
                    inserted = db.populate_ct_towns(towns_data)
                    print(f"✓ Populated database with {inserted} Connecticut towns")
                else:
                    print("WARNING: Could not populate CT towns data")
            else:
                print(f"✓ CT towns database contains {len(ct_towns)} towns")

            # Validate the input town
            town_scraper = CTTownScraper()
            town_scraper.towns_data = [(t['town'], t['county']) for t in ct_towns]
            if not town_scraper.validate_town(town_name):
                print(f"\n⚠ Warning: '{town_name}' may not be a valid Connecticut town")
                county = town_scraper.get_county_for_town(town_name)
                if not county:
                    print("Consider using one of these valid town names:")
                    # Show some sample towns
                    sample_towns = sorted(list(set([t['town'] for t in ct_towns[:10]])))
                    print(f"  {', '.join(sample_towns[:5])}, ...")
            else:
                county = town_scraper.get_county_for_town(town_name)
                print(f"✓ Valid town: {town_name}, {county} County")

            # Scrape and store cases
            print(f"\nScraping cases for {town_name} and storing in database...")
            stats = integration.scrape_and_store_cases(town_name)

            # Display results
            print(f"\n{'-'*40}")
            print("Scraping Results:")
            print(f"{'-'*40}")
            print(f"Town: {stats['town']}")
            print(f"Cases found: {stats['cases_found']}")
            print(f"Cases stored: {stats['cases_stored']}")
            print(f"Cases skipped (duplicates): {stats['cases_skipped']}")
            print(f"Defendants stored: {stats['defendants_stored']}")

            if stats['errors']:
                print(f"\nErrors encountered ({len(stats['errors'])}):")
                for error in stats['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")

            # Get and display town statistics
            print(f"\n{'-'*40}")
            print("Database Statistics for", town_name)
            print(f"{'-'*40}")

            town_stats = integration.get_town_statistics(town_name, include_sandbox=True)
            print(f"Total cases in database: {town_stats['total_cases']}")
            print(f"Total defendants: {town_stats['total_defendants']}")
            print(f"Cases with skip traces (production): {town_stats['cases_with_skiptraces']}")
            print(f"Total skip traces (production): {town_stats['total_skiptraces']}")
            print(f"Cases with skip traces (sandbox): {town_stats['cases_with_sandbox_skiptraces']}")
            print(f"Total skip traces (sandbox): {town_stats['total_sandbox_skiptraces']}")

            # Get recent cases from database to display
            recent_cases = db.get_cases_by_town(town_name)[:5]
            if recent_cases:
                print(f"\n{'-'*40}")
                print("Sample Cases from Database (First 5):")
                print(f"{'-'*40}")

                for i, case in enumerate(recent_cases, 1):
                    print(f"\nCase {i}:")
                    print(f"  Case Name: {case['case_name']}")
                    print(f"  Docket #: {case['docket_number']}")
                    print(f"  Town: {case['town']}")
                    print(f"  Stored: {case['created_at']}")

                    # Get defendants for this case using docket_number
                    defendants = db.get_defendants_by_docket(case['docket_number'])
                    if defendants:
                        print(f"  Defendants:")
                        for defendant in defendants:
                            print(f"    - {defendant['name']}")
                            if defendant.get('address'):
                                print(f"      Address: {defendant['address']}")

            # Process skip traces if enabled
            if enable_skip_trace:
                print(f"\n{'='*60}")
                print(f"Skip Trace Processing ({'SANDBOX' if not use_production else 'PRODUCTION'})")
                print(f"{'='*60}")

                # Initialize skip trace integration
                skip_trace = SkipTraceIntegration(use_sandbox=not use_production)

                # Process skip traces for first 2 cases (as per requirements)
                print(f"\nProcessing skip traces for first 2 cases in {town_name}...")
                skip_stats = skip_trace.process_town_skip_traces(town_name, limit=2)

                print(f"\n{'-'*40}")
                print("Skip Trace Results:")
                print(f"{'-'*40}")
                print(f"Cases processed: {skip_stats['cases_processed']}")
                print(f"Phone numbers found: {skip_stats['total_phone_numbers']}")
                print(f"Records stored in {skip_trace.table_name}: {skip_stats['total_records_stored']}")

                # Display sample skip trace data
                if skip_stats['cases_processed'] > 0:
                    cases_with_skiptraces = db.get_cases_by_town(town_name)[:2]
                    for case in cases_with_skiptraces:
                        full_case = db.get_full_case_data(case['docket_number'], include_sandbox=True)
                        skiptraces = full_case.get('skiptraces_sandbox' if not use_production else 'skiptraces', [])
                        if skiptraces:
                            print(f"\nCase: {case['case_name']}")
                            print(f"Docket: {case['docket_number']}")
                            print(f"Phone numbers found:")
                            for st in skiptraces[:5]:  # Show first 5
                                print(f"  • {st['phone_number']} ({st.get('phone_type', 'unknown')})")

            print(f"\n{'='*60}")
            print("✓ Database storage complete!")
            print(f"{'='*60}\n")

        else:
            # Original file-based functionality
            # Phase 4 Integration: Case Scraping
            # Initialize the case scraper
            scraper = CaseScraper(town_name)

            # Scrape cases for the specified town
            cases = scraper.scrape_cases()

            if not cases:
                print(f"No cases found for {town_name}")
                return

            print(f"\nFound {len(cases)} cases")

            # Display first 5 cases as examples
            print(f"\n{'-'*40}")
            print("Sample Results (First 5 cases):")
            print(f"{'-'*40}")

            for i, case in enumerate(cases[:5], 1):
                print(f"\nCase {i}:")
                print(f"  Case Name: {case['case_name']}")
                print(f"  Defendant: {case['defendant']}")
                print(f"  Address: {case['address']}")
                print(f"  Docket #: {case['docket_number']}")
                print(f"  Docket URL: {case['docket_url']}")

            # Phase 5/6 Integration: Batch API Phone Lookup
            if enable_skip_trace:
                phase_num = "6" if use_production else "5"
                api_env = "prod" if use_production else "sandbox"
                api_label = "Production" if use_production else "Sandbox"

                print(f"\n{'='*60}")
                print(f"Phase {phase_num}: Batch API Phone Lookup ({api_label})")
                print(f"{'='*60}")

                # Initialize the batch API connector
                api_connector = BatchAPIConnector(api_env)

                # Process first 2 cases for phone lookup (as per requirements)
                cases_to_process = cases[:2]
                print(f"\nProcessing {len(cases_to_process)} addresses for phone lookup...")

                for i, case in enumerate(cases_to_process, 1):
                    print(f"\n{'-'*40}")
                    print(f"Processing Case {i}:")
                    print(f"  Defendant: {case['defendant']}")
                    print(f"  Address: {case['address']}")

                    # Parse address into structured format
                    address_dict = parse_address_to_dict(case['address'])

                    if address_dict:
                        # Send skip trace request
                        phone_numbers = api_connector.send_skip_trace_request(address_dict)

                        # Add phone numbers to case data
                        case['phone_numbers'] = phone_numbers

                        if phone_numbers:
                            print(f"  Phone Numbers Found: {', '.join(phone_numbers)}")
                        else:
                            print("  No phone numbers found")
                    else:
                        print("  Could not parse address")
                        case['phone_numbers'] = []

            # Save results to both JSON and CSV files
            json_filename = f"cases_{town_name.lower().replace(' ', '_')}.json"
            with open(json_filename, 'w') as f:
                json.dump(cases, f, indent=2)

            # Save to CSV using the scraper's save_to_csv method
            csv_filename = scraper.save_to_csv(cases)

            print(f"\n{'-'*40}")
            print(f"Results saved to:")
            print(f"  JSON: {json_filename}")
            print(f"  CSV: {csv_filename}")
            print(f"Total cases found: {len(cases)}")
            if enable_skip_trace:
                enriched_count = sum(1 for c in cases if c.get('phone_numbers'))
                print(f"Cases with phone numbers: {enriched_count}")
            print(f"{'='*60}\n")

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()