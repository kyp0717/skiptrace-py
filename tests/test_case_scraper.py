
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import csv
from src.case_scraper import CaseScraper


# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


class TestCaseScraper(unittest.TestCase):
    def test_scrape_cases(self):
        """
        Tests that the scrape_cases method can find cases for a given town and that the extracted data is correct.
        """
        print("\n" + "="*60)
        print(f"{BOLD}FEATURE TEST: Phase 4 - Web Scraping{RESET}")
        print("="*60)
        
        town = "Middletown"
        print(f"\n[INPUT] Searching for cases in town: {town}")
        print("-" * 40)
        
        try:
            scraper = CaseScraper(town)
            cases = scraper.scrape_cases()
            
            print(f"\n[OUTPUT] Found {len(cases)} cases for {town}")
            print("-" * 40)
            
            self.assertIsNotNone(cases)
            self.assertGreater(len(cases), 0)
            
            # Display first 3 cases as examples
            print("\n[SAMPLE RESULTS] First 3 cases:")
            for i, case in enumerate(cases[:3], 1):
                print(f"\nCase {i}:")
                print(f"  Case Name: {case.get('case_name', 'N/A')}")
                print(f"  Defendant: {case.get('defendant', 'N/A')}")
                print(f"  Address: {case.get('address', 'N/A')}")
                print(f"  Docket #: {case.get('docket_number', 'N/A')}")
                print(f"  Docket URL: {case.get('docket_url', 'N/A')}")
            
            with open('tests/test_addresses.json', 'w') as f:
                import json
                addresses = []
                for case in cases[:2]:
                    # Try to parse address, but handle various formats
                    try:
                        parts = case['address'].split(',')
                        if len(parts) >= 2:
                            street = parts[0].strip()
                            city_state_zip = parts[1].strip().split()
                            if len(city_state_zip) >= 2:
                                city = ' '.join(city_state_zip[:-2]) if len(city_state_zip) > 2 else city_state_zip[0]
                                state = city_state_zip[-2]
                                zip_code = city_state_zip[-1]
                                addresses.append({
                                    'street': street,
                                    'city': city,
                                    'state': state,
                                    'zip': zip_code
                                })
                    except:
                        # Skip addresses that can't be parsed
                        pass
                json.dump(addresses, f)
                
            print("\n[VALIDATION] Testing data structure integrity...")
            for case in cases:
                self.assertIn("case_name", case)
                self.assertIn("docket_number", case)
                self.assertIn("docket_url", case)
                self.assertIn("address", case)
                self.assertIn("defendant", case)
                self.assertTrue(
                    case["docket_url"].startswith("https://civilinquiry.jud.ct.gov/")
                )
            print("✓ All cases have required fields")
            print("✓ All docket URLs are properly formatted")
            
            # Test CSV output
            print("\n[CSV OUTPUT] Testing CSV file generation...")
            csv_filename = scraper.save_to_csv(cases)
            
            # Verify CSV file exists and is valid
            self.assertTrue(os.path.exists(csv_filename))
            print(f"✓ CSV file created: {csv_filename}")
            
            # Read and validate CSV content
            with open(csv_filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                csv_cases = list(reader)
                
                self.assertEqual(len(csv_cases), len(cases))
                print(f"✓ CSV contains {len(csv_cases)} cases (matches scraped data)")
                
                # Verify first case data matches
                if csv_cases:
                    first_csv = csv_cases[0]
                    first_case = cases[0]
                    self.assertEqual(first_csv['case_name'], first_case['case_name'])
                    self.assertEqual(first_csv['docket_number'], first_case['docket_number'])
                    print("✓ CSV data integrity verified")
            
            print("\n" + "="*60)
            print(f"{GREEN}{BOLD}Phase 4 Feature Test: SUCCESS{RESET}")
            print("="*60)
            
        except Exception as e:
            print("\n" + "="*60)
            print(f"{RED}{BOLD}Phase 4 Feature Test: FAILURE{RESET}")
            print(f"{RED}Error: {str(e)}{RESET}")
            print("="*60)
            raise


if __name__ == "__main__":
    unittest.main()
