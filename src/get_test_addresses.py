from case_scraper import CaseScraper
import json

scraper = CaseScraper('Middletown')
cases = scraper.scrape_cases()

if cases and len(cases) >= 2:
    # Get first two addresses for Phase 6 testing
    test_addresses = []
    for case in cases[:2]:
        address_str = case.get('address', '')
        if address_str and "See Clerk" not in address_str:
            # Parse the address (simplified)
            test_addresses.append({
                'street': address_str,
                'city': 'Middletown',
                'state': 'CT',
                'zip': '06457'
            })
    
    with open('tests/phase6_test_addresses.json', 'w') as f:
        json.dump(test_addresses, f, indent=2)
    
    print(f'Saved {len(test_addresses)} addresses for Phase 6 testing')
    print('Addresses:', test_addresses)
else:
    print('Failed to get addresses')