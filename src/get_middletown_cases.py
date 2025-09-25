import csv
import time
from case_scraper import CaseScraper
from batch_api_connector import BatchAPIConnector

def main():
    print("="*60)
    print("Fetching Middletown Cases with Phone Numbers")
    print("="*60)
    
    # Step 1: Scrape cases from CT Judicial website
    print("\n[Step 1] Scraping cases from CT Judicial website...")
    scraper = CaseScraper('Middletown')
    cases = scraper.scrape_cases()
    
    if not cases:
        print("No cases found!")
        return
    
    # Get first 10 cases
    cases = cases[:10]
    print(f"Found {len(cases)} cases to process")
    
    # Step 2: Get phone numbers from BatchData API
    print("\n[Step 2] Fetching phone numbers from BatchData API...")
    connector = BatchAPIConnector('prod')
    
    enriched_cases = []
    for i, case in enumerate(cases, 1):
        print(f"\nProcessing case {i}/10:")
        print(f"  Case: {case['case_name']}")
        print(f"  Address: {case['address']}")
        
        # Skip if address is unclear
        if "See Clerk" in case['address'] or not case['address']:
            print("  Skipping - invalid address")
            enriched_case = case.copy()
            enriched_case['phone_numbers'] = ''
            enriched_cases.append(enriched_case)
            continue
        
        # Parse address for API
        address_dict = {
            'street': case['address'],
            'city': 'Middletown',
            'state': 'CT',
            'zip': '06457'
        }
        
        # Get phone numbers
        phone_numbers = connector.send_skip_trace_request(address_dict)
        
        # Add phone numbers to case data
        enriched_case = case.copy()
        enriched_case['phone_numbers'] = '; '.join(phone_numbers) if phone_numbers else ''
        enriched_cases.append(enriched_case)
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Step 3: Save to CSV
    print("\n[Step 3] Saving to CSV file...")
    
    fieldnames = ['case_name', 'defendant', 'address', 'docket_number', 'docket_url', 'phone_numbers']
    
    with open('middletown_cases.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for case in enriched_cases:
            writer.writerow({
                'case_name': case['case_name'],
                'defendant': case['defendant'],
                'address': case['address'],
                'docket_number': case['docket_number'],
                'docket_url': case['docket_url'],
                'phone_numbers': case['phone_numbers']
            })
    
    print("\n" + "="*60)
    print("✅ Complete! Saved 10 cases to middletown_cases.csv")
    print("="*60)
    
    # Display summary
    print("\nSummary of cases saved:")
    for i, case in enumerate(enriched_cases, 1):
        phones = case['phone_numbers'] if case['phone_numbers'] else 'No phones found'
        print(f"{i}. {case['defendant'][:30]:30} | {phones}")

if __name__ == '__main__':
    main()