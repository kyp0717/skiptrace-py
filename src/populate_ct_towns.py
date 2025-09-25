#!/usr/bin/env python3
"""
Script to populate Connecticut towns and counties into Supabase
This should be run before scraping court cases to ensure town validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ct_town_scraper import CTTownScraper
from db_connector import DatabaseConnector
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to scrape and populate CT towns"""

    print("\n" + "="*60)
    print("Connecticut Towns and Counties Database Population")
    print("="*60)

    try:
        # Initialize scraper
        logger.info("Initializing CT town scraper...")
        scraper = CTTownScraper()

        # Scrape towns and counties
        logger.info("Scraping towns and counties from CT State Library...")
        towns_data = scraper.scrape_towns_and_counties()

        if not towns_data:
            logger.error("No towns data retrieved from scraper")
            return False

        print(f"\n✓ Successfully scraped {len(towns_data)} town-county pairs")

        # Show summary
        counties = scraper.get_all_counties()
        print(f"✓ Found {len(counties)} counties: {', '.join(counties)}")

        # Initialize database connection
        logger.info("Connecting to Supabase...")
        db = DatabaseConnector()

        # Check if table already has data
        existing_towns = db.get_all_ct_towns()
        if existing_towns:
            print(f"\n⚠ Warning: ct_towns table already contains {len(existing_towns)} entries")
            response = input("Do you want to clear and repopulate the table? (yes/no): ")
            if response.lower() == 'yes':
                logger.info("Clearing existing ct_towns data...")
                db.clear_ct_towns()
                print("✓ Existing data cleared")
            else:
                print("Skipping population. Existing data retained.")
                return True

        # Populate database
        print(f"\nPopulating database with {len(towns_data)} towns...")
        inserted_count = db.populate_ct_towns(towns_data)

        print(f"✓ Successfully inserted {inserted_count} towns into database")

        # Verify data
        print("\nVerifying data in database...")
        db_towns = db.get_all_ct_towns()
        print(f"✓ Database now contains {len(db_towns)} towns")

        # Show sample data
        print("\nSample data from database:")
        for i, town_record in enumerate(db_towns[:5]):
            print(f"  {i+1}. {town_record['town']}, {town_record['county']} County")

        # Test specific town lookup
        test_town = "Middletown"
        town_info = db.get_ct_town(test_town)
        if town_info:
            print(f"\nTest lookup: {test_town} is in {town_info['county']} County")

        print("\n" + "="*60)
        print("✓ CT Towns population completed successfully!")
        print("="*60)

        return True

    except Exception as e:
        logger.error(f"Error during population: {e}")
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)