#!/usr/bin/env python3
"""
Phase 5 Integration Test
Tests the main.py integration with Sandbox Batch API functionality
"""

import sys
import os
import subprocess
import json

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def test_phase5_integration():
    """Test Phase 5 integration through main.py with --skip-trace flag"""
    print("\n" + "="*60)
    print(f"{BOLD}INTEGRATION TEST: Phase 5 - Sandbox Batch API{RESET}")
    print("="*60)
    
    # Load test cases from batchapi_test_cases.json
    test_cases_file = 'tests/batchapi_test_cases.json'
    if os.path.exists(test_cases_file):
        with open(test_cases_file, 'r') as f:
            test_addresses = json.load(f)
            print(f"\n[INPUT] Using test addresses from {test_cases_file}")
            for addr in test_addresses[:2]:
                print(f"  - {addr['street']}, {addr['city']}, {addr['state']} {addr['zip']}")
    
    town = "Middletown"
    print(f"\n[INPUT] Testing main.py with town: {town} and --skip-trace flag")
    print("-" * 40)
    
    try:
        # Run main.py with the town argument and --skip-trace flag
        result = subprocess.run(
            [sys.executable, "main.py", town, "--skip-trace"],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        print("\n[OUTPUT]")
        print(result.stdout)
        
        if result.stderr:
            print("\n[STDERR]")
            print(result.stderr)
        
        # Check if the process ran successfully
        if result.returncode != 0:
            raise Exception(f"main.py exited with code {result.returncode}")
        
        # Check if output file was created
        output_filename = f"cases_{town.lower()}.json"
        if not os.path.exists(output_filename):
            raise Exception(f"Output file {output_filename} was not created")
        
        # Load and validate the output file
        with open(output_filename, 'r') as f:
            cases = json.load(f)
        
        print(f"\n[VALIDATION]")
        print(f"Output file created: {output_filename}")
        print(f"Number of cases: {len(cases)}")
        
        # Validate data structure
        if len(cases) == 0:
            raise Exception("No cases were scraped")
        
        # Check if phone numbers were added (at least to first 2 cases)
        cases_with_phones = 0
        for i, case in enumerate(cases[:2]):
            if 'phone_numbers' in case:
                cases_with_phones += 1
                print(f"Case {i+1} phone numbers: {case['phone_numbers']}")
        
        if cases_with_phones == 0:
            raise Exception("No phone numbers were added to any cases")
        
        # Validate that sandbox API was called (check output for API messages)
        if "Batch API Phone Lookup (Sandbox)" not in result.stdout:
            raise Exception("Batch API integration not executed")
        
        if "[SANDBOX API]" not in result.stdout:
            raise Exception("Sandbox API was not called")
        
        print(f"\n✓ Output file contains valid case data")
        print(f"✓ Phone numbers added to {cases_with_phones} cases")
        print("✓ Sandbox Batch API integration working correctly")
        
        print("\n" + "="*60)
        print(f"{GREEN}{BOLD}INTEGRATION TEST: Phase 5 - SUCCESS{RESET}")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"{RED}{BOLD}INTEGRATION TEST: Phase 5 - FAILURE{RESET}")
        print(f"{RED}Error: {str(e)}{RESET}")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    test_phase5_integration()