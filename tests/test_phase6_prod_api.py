#!/usr/bin/env python3
"""
Phase 6 Test - Production Batch API
Tests direct connection to production batch API
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.batch_api_connector import BatchAPIConnector
from src.case_scraper import CaseScraper

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def test_prod_api():
    """Test Production Batch API with real addresses from case scraper"""
    print("\n" + "="*60)
    print(f"{BOLD}Phase 6 Test: Production Batch API{RESET}")
    print("="*60)
    
    try:
        # First, get real addresses from case scraper
        print("\n[STEP 1] Getting real addresses from case scraper...")
        town = "Middletown"
        scraper = CaseScraper(town)
        cases = scraper.scrape_cases()
        
        if not cases or len(cases) < 2:
            raise Exception("Not enough cases found for testing")
        
        # Use first 2 addresses as per requirements
        test_cases = cases[:2]
        print(f"Found {len(cases)} cases, using first 2 for testing")
        
        # Initialize production API connector
        print("\n[STEP 2] Initializing Production API connector...")
        api_connector = BatchAPIConnector('prod')
        
        # Test each address
        print("\n[STEP 3] Testing production API with real addresses...")
        print("REMINDER: Using only 2 addresses for testing as per requirements")
        
        successful_requests = 0
        for i, case in enumerate(test_cases, 1):
            print(f"\n{'-'*40}")
            print(f"Test Case {i}:")
            print(f"  Defendant: {case['defendant']}")
            print(f"  Address: {case['address']}")
            
            # Parse address
            parts = case['address'].split(',')
            if len(parts) >= 2:
                street = parts[0].strip()
                remainder = parts[1].strip()
                words = remainder.split()
                if len(words) >= 2:
                    address_dict = {
                        'street': street,
                        'city': ' '.join(words[:-2]) if len(words) > 2 else words[0],
                        'state': words[-2],
                        'zip': words[-1]
                    }
                    
                    # Send request to production API
                    phone_numbers = api_connector.send_skip_trace_request(address_dict)
                    
                    if phone_numbers:
                        print(f"  Result: Found {len(phone_numbers)} phone numbers")
                        print(f"  Phone Numbers: {', '.join(phone_numbers)}")
                        successful_requests += 1
                    else:
                        print("  Result: No phone numbers found")
                else:
                    print("  Result: Could not parse address")
            else:
                print("  Result: Invalid address format")
        
        print(f"\n{'-'*40}")
        print(f"Summary: {successful_requests}/{len(test_cases)} successful API requests")
        
        if successful_requests > 0:
            print("\n" + "="*60)
            print(f"{GREEN}{BOLD}Phase 6 Test: SUCCESS{RESET}")
            print("="*60)
        else:
            print("\n" + "="*60)
            print(f"{RED}{BOLD}Phase 6 Test: WARNING - No phone numbers found{RESET}")
            print("This may be normal if the addresses have no associated phone numbers")
            print("="*60)
            
    except Exception as e:
        print("\n" + "="*60)
        print(f"{RED}{BOLD}Phase 6 Test: FAILURE{RESET}")
        print(f"{RED}Error: {str(e)}{RESET}")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    test_prod_api()