#!/usr/bin/env python3
"""
Run skip trace for a single specific case
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skip_trace_integration import SkipTraceIntegration
from db_connector import DatabaseConnector
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run skip trace for a single case')
    parser.add_argument('docket_number', help='Docket number to process')
    parser.add_argument('--prod', action='store_true', help='Use production API (default: sandbox)')
    parser.add_argument('--force', action='store_true', help='Force skip trace even if already done')

    args = parser.parse_args()

    # Initialize database connection
    db = DatabaseConnector()

    # Test connection
    if not db.test_connection():
        print("ERROR: Could not connect to database")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Skip Trace for Single Case")
    print(f"{'='*60}")
    print(f"Docket Number: {args.docket_number}")
    print(f"Mode: {'PRODUCTION' if args.prod else 'SANDBOX'}")
    print(f"{'='*60}\n")

    # Get case details
    case = db.get_full_case_data(args.docket_number, include_sandbox=True)
    if not case:
        print(f"ERROR: Case {args.docket_number} not found in database")
        sys.exit(1)

    print(f"Case Name: {case['case_name']}")
    print(f"Town: {case.get('town', 'N/A')}")
    print(f"Defendants: {len(case.get('defendants', []))}")

    for defendant in case.get('defendants', []):
        print(f"  - {defendant['name']}")
        if defendant.get('address'):
            print(f"    Address: {defendant['address']}")

    # Check existing skip traces
    existing_prod = len(case.get('skiptraces', []))
    existing_sandbox = len(case.get('skiptraces_sandbox', []))

    print(f"\nExisting Skip Traces:")
    print(f"  Production: {existing_prod}")
    print(f"  Sandbox: {existing_sandbox}")

    # Initialize skip trace integration
    skip_trace = SkipTraceIntegration(use_sandbox=not args.prod)

    print(f"\n{'-'*40}")
    print(f"Processing Skip Trace...")
    print(f"{'-'*40}\n")

    # Process the case
    stats = skip_trace.process_case_skip_trace(args.docket_number, force=args.force)

    # Display results
    print(f"\n{'='*60}")
    print(f"Skip Trace Results")
    print(f"{'='*60}")

    if stats.get('skipped'):
        print(f"STATUS: SKIPPED - Case already skip traced")
        if not args.force:
            print("Use --force flag to override and re-process")
    else:
        print(f"Defendants processed: {stats['defendants_processed']}")
        print(f"Addresses processed: {stats['addresses_processed']}")
        print(f"Phone numbers found: {stats['phone_numbers_found']}")
        print(f"Records stored: {stats['records_stored']}")

        # Show cost information
        cost = stats.get('cost', 0.0)
        if not args.prod:
            print(f"Cost: $0.00 (sandbox - no charge)")
        else:
            print(f"Cost: ${cost:.2f} ({stats['addresses_processed']} lookups @ $0.07 each)")

    if stats['errors']:
        print(f"\nErrors encountered:")
        for error in stats['errors']:
            print(f"  - {error}")

    # Get updated case data to show new skip traces
    updated_case = db.get_full_case_data(args.docket_number, include_sandbox=True)

    if args.prod:
        new_skiptraces = updated_case.get('skiptraces', [])
        table_name = 'skiptrace'
    else:
        new_skiptraces = updated_case.get('skiptraces_sandbox', [])
        table_name = 'skiptrace_sandbox'

    # Show only the newly added skip traces
    new_count = len(new_skiptraces) - (existing_prod if args.prod else existing_sandbox)

    if new_count > 0:
        print(f"\n{'-'*40}")
        print(f"New Phone Numbers Added to {table_name}:")
        print(f"{'-'*40}")

        # Show the last 'new_count' records (the newly added ones)
        for st in new_skiptraces[-new_count:]:
            print(f"\nPhone Number Added:")
            print(f"  Number: {st['phone_number']}")
            print(f"  Type: {st.get('phone_type', 'unknown')}")

    print(f"\n{'='*60}")
    print(f"✓ Skip trace complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()