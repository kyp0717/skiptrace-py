"""
Integration module for BatchData API skip trace with database storage
Handles phone lookup and storage in Supabase
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict, Optional
from batch_api_connector import BatchAPIConnector
from db_connector import DatabaseConnector
from db_models import SkipTrace
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkipTraceIntegration:
    """Integrates BatchData API with database operations"""

    def __init__(self, use_sandbox: bool = True):
        """Initialize with database connection and API connector

        Args:
            use_sandbox: If True, use sandbox API and skiptrace_sandbox table
        """
        self.db = DatabaseConnector()
        self.use_sandbox = use_sandbox
        env = 'sandbox' if use_sandbox else 'prod'
        self.api = BatchAPIConnector(env)
        self.table_name = 'skiptrace_sandbox' if use_sandbox else 'skiptrace'

        logger.info(f"SkipTrace integration initialized (sandbox={use_sandbox})")

    def parse_address(self, address_str: str, town: str = None) -> Dict[str, str]:
        """Parse address string into components for API"""
        parts = address_str.split(',')
        result = {
            'street': address_str,
            'city': town if town else '',
            'state': 'CT',
            'zip': ''
        }

        if len(parts) >= 2:
            result['street'] = parts[0].strip()
            # Try to extract city, state, zip from remaining parts
            remainder = ','.join(parts[1:]).strip()
            words = remainder.split()

            if words:
                # Last word might be zip
                if words[-1].replace('-', '').isdigit():
                    result['zip'] = words[-1]
                    words = words[:-1]

                # Second to last might be state
                if words and len(words[-1]) == 2:
                    result['state'] = words[-1]
                    words = words[:-1]

                # Remaining is city
                if words:
                    result['city'] = ' '.join(words)

        return result

    def process_case_skip_trace(self, docket_number: str, force: bool = False) -> Dict[str, any]:
        """Process skip trace for a single case

        Args:
            docket_number: The docket number to process
            force: If True, skip trace even if already done (default: False)

        Returns:
            Statistics about the processing
        """
        stats = {
            'docket_number': docket_number,
            'defendants_processed': 0,
            'addresses_processed': 0,
            'phone_numbers_found': 0,
            'records_stored': 0,
            'skipped': False,
            'errors': []
        }

        # Check if already skip traced (unless force flag is set)
        if not force and self.db.has_been_skip_traced(docket_number, is_sandbox=self.use_sandbox):
            logger.info(f"Case {docket_number} has already been skip traced in {self.table_name}")
            stats['skipped'] = True
            stats['errors'].append(f"Case already skip traced. Use force=True to override.")
            return stats

        # Get case and defendants
        case = self.db.get_case_by_docket(docket_number)
        if not case:
            error_msg = f"Case {docket_number} not found"
            logger.error(error_msg)
            stats['errors'].append(error_msg)
            return stats

        defendants = self.db.get_defendants_by_docket(docket_number)
        if not defendants:
            logger.info(f"No defendants found for case {docket_number}")
            return stats

        stats['defendants_processed'] = len(defendants)

        # Process each defendant's address
        all_skiptraces = []

        for defendant in defendants:
            address = defendant.get('address')
            if not address:
                logger.info(f"No address for defendant {defendant['name']}")
                continue

            stats['addresses_processed'] += 1

            # Parse address and call API, include town from defendant or case
            town = defendant.get('town') or case.get('town')
            address_dict = self.parse_address(address, town=town)
            logger.info(f"Processing address for {defendant['name']}: {address}")

            try:
                # Call BatchData API
                phone_numbers = self.api.send_skip_trace_request(address_dict)

                if phone_numbers:
                    stats['phone_numbers_found'] += len(phone_numbers)

                    # Create skip trace records
                    for phone in phone_numbers:
                        # Determine phone type based on pattern (simplified)
                        phone_type = 'mobile' if any(x in phone for x in ['555-01', '860-']) else 'landline'

                        skiptrace_data = {
                            'docket_number': docket_number,
                            'phone_number': phone,
                            'phone_type': phone_type
                        }
                        all_skiptraces.append(skiptrace_data)

                    logger.info(f"Found {len(phone_numbers)} phone numbers for {defendant['name']}")
                else:
                    logger.info(f"No phone numbers found for {defendant['name']}")

            except Exception as e:
                error_msg = f"Error processing {defendant['name']}: {e}"
                logger.error(error_msg)
                stats['errors'].append(error_msg)

        # Store all skip trace records
        if all_skiptraces:
            stored = self.db.insert_skiptraces(all_skiptraces, is_sandbox=self.use_sandbox)
            stats['records_stored'] = len(stored) if stored else 0
            logger.info(f"Stored {stats['records_stored']} skip trace records in {self.table_name}")

        return stats

    def process_town_skip_traces(self, town: str, limit: Optional[int] = None, force: bool = False) -> Dict[str, any]:
        """Process skip traces for all cases in a town

        Args:
            town: Town name to process
            limit: Optional limit on number of cases to process
            force: If True, skip trace even if already done (default: False)

        Returns:
            Statistics about the processing
        """
        stats = {
            'town': town,
            'cases_processed': 0,
            'cases_skipped': 0,
            'total_defendants': 0,
            'total_addresses': 0,
            'total_phone_numbers': 0,
            'total_records_stored': 0,
            'errors': []
        }

        # Get all cases for the town
        cases = self.db.get_cases_by_town(town)
        if not cases:
            logger.info(f"No cases found for town {town}")
            return stats

        # Apply limit if specified
        if limit:
            cases = cases[:limit]

        logger.info(f"Processing skip traces for {len(cases)} cases in {town}")

        # Process each case
        for case in cases:
            docket_number = case['docket_number']
            logger.info(f"\nProcessing case {docket_number}: {case['case_name']}")

            case_stats = self.process_case_skip_trace(docket_number, force=force)

            if case_stats['skipped']:
                stats['cases_skipped'] += 1
            else:
                stats['cases_processed'] += 1
                stats['total_defendants'] += case_stats['defendants_processed']
                stats['total_addresses'] += case_stats['addresses_processed']
                stats['total_phone_numbers'] += case_stats['phone_numbers_found']
                stats['total_records_stored'] += case_stats['records_stored']

            stats['errors'].extend(case_stats['errors'])

        # Log summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Skip Trace Processing Complete for {town}")
        logger.info(f"{'='*60}")
        logger.info(f"Environment: {'SANDBOX' if self.use_sandbox else 'PRODUCTION'}")
        logger.info(f"Table: {self.table_name}")
        logger.info(f"Cases processed: {stats['cases_processed']}")
        logger.info(f"Cases skipped (already traced): {stats['cases_skipped']}")
        logger.info(f"Defendants processed: {stats['total_defendants']}")
        logger.info(f"Addresses processed: {stats['total_addresses']}")
        logger.info(f"Phone numbers found: {stats['total_phone_numbers']}")
        logger.info(f"Records stored: {stats['total_records_stored']}")

        if stats['errors']:
            logger.warning(f"Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:5]:
                logger.warning(f"  - {error}")

        return stats

    def get_skip_trace_report(self, docket_number: str) -> Dict[str, any]:
        """Get a report of skip trace data for a case"""
        case = self.db.get_full_case_data(docket_number, include_sandbox=True)

        if not case:
            return None

        report = {
            'case_name': case['case_name'],
            'docket_number': docket_number,
            'defendants': []
        }

        # Organize by defendant
        for defendant in case.get('defendants', []):
            def_data = {
                'name': defendant['name'],
                'address': defendant.get('address'),
                'production_phones': [],
                'sandbox_phones': []
            }

            # Get production phones (all belong to this case via docket_number)
            for skiptrace in case.get('skiptraces', []):
                def_data['production_phones'].append({
                    'number': skiptrace['phone_number'],
                    'type': skiptrace.get('phone_type')
                })

            # Get sandbox phones (all belong to this case via docket_number)
            for skiptrace in case.get('skiptraces_sandbox', []):
                def_data['sandbox_phones'].append({
                    'number': skiptrace['phone_number'],
                    'type': skiptrace.get('phone_type')
                })

            report['defendants'].append(def_data)

        return report