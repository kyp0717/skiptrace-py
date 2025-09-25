import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from src.batch_api_connector import BatchAPIConnector


class TestBatchAPISandbox(unittest.TestCase):
    def test_sandbox_api(self):
        """Test Phase 5: Sandbox Batch API"""
        print("\n" + "="*60)
        print("Phase 5 - Sandbox Batch API Test")
        print("="*60)
        
        # Load test cases
        with open('tests/batchapi_test_cases.json', 'r') as f:
            test_data = json.load(f)
        
        # Initialize sandbox connector
        connector = BatchAPIConnector('sandbox')
        
        # Test each address
        for i, request in enumerate(test_data['requests'], 1):
            address = request['propertyAddress']
            
            print(f"\n[TEST CASE {i}]")
            print(f"[INPUT] Testing address:")
            print(f"  Street: {address['street']}")
            print(f"  City: {address['city']}")  
            print(f"  State: {address['state']}")
            print(f"  ZIP: {address['zip']}")
            print("-" * 40)
            
            # Send request
            phone_numbers = connector.send_skip_trace_request(address)
            
            print(f"\n[OUTPUT] Results:")
            if phone_numbers:
                print(f"  Found {len(phone_numbers)} phone numbers:")
                for phone in phone_numbers:
                    print(f"    - {phone}")
                self.assertIsInstance(phone_numbers, list)
                self.assertTrue(len(phone_numbers) > 0)
            else:
                print("  No phone numbers found")
            
            print("-" * 40)
        
        print("\n" + "="*60)
        print("Phase 5 Test: PASSED")
        print("="*60)


if __name__ == '__main__':
    unittest.main()