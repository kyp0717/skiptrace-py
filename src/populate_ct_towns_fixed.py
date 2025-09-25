"""
Populate Connecticut Towns table with correct data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connector import DatabaseConnector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Complete Connecticut towns and counties data
CONNECTICUT_TOWNS = [
    # Fairfield County
    ("Bethel", "Fairfield"),
    ("Bridgeport", "Fairfield"),
    ("Brookfield", "Fairfield"),
    ("Danbury", "Fairfield"),
    ("Darien", "Fairfield"),
    ("Easton", "Fairfield"),
    ("Fairfield", "Fairfield"),
    ("Greenwich", "Fairfield"),
    ("Monroe", "Fairfield"),
    ("New Canaan", "Fairfield"),
    ("New Fairfield", "Fairfield"),
    ("Newtown", "Fairfield"),
    ("Norwalk", "Fairfield"),
    ("Redding", "Fairfield"),
    ("Ridgefield", "Fairfield"),
    ("Shelton", "Fairfield"),
    ("Sherman", "Fairfield"),
    ("Stamford", "Fairfield"),
    ("Stratford", "Fairfield"),
    ("Trumbull", "Fairfield"),
    ("Weston", "Fairfield"),
    ("Westport", "Fairfield"),
    ("Wilton", "Fairfield"),
    
    # Hartford County
    ("Avon", "Hartford"),
    ("Berlin", "Hartford"),
    ("Bloomfield", "Hartford"),
    ("Bristol", "Hartford"),
    ("Burlington", "Hartford"),
    ("Canton", "Hartford"),
    ("East Granby", "Hartford"),
    ("East Hartford", "Hartford"),
    ("East Windsor", "Hartford"),
    ("Enfield", "Hartford"),
    ("Farmington", "Hartford"),
    ("Glastonbury", "Hartford"),
    ("Granby", "Hartford"),
    ("Hartford", "Hartford"),
    ("Hartland", "Hartford"),
    ("Manchester", "Hartford"),
    ("Marlborough", "Hartford"),
    ("New Britain", "Hartford"),
    ("Newington", "Hartford"),
    ("Plainville", "Hartford"),
    ("Rocky Hill", "Hartford"),
    ("Simsbury", "Hartford"),
    ("South Windsor", "Hartford"),
    ("Southington", "Hartford"),
    ("Suffield", "Hartford"),
    ("West Hartford", "Hartford"),
    ("Wethersfield", "Hartford"),
    ("Windsor", "Hartford"),
    ("Windsor Locks", "Hartford"),
    
    # Litchfield County
    ("Barkhamsted", "Litchfield"),
    ("Bethlehem", "Litchfield"),
    ("Bridgewater", "Litchfield"),
    ("Canaan", "Litchfield"),
    ("Colebrook", "Litchfield"),
    ("Cornwall", "Litchfield"),
    ("Goshen", "Litchfield"),
    ("Harwinton", "Litchfield"),
    ("Kent", "Litchfield"),
    ("Litchfield", "Litchfield"),
    ("Morris", "Litchfield"),
    ("New Hartford", "Litchfield"),
    ("New Milford", "Litchfield"),
    ("Norfolk", "Litchfield"),
    ("North Canaan", "Litchfield"),
    ("Plymouth", "Litchfield"),
    ("Roxbury", "Litchfield"),
    ("Salisbury", "Litchfield"),
    ("Sharon", "Litchfield"),
    ("Thomaston", "Litchfield"),
    ("Torrington", "Litchfield"),
    ("Warren", "Litchfield"),
    ("Washington", "Litchfield"),
    ("Watertown", "Litchfield"),
    ("Winchester", "Litchfield"),
    ("Woodbury", "Litchfield"),
    
    # Middlesex County
    ("Chester", "Middlesex"),
    ("Clinton", "Middlesex"),
    ("Cromwell", "Middlesex"),
    ("Deep River", "Middlesex"),
    ("Durham", "Middlesex"),
    ("East Haddam", "Middlesex"),
    ("East Hampton", "Middlesex"),
    ("Essex", "Middlesex"),
    ("Haddam", "Middlesex"),
    ("Killingworth", "Middlesex"),
    ("Middlefield", "Middlesex"),
    ("Middletown", "Middlesex"),
    ("Old Saybrook", "Middlesex"),
    ("Portland", "Middlesex"),
    ("Westbrook", "Middlesex"),
    
    # New Haven County
    ("Ansonia", "New Haven"),
    ("Beacon Falls", "New Haven"),
    ("Bethany", "New Haven"),
    ("Branford", "New Haven"),
    ("Cheshire", "New Haven"),
    ("Derby", "New Haven"),
    ("East Haven", "New Haven"),
    ("Guilford", "New Haven"),
    ("Hamden", "New Haven"),
    ("Madison", "New Haven"),
    ("Meriden", "New Haven"),
    ("Middlebury", "New Haven"),
    ("Milford", "New Haven"),
    ("Naugatuck", "New Haven"),
    ("New Haven", "New Haven"),
    ("North Branford", "New Haven"),
    ("North Haven", "New Haven"),
    ("Orange", "New Haven"),
    ("Oxford", "New Haven"),
    ("Prospect", "New Haven"),
    ("Seymour", "New Haven"),
    ("Southbury", "New Haven"),
    ("Wallingford", "New Haven"),
    ("Waterbury", "New Haven"),
    ("West Haven", "New Haven"),
    ("Wolcott", "New Haven"),
    ("Woodbridge", "New Haven"),
    
    # New London County
    ("Bozrah", "New London"),
    ("Colchester", "New London"),
    ("East Lyme", "New London"),
    ("Franklin", "New London"),
    ("Griswold", "New London"),
    ("Groton", "New London"),
    ("Lebanon", "New London"),
    ("Ledyard", "New London"),
    ("Lisbon", "New London"),
    ("Lyme", "New London"),
    ("Montville", "New London"),
    ("New London", "New London"),
    ("North Stonington", "New London"),
    ("Norwich", "New London"),
    ("Old Lyme", "New London"),
    ("Preston", "New London"),
    ("Salem", "New London"),
    ("Sprague", "New London"),
    ("Stonington", "New London"),
    ("Voluntown", "New London"),
    ("Waterford", "New London"),
    
    # Tolland County
    ("Andover", "Tolland"),
    ("Bolton", "Tolland"),
    ("Columbia", "Tolland"),
    ("Coventry", "Tolland"),
    ("Ellington", "Tolland"),
    ("Hebron", "Tolland"),
    ("Mansfield", "Tolland"),
    ("Somers", "Tolland"),
    ("Stafford", "Tolland"),
    ("Tolland", "Tolland"),
    ("Union", "Tolland"),
    ("Vernon", "Tolland"),
    ("Willington", "Tolland"),
    
    # Windham County
    ("Ashford", "Windham"),
    ("Brooklyn", "Windham"),
    ("Canterbury", "Windham"),
    ("Chaplin", "Windham"),
    ("Eastford", "Windham"),
    ("Hampton", "Windham"),
    ("Killingly", "Windham"),
    ("Plainfield", "Windham"),
    ("Pomfret", "Windham"),
    ("Putnam", "Windham"),
    ("Scotland", "Windham"),
    ("Sterling", "Windham"),
    ("Thompson", "Windham"),
    ("Windham", "Windham"),
    ("Woodstock", "Windham"),
]

def main():
    logger.info("Starting Connecticut Towns Population")
    logger.info("=" * 50)
    
    # Initialize database
    db = DatabaseConnector()
    
    if not db.test_connection():
        logger.error("Failed to connect to database")
        return False
    
    # Clear existing data
    try:
        logger.info("Clearing existing data...")
        response = db.client.table('ct_towns').delete().neq('id', 0).execute()
    except Exception as e:
        logger.warning(f"Could not clear existing data: {e}")
    
    # Insert all towns
    success_count = 0
    error_count = 0
    
    for town_name, county in CONNECTICUT_TOWNS:
        try:
            data = {
                'town': town_name,
                'county': county
            }
            
            response = db.client.table('ct_towns').insert(data).execute()
            
            if response.data:
                success_count += 1
                logger.debug(f"Inserted: {town_name}, {county} County")
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to insert {town_name}: {e}")
    
    logger.info("=" * 50)
    logger.info(f"✓ Successfully inserted: {success_count} towns")
    if error_count > 0:
        logger.warning(f"✗ Failed: {error_count} towns")
    
    # Verify
    try:
        response = db.client.table('ct_towns').select('*').execute()
        logger.info(f"Total towns in database: {len(response.data)}")
        
        # Show sample
        if response.data:
            logger.info("\nSample data:")
            for town in response.data[:5]:
                logger.info(f"  - {town['town']}, {town['county']} County")
    except Exception as e:
        logger.error(f"Error verifying: {e}")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Population completed successfully!")
    else:
        print("\n❌ Population failed!")
        sys.exit(1)
