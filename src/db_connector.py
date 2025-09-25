"""
Database connector for Supabase
Handles all database operations for the foreclosure scraper
"""

import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Manages Supabase database connections and operations"""

    def __init__(self):
        """Initialize Supabase client"""
        load_dotenv()

        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_ANON_KEY")

        if not self.url or not self.key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment variables")

        self.client: Client = create_client(self.url, self.key)
        logger.info("Database connection initialized")

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            response = self.client.table('cases').select("*").limit(1).execute()
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    # Case operations
    def insert_case(self, case_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert a new case"""
        try:
            response = self.client.table('cases').insert(case_data).execute()
            logger.info(f"Case inserted: {case_data.get('docket_number')}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error inserting case: {e}")
            return None

    def get_case_by_docket(self, docket_number: str) -> Optional[Dict]:
        """Get case by docket number"""
        try:
            response = self.client.table('cases').select("*").eq('docket_number', docket_number).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching case: {e}")
            return None

    def get_cases_by_town(self, town: str) -> List[Dict]:
        """Get all cases for a specific town"""
        try:
            response = self.client.table('cases').select("*").eq('town', town).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching cases by town: {e}")
            return []

    # Defendant operations
    def insert_defendant(self, defendant_data: Dict[str, Any]) -> Optional[Dict]:
        """Insert a new defendant"""
        try:
            response = self.client.table('defendants').insert(defendant_data).execute()
            logger.info(f"Defendant inserted: {defendant_data.get('name')} for docket {defendant_data.get('docket_number')}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error inserting defendant: {e}")
            return None

    def get_defendants_by_docket(self, docket_number: str) -> List[Dict]:
        """Get all defendants for a case by docket number"""
        try:
            response = self.client.table('defendants').select("*").eq('docket_number', docket_number).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching defendants: {e}")
            return []

    def get_defendant_by_docket_and_name(self, docket_number: str, name: str) -> Optional[Dict]:
        """Get a specific defendant by docket number and name"""
        try:
            response = self.client.table('defendants').select("*").eq('docket_number', docket_number).eq('name', name).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching defendant: {e}")
            return None

    # CT Towns operations
    def insert_ct_town(self, town: str, county: str) -> Optional[Dict]:
        """Insert a Connecticut town and county"""
        try:
            town_data = {'town': town, 'county': county}
            response = self.client.table('ct_towns').insert(town_data).execute()
            logger.info(f"CT town inserted: {town}, {county} County")
            return response.data[0] if response.data else None
        except Exception as e:
            if 'duplicate key' in str(e).lower():
                logger.debug(f"Town already exists: {town}")
            else:
                logger.error(f"Error inserting CT town: {e}")
            return None

    def get_all_ct_towns(self) -> List[Dict]:
        """Get all Connecticut towns and counties"""
        try:
            response = self.client.table('ct_towns').select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching CT towns: {e}")
            return []

    def get_ct_town(self, town: str) -> Optional[Dict]:
        """Get a specific Connecticut town"""
        try:
            response = self.client.table('ct_towns').select("*").eq('town', town).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching CT town: {e}")
            return None

    def get_towns_by_county(self, county: str) -> List[Dict]:
        """Get all towns in a specific county"""
        try:
            response = self.client.table('ct_towns').select("*").eq('county', county).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching towns by county: {e}")
            return []

    def clear_ct_towns(self) -> bool:
        """Clear all entries from ct_towns table (use with caution)"""
        try:
            response = self.client.table('ct_towns').delete().neq('town', '').execute()
            logger.info("CT towns table cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing CT towns: {e}")
            return False

    def populate_ct_towns(self, towns_data: List[tuple]) -> int:
        """Bulk insert Connecticut towns and counties"""
        inserted_count = 0
        for town, county in towns_data:
            result = self.insert_ct_town(town, county)
            if result:
                inserted_count += 1
        logger.info(f"Inserted {inserted_count} towns into database")
        return inserted_count

    # Skip trace operations
    def insert_skiptraces(self, skiptrace_data: List[Dict[str, Any]], is_sandbox: bool = False) -> List[Dict]:
        """Insert multiple skip trace records to appropriate table"""
        table_name = 'skiptrace_sandbox' if is_sandbox else 'skiptrace'
        try:
            response = self.client.table(table_name).insert(skiptrace_data).execute()
            logger.info(f"Inserted {len(skiptrace_data)} skip trace records to {table_name}")
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error inserting skip trace records to {table_name}: {e}")
            return []

    def get_skiptraces_by_docket(self, docket_number: str, is_sandbox: bool = False) -> List[Dict]:
        """Get all skip trace records for a case by docket number from appropriate table"""
        table_name = 'skiptrace_sandbox' if is_sandbox else 'skiptrace'
        try:
            response = self.client.table(table_name).select("*").eq('docket_number', docket_number).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching skip trace records from {table_name}: {e}")
            return []

    # Batch operations
    def insert_case_with_defendants(self, case_data: Dict, defendants: List[Dict]) -> Optional[Dict]:
        """Insert a case with multiple defendants in a transaction-like manner"""
        try:
            # Insert case first
            case = self.insert_case(case_data)
            if not case:
                return None

            # Insert defendants with docket_number
            docket_number = case['docket_number']
            for defendant in defendants:
                defendant['docket_number'] = docket_number
                self.insert_defendant(defendant)

            return case
        except Exception as e:
            logger.error(f"Error in batch insert: {e}")
            return None

    def get_full_case_data(self, docket_number: str, include_sandbox: bool = False) -> Optional[Dict]:
        """Get complete case data with defendants and skip trace records"""
        try:
            # Get case
            case = self.get_case_by_docket(docket_number)
            if not case:
                return None

            # Get defendants by docket number
            defendants = self.get_defendants_by_docket(docket_number)

            # Get production skip trace records for the case
            skiptraces = self.get_skiptraces_by_docket(docket_number, is_sandbox=False)

            # Optionally get sandbox skip trace records
            skiptraces_sandbox = []
            if include_sandbox:
                skiptraces_sandbox = self.get_skiptraces_by_docket(docket_number, is_sandbox=True)

            case['defendants'] = defendants
            case['skiptraces'] = skiptraces
            if include_sandbox:
                case['skiptraces_sandbox'] = skiptraces_sandbox
            return case
        except Exception as e:
            logger.error(f"Error fetching full case data: {e}")
            return None

    # Utility methods
    def delete_case(self, docket_number: str) -> bool:
        """Delete a case (cascades to defendants and skip trace records)"""
        try:
            response = self.client.table('cases').delete().eq('docket_number', docket_number).execute()
            logger.info(f"Case deleted: {docket_number}")
            return True
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            return False

    def get_recent_cases(self, limit: int = 10) -> List[Dict]:
        """Get most recent cases"""
        try:
            response = self.client.table('cases').select("*").order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching recent cases: {e}")
            return []

    def get_cases_with_defendants(self, town: str = None) -> List[Dict]:
        """Get cases with their defendants joined"""
        try:
            query = self.client.table('cases').select("*, defendants(*)")
            if town:
                query = query.eq('town', town)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching cases with defendants: {e}")
            return []

    def get_town_skip_trace_stats(self, town: str) -> Dict:
        """Get skip trace statistics for a town
        Returns:
            - total_cases: Total unique docket numbers for the town
            - traced_cases: Number of cases that have been skip traced
            - untraced_cases: Number of cases not yet skip traced
        """
        try:
            # Get all cases for the town
            cases = self.get_cases_by_town(town)
            docket_numbers = list(set(case['docket_number'] for case in cases))
            total_cases = len(docket_numbers)

            if total_cases == 0:
                return {
                    'town': town,
                    'scraped': False,
                    'total_cases': 0,
                    'traced_cases': 0,
                    'untraced_cases': 0
                }

            # Get skip traces for these docket numbers
            traced_dockets = set()
            for docket in docket_numbers:
                skiptraces = self.get_skiptraces_by_docket(docket)
                if skiptraces:
                    traced_dockets.add(docket)

            traced_cases = len(traced_dockets)
            untraced_cases = total_cases - traced_cases

            return {
                'town': town,
                'scraped': True,
                'total_cases': total_cases,
                'traced_cases': traced_cases,
                'untraced_cases': untraced_cases
            }
        except Exception as e:
            logger.error(f"Error getting town skip trace stats: {str(e)}")
            return {
                'town': town,
                'scraped': False,
                'total_cases': 0,
                'traced_cases': 0,
                'untraced_cases': 0,
                'error': str(e)
            }

    # Skip trace status checking methods
    def has_been_skip_traced(self, docket_number: str, is_sandbox: bool = False) -> bool:
        """Check if a case has already been skip traced

        Args:
            docket_number: The docket number to check
            is_sandbox: Check sandbox or production table

        Returns:
            True if the case has skip trace records, False otherwise
        """
        table_name = 'skiptrace_sandbox' if is_sandbox else 'skiptrace'
        try:
            response = self.client.table(table_name).select("id").eq('docket_number', docket_number).limit(1).execute()
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            logger.error(f"Error checking skip trace status: {e}")
            return False

    # Cost tracking methods
    def record_skip_trace_cost(self, docket_number: str, lookup_count: int = 1,
                               cost_per_lookup: float = 0.07, is_sandbox: bool = False) -> Optional[Dict]:
        """Record the cost of a skip trace operation

        Args:
            docket_number: The docket number
            lookup_count: Number of lookups performed
            cost_per_lookup: Cost per lookup (default $0.07)
            is_sandbox: Whether this was a sandbox operation

        Returns:
            The created cost record or None
        """
        try:
            cost_data = {
                'docket_number': docket_number,
                'lookup_count': lookup_count,
                'cost_per_lookup': cost_per_lookup,
                'is_sandbox': is_sandbox
            }
            response = self.client.table('skiptrace_costs').insert(cost_data).execute()
            logger.info(f"Recorded skip trace cost for {docket_number}: ${lookup_count * cost_per_lookup:.2f}")
            return response.data[0] if response.data else None
        except Exception as e:
            # Try to update existing record if unique constraint violated
            if 'duplicate key' in str(e).lower():
                try:
                    # Get existing record
                    existing = self.client.table('skiptrace_costs').select("*").eq('docket_number', docket_number).eq('is_sandbox', is_sandbox).execute()
                    if existing.data:
                        current_count = existing.data[0]['lookup_count']
                        # Update with new count
                        response = self.client.table('skiptrace_costs').update({
                            'lookup_count': current_count + lookup_count
                        }).eq('docket_number', docket_number).eq('is_sandbox', is_sandbox).execute()
                        logger.info(f"Updated skip trace cost for {docket_number}: added {lookup_count} lookups")
                        return response.data[0] if response.data else None
                except Exception as update_e:
                    logger.error(f"Error updating skip trace cost: {update_e}")
            else:
                logger.error(f"Error recording skip trace cost: {e}")
            return None

    def get_skip_trace_costs(self, town: str = None, is_sandbox: Optional[bool] = None) -> Dict[str, Any]:
        """Get skip trace cost summary

        Args:
            town: Optional town filter
            is_sandbox: Optional filter for sandbox/production (None = both)

        Returns:
            Dictionary with cost statistics
        """
        try:
            query = self.client.table('skiptrace_costs').select("*")

            if is_sandbox is not None:
                query = query.eq('is_sandbox', is_sandbox)

            response = query.execute()
            costs = response.data if response.data else []

            # If town filter, need to join with cases
            if town and costs:
                case_dockets = self.get_cases_by_town(town)
                town_dockets = {c['docket_number'] for c in case_dockets}
                costs = [c for c in costs if c['docket_number'] in town_dockets]

            # Calculate totals
            total_lookups = sum(c['lookup_count'] for c in costs)
            total_cost = sum(c['lookup_count'] * c['cost_per_lookup'] for c in costs)

            return {
                'total_cases': len(costs),
                'total_lookups': total_lookups,
                'total_cost': total_cost,
                'average_lookups_per_case': total_lookups / len(costs) if costs else 0,
                'cost_per_lookup': 0.07,
                'details': costs
            }
        except Exception as e:
            logger.error(f"Error getting skip trace costs: {e}")
            return {
                'total_cases': 0,
                'total_lookups': 0,
                'total_cost': 0,
                'average_lookups_per_case': 0,
                'cost_per_lookup': 0.07,
                'details': []
            }

    # Sandbox-specific helper methods
    def clear_sandbox_skiptraces(self, docket_number: str = None) -> bool:
        """Clear sandbox skip trace records for testing

        Args:
            docket_number: Optional - clear only for specific case, otherwise clear all
        """
        try:
            query = self.client.table('skiptrace_sandbox').delete()
            if docket_number:
                query = query.eq('docket_number', docket_number)
                logger.info(f"Cleared sandbox skip traces for docket: {docket_number}")
            else:
                logger.info("Cleared all sandbox skip traces")

            query.execute()
            return True
        except Exception as e:
            logger.error(f"Error clearing sandbox skip traces: {e}")
            return False

    def copy_sandbox_to_production(self, docket_number: str) -> bool:
        """Copy sandbox skip trace records to production table

        Args:
            docket_number: Docket number to copy records for
        """
        try:
            # Get sandbox records
            sandbox_records = self.get_skiptraces_by_docket(docket_number, is_sandbox=True)
            if not sandbox_records:
                logger.info(f"No sandbox records found for {docket_number}")
                return True

            # Remove id field and prepare for production insert
            production_data = []
            for record in sandbox_records:
                data = {
                    'docket_number': record['docket_number'],
                    'phone_number': record['phone_number'],
                    'phone_type': record.get('phone_type'),
                    'api_response': record.get('api_response')
                }
                production_data.append(data)

            # Insert into production table
            result = self.insert_skiptraces(production_data, is_sandbox=False)
            if result:
                logger.info(f"Copied {len(result)} records from sandbox to production for {docket_number}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error copying sandbox to production: {e}")
            return False