#!/usr/bin/env python3
"""
Phase 4 Integration Test
Tests the main.py integration with case scraping functionality
"""

import sys
import os
import subprocess
import json
import csv

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def test_phase4_integration():
    """Test Phase 4 integration through main.py"""
    print("\n" + "="*60)
    print(f"{BOLD}INTEGRATION TEST: Phase 4 - Web Scraping{RESET}")
    print("="*60)
    
    town = "Middletown"
    print(f"\n[INPUT] Testing main.py with town: {town}")
    print("-" * 40)
    
    try:
        # Run main.py with the town argument
        result = subprocess.run(
            [sys.executable, "main.py", town],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print("\n[OUTPUT]")
        print(result.stdout)
        
        if result.stderr:
            print("\n[STDERR]")
            print(result.stderr)
        
        # Check if the process ran successfully
        if result.returncode != 0:
            raise Exception(f"main.py exited with code {result.returncode}")
        
        # Check if output files were created
        json_filename = f"cases_{town.lower()}.json"
        csv_filename = f"cases_{town.lower()}.csv"
        
        if not os.path.exists(json_filename):
            raise Exception(f"JSON output file {json_filename} was not created")
        
        if not os.path.exists(csv_filename):
            raise Exception(f"CSV output file {csv_filename} was not created")
        
        # Load and validate the JSON file
        with open(json_filename, 'r') as f:
            cases = json.load(f)
        
        print(f"\n[VALIDATION]")
        print(f"Output files created:")
        print(f"  JSON: {json_filename}")
        print(f"  CSV: {csv_filename}")
        print(f"Number of cases: {len(cases)}")
        
        # Validate data structure
        if len(cases) == 0:
            raise Exception("No cases were scraped")
        
        # Check first case has all required fields
        first_case = cases[0]
        required_fields = ['case_name', 'defendant', 'address', 'docket_number', 'docket_url']
        for field in required_fields:
            if field not in first_case:
                raise Exception(f"Missing required field: {field}")
        
        # Validate CSV file
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            csv_cases = list(reader)
            
            if len(csv_cases) != len(cases):
                raise Exception(f"CSV has {len(csv_cases)} cases but JSON has {len(cases)}")
            
            print(f"✓ CSV file contains {len(csv_cases)} cases")
        
        print("✓ Output files contain valid case data")
        print("✓ All required fields present")
        print("✓ Both JSON and CSV outputs generated")
        print("✓ Integration working correctly")
        
        print("\n" + "="*60)
        print(f"{GREEN}{BOLD}INTEGRATION TEST: Phase 4 - SUCCESS{RESET}")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"{RED}{BOLD}INTEGRATION TEST: Phase 4 - FAILURE{RESET}")
        print(f"{RED}Error: {str(e)}{RESET}")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    test_phase4_integration()