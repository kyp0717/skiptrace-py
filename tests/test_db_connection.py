"""
Test database connection and operations for Supabase
"""

import unittest
import os
from datetime import datetime
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db_connector import DatabaseConnector
from src.db_models import Case, Defendant, PhoneNumber

class TestDatabaseConnection(unittest.TestCase):
    """Test Supabase database connection and operations"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        load_dotenv()
        cls.db = DatabaseConnector()
        cls.test_docket = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def test_01_connection(self):
        """Test database connection"""
        print("\n" + "="*50)
        print("TEST: Database Connection")
        print("="*50)

        result = self.db.test_connection()

        if result:
            print("\033[92m✓ Database connection successful\033[0m")
        else:
            print("\033[91m✗ Database connection failed\033[0m")

        self.assertTrue(result, "Database connection should be successful")

    def test_02_insert_case(self):
        """Test inserting a case"""
        print("\n" + "="*50)
        print("TEST: Insert Case")
        print("="*50)

        case_data = {
            'case_name': 'Test Bank vs John Doe',
            'docket_number': self.test_docket,
            'docket_url': 'https://example.com/case/test',
            'town': 'TestTown'
        }

        print(f"Input: {case_data}")
        result = self.db.insert_case(case_data)
        print(f"Output: {result}")

        if result:
            print("\033[92m✓ Case inserted successfully\033[0m")
        else:
            print("\033[91m✗ Failed to insert case\033[0m")

        self.assertIsNotNone(result, "Case should be inserted successfully")
        self.assertEqual(result['docket_number'], self.test_docket)

    def test_03_insert_defendant(self):
        """Test inserting a defendant"""
        print("\n" + "="*50)
        print("TEST: Insert Defendant")
        print("="*50)

        # First get the case we just inserted
        case = self.db.get_case_by_docket(self.test_docket)
        self.assertIsNotNone(case, "Should find the test case")

        defendant_data = {
            'docket_number': self.test_docket,
            'name': 'John Doe',
            'address': '123 Test St',
            'town': 'TestTown',
            'state': 'CT',
            'zip': '06001'
        }

        print(f"Input: {defendant_data}")
        result = self.db.insert_defendant(defendant_data)
        print(f"Output: {result}")

        if result:
            print("\033[92m✓ Defendant inserted successfully\033[0m")
            self.defendant_id = result['id']
        else:
            print("\033[91m✗ Failed to insert defendant\033[0m")

        self.assertIsNotNone(result, "Defendant should be inserted successfully")

    def test_04_insert_skiptraces(self):
        """Test inserting skip trace records to both production and sandbox"""
        print("\n" + "="*50)
        print("TEST: Insert Skip Traces (Production and Sandbox)")
        print("="*50)

        # Test production table
        print("\n--- Testing Production Table ---")
        production_data = [
            {
                'docket_number': self.test_docket,
                'phone_number': '860-555-0001',
                'phone_type': 'mobile'
            }
        ]

        print(f"Input (Production): {production_data}")
        result_prod = self.db.insert_skiptraces(production_data, is_sandbox=False)
        print(f"Output (Production): {result_prod}")

        # Test sandbox table
        print("\n--- Testing Sandbox Table ---")
        sandbox_data = [
            {
                'docket_number': self.test_docket,
                'phone_number': '860-555-0002',
                'phone_type': 'landline'
            },
            {
                'docket_number': self.test_docket,
                'phone_number': '860-555-0003',
                'phone_type': 'mobile'
            }
        ]

        print(f"Input (Sandbox): {sandbox_data}")
        result_sandbox = self.db.insert_skiptraces(sandbox_data, is_sandbox=True)
        print(f"Output (Sandbox): {result_sandbox}")

        if result_prod and len(result_prod) == 1:
            print("\033[92m✓ Production skip trace record inserted successfully\033[0m")
        else:
            print("\033[91m✗ Failed to insert production skip trace record\033[0m")

        if result_sandbox and len(result_sandbox) == 2:
            print("\033[92m✓ Sandbox skip trace records inserted successfully\033[0m")
        else:
            print("\033[91m✗ Failed to insert sandbox skip trace records\033[0m")

        self.assertIsNotNone(result_prod, "Production skip trace should be inserted")
        self.assertEqual(len(result_prod), 1, "Should insert 1 production record")
        self.assertIsNotNone(result_sandbox, "Sandbox skip traces should be inserted")
        self.assertEqual(len(result_sandbox), 2, "Should insert 2 sandbox records")

    def test_05_get_full_case_data(self):
        """Test retrieving complete case data"""
        print("\n" + "="*50)
        print("TEST: Get Full Case Data")
        print("="*50)

        print(f"Input: docket_number = {self.test_docket} (with sandbox data)")
        result = self.db.get_full_case_data(self.test_docket, include_sandbox=True)

        if result:
            print(f"Output:")
            print(f"  Case: {result['case_name']}")
            print(f"  Docket: {result['docket_number']}")
            print(f"  Defendants: {len(result.get('defendants', []))}")
            for defendant in result.get('defendants', []):
                print(f"    - {defendant['name']}")
                if defendant.get('address'):
                    print(f"      Address: {defendant['address']}")

            # Print production skip traces
            skiptraces = result.get('skiptraces', [])
            if skiptraces:
                print(f"  Production Skip Traces: {len(skiptraces)}")
                for skiptrace in skiptraces:
                    print(f"    • {skiptrace['phone_number']} ({skiptrace.get('phone_type', 'unknown')})")

            # Print sandbox skip traces
            skiptraces_sandbox = result.get('skiptraces_sandbox', [])
            if skiptraces_sandbox:
                print(f"  Sandbox Skip Traces: {len(skiptraces_sandbox)}")
                for skiptrace in skiptraces_sandbox:
                    print(f"    • {skiptrace['phone_number']} ({skiptrace.get('phone_type', 'unknown')})")

            print("\033[92m✓ Full case data retrieved successfully\033[0m")
        else:
            print("\033[91m✗ Failed to retrieve full case data\033[0m")

        self.assertIsNotNone(result, "Should retrieve full case data")
        self.assertTrue('defendants' in result, "Should include defendants")
        self.assertTrue('skiptraces' in result, "Should include production skiptraces")
        self.assertTrue('skiptraces_sandbox' in result, "Should include sandbox skiptraces")

    def test_06_cleanup(self):
        """Clean up test data"""
        print("\n" + "="*50)
        print("TEST: Cleanup Test Data")
        print("="*50)

        result = self.db.delete_case(self.test_docket)

        if result:
            print(f"\033[92m✓ Test case {self.test_docket} deleted successfully\033[0m")
        else:
            print(f"\033[91m✗ Failed to delete test case\033[0m")

        self.assertTrue(result, "Should delete test case")

        # Verify deletion
        case = self.db.get_case_by_docket(self.test_docket)
        self.assertIsNone(case, "Case should be deleted")

if __name__ == '__main__':
    unittest.main()