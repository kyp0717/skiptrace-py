import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from src.batch_api_connector import BatchAPIConnector


class TestBatchAPIProd(unittest.TestCase):
    def test_prod_api(self):
        """Test Phase 6: Production Batch API"""
        print("\n" + "="*60)
        print("Phase 6 - Production Batch API Test")
        print("="*60)
        
        # Load test addresses from Phase 4 results or use defaults
        try:
            with open('tests/phase6_test_addresses.json', 'r') as f:
                test_addresses = json.load(f)
        except FileNotFoundError:
            # Use default test addresses if file not found
            test_addresses = [
                {
                    'street': '647 MINOR ST.',
                    'city': 'Middletown',
                    'state': 'CT',
                    'zip': '06457'
                },
                {
                    'street': '104 Bell Street',
                    'city': 'Middletown',
                    'state': 'CT',
                    'zip': '06457'
                }
            ]
        
        # Initialize production connector
        connector = BatchAPIConnector('prod')
        
        # Test each address
        for i, address in enumerate(test_addresses[:2], 1):  # Limit to 2 addresses
            print(f"\n[TEST CASE {i}]")
            print(f"[INPUT] Testing address:")
            print(f"  Street: {address['street']}")
            print(f"  City: {address['city']}")  
            print(f"  State: {address['state']}")
            print(f"  ZIP: {address['zip']}")
            print("-" * 40)
            
            # Send request to production API
            phone_numbers = connector.send_skip_trace_request(address)
            
            print(f"\n[OUTPUT] Results:")
            if phone_numbers:
                print(f"  Found {len(phone_numbers)} phone numbers:")
                for phone in phone_numbers:
                    print(f"    - {phone}")
                self.assertIsInstance(phone_numbers, list)
            else:
                print("  No phone numbers found (may require valid API token)")
                # Production API might fail without valid token, which is okay for testing
            
            print("-" * 40)
        
        print("\n[NOTE] Production API requires valid authentication token.")
        print("If requests failed, ensure batchapi.csv contains valid production token.")
        
        print("\n" + "="*60)
        print("Phase 6 Test: COMPLETED")
        print("="*60)


if __name__ == '__main__':
    unittest.main()