"""
Populate Connecticut Towns table in Supabase
This script scrapes CT towns/counties and loads them into the database
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def populate_ct_towns():
    """
    Scrape Connecticut towns and counties and populate the database
    """
    # Initialize database connector
    db = DatabaseConnector()

    # Test database connection
    if not db.test_connection():
        logger.error("Failed to connect to database")
        return False

    logger.info("Database connection successful")

    # Initialize scraper
    scraper = CTTownScraper()

    # Scrape towns and counties
    logger.info("Starting to scrape Connecticut towns and counties...")
    towns_counties = scraper.scrape_towns_and_counties()

    if not towns_counties:
        logger.error("No towns data was scraped")
        return False

    logger.info(f"Successfully scraped {len(towns_counties)} towns")

    # Clear existing data in ct_towns table
    try:
        logger.info("Clearing existing data in ct_towns table...")
        response = db.client.table('ct_towns').delete().neq('id', 0).execute()
        logger.info("Existing data cleared")
    except Exception as e:
        logger.warning(f"Error clearing existing data (table might be empty): {e}")

    # Insert towns into database
    success_count = 0
    error_count = 0

    for town, county in towns_counties:
        try:
            # Prepare town data
            town_data = {
                'name': town,
                'county': county
            }

            # Insert into database
            response = db.client.table('ct_towns').insert(town_data).execute()

            if response.data:
                success_count += 1
                logger.debug(f"Inserted: {town} - {county} County")
            else:
                error_count += 1
                logger.error(f"Failed to insert: {town}")

        except Exception as e:
            error_count += 1
            logger.error(f"Error inserting {town}: {e}")

    # Report results
    logger.info("=" * 50)
    logger.info("Population Complete!")
    logger.info(f"✓ Successfully inserted: {success_count} towns")
    if error_count > 0:
        logger.warning(f"✗ Failed to insert: {error_count} towns")

    # Verify by fetching count
    try:
        response = db.client.table('ct_towns').select('*', count='exact').execute()
        total_in_db = response.count if hasattr(response, 'count') else len(response.data)
        logger.info(f"Total towns now in database: {total_in_db}")

        # Show sample data
        if response.data and len(response.data) > 0:
            logger.info("\nSample of inserted data:")
            for town in response.data[:5]:
                logger.info(f"  - {town.get('name')} ({town.get('county')} County)")

    except Exception as e:
        logger.error(f"Error verifying data: {e}")

    return success_count > 0


if __name__ == "__main__":
    logger.info("Starting Connecticut Towns Database Population")
    logger.info("=" * 50)

    success = populate_ct_towns()

    if success:
        logger.info("\n✅ Population completed successfully!")
    else:
        logger.error("\n❌ Population failed!")
        sys.exit(1)
