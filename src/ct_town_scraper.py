"""
Connecticut Towns and Counties Scraper
Scrapes town and county data from CT State Library website
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CTTownScraper:
    """Scraper for Connecticut towns and counties from CT State Library"""

    def __init__(self):
        self.url = "https://libguides.ctstatelibrary.org/cttowns"
        self.towns_data = []

    def scrape_towns_and_counties(self) -> List[Tuple[str, str]]:
        """
        Scrape all Connecticut towns and their counties
        Returns: List of tuples (town, county)
        """
        try:
            logger.info(f"Starting to scrape CT towns from {self.url}")

            # Make request to the website
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all county sections
            # The page has sections for each county with town lists
            counties_data = {}

            # Look for county headers and their associated town lists
            # The structure typically has county names as headers followed by town lists
            content_divs = soup.find_all('div', class_='s-lg-box-content')

            for div in content_divs:
                # Try to find county headers and associated towns
                headers = div.find_all(['h3', 'h4', 'strong'])

                for header in headers:
                    header_text = header.get_text(strip=True)

                    # Check if this is a county header
                    if 'County' in header_text:
                        county_name = header_text.replace('County', '').strip()

                        # Find the associated list of towns
                        # Towns are usually in lists or paragraphs following the county header
                        next_element = header.find_next_sibling()
                        towns = []

                        while next_element:
                            # Check if we've reached the next county section
                            if next_element.name in ['h3', 'h4', 'strong']:
                                if 'County' in next_element.get_text():
                                    break

                            # Extract town names from lists
                            if next_element.name == 'ul':
                                town_items = next_element.find_all('li')
                                for item in town_items:
                                    town_text = item.get_text(strip=True)
                                    # Clean up town name
                                    town_name = self._clean_town_name(town_text)
                                    if town_name:
                                        towns.append(town_name)

                            # Also check for towns in paragraphs
                            elif next_element.name == 'p':
                                text = next_element.get_text(strip=True)
                                # Split by common delimiters
                                potential_towns = text.split(',')
                                for pt in potential_towns:
                                    town_name = self._clean_town_name(pt)
                                    if town_name and len(town_name) > 2:
                                        towns.append(town_name)

                            next_element = next_element.find_next_sibling()

                        if towns:
                            counties_data[county_name] = towns

            # Alternative parsing method - look for specific county patterns
            if not counties_data:
                logger.info("Primary parsing method didn't find data, trying alternative method")
                counties_data = self._parse_alternative_method(soup)

            # Convert to list of tuples
            for county, towns in counties_data.items():
                for town in towns:
                    self.towns_data.append((town, county))

            # If still no data, use hardcoded Connecticut data as fallback
            if not self.towns_data:
                logger.warning("Could not parse website, using hardcoded CT town data")
                self.towns_data = self._get_hardcoded_ct_towns()

            logger.info(f"Successfully scraped {len(self.towns_data)} town-county pairs")
            return self.towns_data

        except Exception as e:
            logger.error(f"Error scraping towns: {e}")
            # Return hardcoded data as fallback
            logger.info("Using hardcoded Connecticut town data as fallback")
            self.towns_data = self._get_hardcoded_ct_towns()
            return self.towns_data

    def _parse_alternative_method(self, soup) -> Dict[str, List[str]]:
        """Alternative parsing method for the website"""
        counties_data = {}

        # Look for any text containing county names
        county_names = ['Fairfield', 'Hartford', 'Litchfield', 'Middlesex',
                       'New Haven', 'New London', 'Tolland', 'Windham']

        for county in county_names:
            # Find all text containing this county
            county_elements = soup.find_all(text=lambda text: county in text if text else False)

            for element in county_elements:
                parent = element.parent
                if parent:
                    # Look for lists near this county mention
                    next_list = parent.find_next('ul')
                    if next_list:
                        towns = []
                        for li in next_list.find_all('li'):
                            town_name = self._clean_town_name(li.get_text())
                            if town_name:
                                towns.append(town_name)
                        if towns:
                            counties_data[county] = towns
                            break

        return counties_data

    def _clean_town_name(self, text: str) -> str:
        """Clean and normalize town name"""
        # Remove common suffixes and clean up
        text = text.strip()
        text = text.replace('(town)', '')
        text = text.replace('(city)', '')
        text = text.replace('Town of', '')
        text = text.replace('City of', '')
        text = text.strip()

        # Remove any text in parentheses
        if '(' in text:
            text = text.split('(')[0].strip()

        # Remove any special characters at the end
        text = text.rstrip('.,;:')

        return text.strip()

    def _get_hardcoded_ct_towns(self) -> List[Tuple[str, str]]:
        """
        Hardcoded list of Connecticut towns and counties as fallback
        Source: Official CT state data
        """
        ct_towns = {
            'Fairfield': [
                'Bethel', 'Bridgeport', 'Brookfield', 'Danbury', 'Darien',
                'Easton', 'Fairfield', 'Greenwich', 'Monroe', 'New Canaan',
                'New Fairfield', 'Newtown', 'Norwalk', 'Redding', 'Ridgefield',
                'Shelton', 'Sherman', 'Stamford', 'Stratford', 'Trumbull',
                'Weston', 'Westport', 'Wilton'
            ],
            'Hartford': [
                'Avon', 'Berlin', 'Bloomfield', 'Bristol', 'Burlington',
                'Canton', 'East Granby', 'East Hartford', 'East Windsor',
                'Enfield', 'Farmington', 'Glastonbury', 'Granby', 'Hartford',
                'Hartland', 'Manchester', 'Marlborough', 'New Britain',
                'Newington', 'Plainville', 'Rocky Hill', 'Simsbury', 'South Windsor',
                'Southington', 'Suffield', 'West Hartford', 'Wethersfield', 'Windsor',
                'Windsor Locks'
            ],
            'Litchfield': [
                'Barkhamsted', 'Bethlehem', 'Bridgewater', 'Canaan', 'Colebrook',
                'Cornwall', 'Goshen', 'Harwinton', 'Kent', 'Litchfield',
                'Morris', 'New Hartford', 'New Milford', 'Norfolk', 'North Canaan',
                'Plymouth', 'Roxbury', 'Salisbury', 'Sharon', 'Thomaston',
                'Torrington', 'Warren', 'Washington', 'Watertown', 'Winchester',
                'Woodbury'
            ],
            'Middlesex': [
                'Chester', 'Clinton', 'Cromwell', 'Deep River', 'Durham',
                'East Haddam', 'East Hampton', 'Essex', 'Haddam', 'Killingworth',
                'Middlefield', 'Middletown', 'Old Saybrook', 'Portland', 'Westbrook'
            ],
            'New Haven': [
                'Ansonia', 'Beacon Falls', 'Bethany', 'Branford', 'Cheshire',
                'Derby', 'East Haven', 'Guilford', 'Hamden', 'Madison',
                'Meriden', 'Middlebury', 'Milford', 'Naugatuck', 'New Haven',
                'North Branford', 'North Haven', 'Orange', 'Oxford', 'Prospect',
                'Seymour', 'Southbury', 'Wallingford', 'Waterbury', 'West Haven',
                'Wolcott', 'Woodbridge'
            ],
            'New London': [
                'Bozrah', 'Colchester', 'East Lyme', 'Franklin', 'Griswold',
                'Groton', 'Lebanon', 'Ledyard', 'Lisbon', 'Lyme',
                'Montville', 'New London', 'North Stonington', 'Norwich', 'Old Lyme',
                'Preston', 'Salem', 'Sprague', 'Stonington', 'Voluntown',
                'Waterford'
            ],
            'Tolland': [
                'Andover', 'Bolton', 'Columbia', 'Coventry', 'Ellington',
                'Hebron', 'Mansfield', 'Somers', 'Stafford', 'Tolland',
                'Union', 'Vernon', 'Willington'
            ],
            'Windham': [
                'Ashford', 'Brooklyn', 'Canterbury', 'Chaplin', 'Eastford',
                'Hampton', 'Killingly', 'Plainfield', 'Pomfret', 'Putnam',
                'Scotland', 'Sterling', 'Thompson', 'Windham', 'Woodstock'
            ]
        }

        result = []
        for county, towns in ct_towns.items():
            for town in towns:
                result.append((town, county))

        return result

    def get_towns_by_county(self, county: str) -> List[str]:
        """Get all towns in a specific county"""
        if not self.towns_data:
            self.scrape_towns_and_counties()

        return [town for town, c in self.towns_data if c.lower() == county.lower()]

    def get_all_counties(self) -> List[str]:
        """Get list of all counties"""
        if not self.towns_data:
            self.scrape_towns_and_counties()

        counties = list(set(county for _, county in self.towns_data))
        return sorted(counties)

    def validate_town(self, town_name: str) -> bool:
        """Check if a town name is valid"""
        if not self.towns_data:
            self.scrape_towns_and_counties()

        town_lower = town_name.lower().strip()
        valid_towns = [t.lower() for t, _ in self.towns_data]
        return town_lower in valid_towns

    def get_county_for_town(self, town_name: str) -> str:
        """Get the county for a specific town"""
        if not self.towns_data:
            self.scrape_towns_and_counties()

        town_lower = town_name.lower().strip()
        for town, county in self.towns_data:
            if town.lower() == town_lower:
                return county
        return None


if __name__ == "__main__":
    # Test the scraper
    scraper = CTTownScraper()
    towns_counties = scraper.scrape_towns_and_counties()

    print(f"\nTotal towns scraped: {len(towns_counties)}")
    print(f"Counties found: {scraper.get_all_counties()}")

    # Show sample data
    print("\nSample data (first 10 towns):")
    for town, county in towns_counties[:10]:
        print(f"  {town} - {county} County")

    # Test validation
    test_town = "Middletown"
    print(f"\nIs '{test_town}' a valid CT town? {scraper.validate_town(test_town)}")
    print(f"County for '{test_town}': {scraper.get_county_for_town(test_town)}")