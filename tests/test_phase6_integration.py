#!/usr/bin/env python3
"""
Phase 6 Integration Test
Tests the main.py integration with Production Batch API functionality
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


def test_phase6_integration():
    """Test Phase 6 integration through main.py with --skip-trace --prod flags"""
    print("\n" + "="*60)
    print(f"{BOLD}INTEGRATION TEST: Phase 6 - Production Batch API{RESET}")
    print("="*60)
    
    town = "Middletown"
    print(f"\n[INPUT] Testing main.py with town: {town}")
    print("        Flags: --skip-trace --prod")
    print("-" * 40)
    
    try:
        # Run main.py with the town argument and production flags
        result = subprocess.run(
            [sys.executable, "main.py", town, "--skip-trace", "--prod"],
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
        total_phone_numbers = 0
        for i, case in enumerate(cases[:2]):
            if 'phone_numbers' in case and case['phone_numbers']:
                cases_with_phones += 1
                total_phone_numbers += len(case['phone_numbers'])
                print(f"Case {i+1} phone numbers: {case['phone_numbers']}")
        
        # Validate that production API was called (check output for API messages)
        if "Phase 6: Batch API Phone Lookup (Production)" not in result.stdout:
            raise Exception("Production Batch API integration not executed")
        
        if "[PROD API]" not in result.stdout:
            raise Exception("Production API was not called")
        
        print(f"\n✓ Output file contains valid case data")
        print(f"✓ Phone lookup attempted for 2 cases")
        if cases_with_phones > 0:
            print(f"✓ Phone numbers found for {cases_with_phones} cases (Total: {total_phone_numbers} numbers)")
        else:
            print("⚠ No phone numbers found (this may be normal for these addresses)")
        print("✓ Production Batch API integration executed successfully")
        
        print("\n" + "="*60)
        print(f"{GREEN}{BOLD}INTEGRATION TEST: Phase 6 - SUCCESS{RESET}")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"{RED}{BOLD}INTEGRATION TEST: Phase 6 - FAILURE{RESET}")
        print(f"{RED}Error: {str(e)}{RESET}")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    test_phase6_integration()