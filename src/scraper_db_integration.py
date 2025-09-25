"""
Integration module for web scraper and database
Handles scraping cases and storing them in Supabase
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from typing import List, Dict, Optional
from case_scraper import CaseScraper
from db_connector import DatabaseConnector
from db_models import Case, Defendant
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperDatabaseIntegration:
    """Integrates web scraper with database operations"""

    def __init__(self):
        """Initialize database connection"""
        self.db = DatabaseConnector()

    def parse_address(self, address_str: str) -> Dict[str, str]:
        """Parse address string into components"""
        # Basic parsing - can be enhanced based on actual data format
        parts = address_str.split(',')
        result = {
            'address': address_str,
            'state': 'CT',  # Default to Connecticut
            'zip': None
        }

        if len(parts) >= 2:
            result['address'] = parts[0].strip()
            # Try to extract zip from last part
            city_zip = parts[-1].strip()
            zip_parts = city_zip.split()
            if zip_parts and zip_parts[-1].isdigit() and len(zip_parts[-1]) == 5:
                result['zip'] = zip_parts[-1]

        return result

    def scrape_and_store_cases(self, town: str) -> Dict[str, any]:
        """
        Scrape cases for a town and store them in the database

        Args:
            town: Name of the town to scrape

        Returns:
            Dictionary with statistics about the operation
        """
        stats = {
            'town': town,
            'cases_found': 0,
            'cases_stored': 0,
            'cases_skipped': 0,
            'defendants_stored': 0,
            'errors': []
        }

        # Initialize scraper
        logger.info(f"Starting scrape for town: {town}")
        scraper = CaseScraper(town)

        # Scrape cases
        try:
            cases = scraper.scrape_cases()
            stats['cases_found'] = len(cases)
            logger.info(f"Found {len(cases)} cases for {town}")
        except Exception as e:
            error_msg = f"Error scraping cases: {e}"
            logger.error(error_msg)
            stats['errors'].append(error_msg)
            return stats

        # Store each case in database
        for case_data in cases:
            try:
                docket_number = case_data['docket_number']

                # Check if case already exists
                existing_case = self.db.get_case_by_docket(docket_number)
                if existing_case:
                    logger.info(f"Case {docket_number} already exists, skipping")
                    stats['cases_skipped'] += 1
                    continue

                # Prepare case data (no search_date anymore)
                case_model = Case(
                    case_name=case_data['case_name'],
                    docket_number=docket_number,
                    docket_url=case_data.get('docket_url'),
                    town=town
                )

                # Insert case
                inserted_case = self.db.insert_case(case_model.to_dict())
                if not inserted_case:
                    error_msg = f"Failed to insert case {docket_number}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    continue

                stats['cases_stored'] += 1

                # Parse address and create defendant
                address_info = self.parse_address(case_data.get('address', ''))
                defendant_model = Defendant(
                    name=case_data.get('defendant', 'Unknown'),
                    docket_number=docket_number,
                    address=address_info['address'],
                    town=town,  # Use the town from the search
                    state=address_info['state'],
                    zip=address_info['zip']
                )

                # Insert defendant
                inserted_defendant = self.db.insert_defendant(defendant_model.to_dict())
                if inserted_defendant:
                    stats['defendants_stored'] += 1
                    logger.info(f"Stored case {docket_number} with defendant {defendant_model.name}")
                else:
                    error_msg = f"Failed to insert defendant for case {docket_number}"
                    logger.warning(error_msg)
                    stats['errors'].append(error_msg)

            except Exception as e:
                error_msg = f"Error processing case {case_data.get('docket_number', 'unknown')}: {e}"
                logger.error(error_msg)
                stats['errors'].append(error_msg)
                continue

        # Log summary
        logger.info(f"Scraping complete for {town}")
        logger.info(f"Cases found: {stats['cases_found']}")
        logger.info(f"Cases stored: {stats['cases_stored']}")
        logger.info(f"Cases skipped (duplicates): {stats['cases_skipped']}")
        logger.info(f"Defendants stored: {stats['defendants_stored']}")
        if stats['errors']:
            logger.warning(f"Errors encountered: {len(stats['errors'])}")

        return stats

    def get_town_statistics(self, town: str, include_sandbox: bool = False) -> Dict[str, any]:
        """Get statistics for cases in a specific town"""
        cases = self.db.get_cases_by_town(town)

        stats = {
            'town': town,
            'total_cases': len(cases),
            'total_defendants': 0,
            'cases_with_skiptraces': 0,
            'total_skiptraces': 0,
            'cases_with_sandbox_skiptraces': 0,
            'total_sandbox_skiptraces': 0
        }

        for case in cases:
            # Get defendants by docket number
            defendants = self.db.get_defendants_by_docket(case['docket_number'])
            stats['total_defendants'] += len(defendants)

            # Get production skip traces by docket number
            skiptraces = self.db.get_skiptraces_by_docket(case['docket_number'], is_sandbox=False)
            if skiptraces:
                stats['cases_with_skiptraces'] += 1
                stats['total_skiptraces'] += len(skiptraces)

            # Get sandbox skip traces if requested
            if include_sandbox:
                sandbox_skiptraces = self.db.get_skiptraces_by_docket(case['docket_number'], is_sandbox=True)
                if sandbox_skiptraces:
                    stats['cases_with_sandbox_skiptraces'] += 1
                    stats['total_sandbox_skiptraces'] += len(sandbox_skiptraces)

        return stats