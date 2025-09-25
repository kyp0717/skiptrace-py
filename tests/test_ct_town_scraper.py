#!/usr/bin/env python3
"""
Unit tests for Connecticut Town and County Scraper
"""

import unittest
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ct_town_scraper import CTTownScraper


class TestCTTownScraper(unittest.TestCase):
    """Test cases for CTTownScraper"""

    def setUp(self):
        """Set up test fixtures"""
        self.scraper = CTTownScraper()

    def test_scraper_initialization(self):
        """Test that scraper initializes correctly"""
        self.assertEqual(self.scraper.url, "https://libguides.ctstatelibrary.org/cttowns")
        self.assertEqual(self.scraper.towns_data, [])

    def test_clean_town_name(self):
        """Test town name cleaning function"""
        # Test various formats
        self.assertEqual(self.scraper._clean_town_name("Hartford"), "Hartford")
        self.assertEqual(self.scraper._clean_town_name("  Hartford  "), "Hartford")
        self.assertEqual(self.scraper._clean_town_name("Hartford (town)"), "Hartford")
        self.assertEqual(self.scraper._clean_town_name("City of Hartford"), "Hartford")
        self.assertEqual(self.scraper._clean_town_name("Hartford,"), "Hartford")

    def test_hardcoded_data_fallback(self):
        """Test that hardcoded data is available as fallback"""
        towns_data = self.scraper._get_hardcoded_ct_towns()

        # Connecticut has 169 towns
        self.assertEqual(len(towns_data), 169)

        # Check that data is in correct format
        for town, county in towns_data:
            self.assertIsInstance(town, str)
            self.assertIsInstance(county, str)
            self.assertTrue(len(town) > 0)
            self.assertTrue(len(county) > 0)

        # Check for known towns
        town_names = [t for t, c in towns_data]
        self.assertIn("Hartford", town_names)
        self.assertIn("Middletown", town_names)
        self.assertIn("New Haven", town_names)

    def test_get_all_counties(self):
        """Test getting all counties"""
        # Use hardcoded data for consistent testing
        self.scraper.towns_data = self.scraper._get_hardcoded_ct_towns()
        counties = self.scraper.get_all_counties()

        # Connecticut has 8 counties
        self.assertEqual(len(counties), 8)

        expected_counties = ['Fairfield', 'Hartford', 'Litchfield', 'Middlesex',
                           'New Haven', 'New London', 'Tolland', 'Windham']
        self.assertEqual(sorted(counties), sorted(expected_counties))

    def test_validate_town(self):
        """Test town validation"""
        # Use hardcoded data for consistent testing
        self.scraper.towns_data = self.scraper._get_hardcoded_ct_towns()

        # Valid towns
        self.assertTrue(self.scraper.validate_town("Hartford"))
        self.assertTrue(self.scraper.validate_town("Middletown"))
        self.assertTrue(self.scraper.validate_town("middletown"))  # Case insensitive
        self.assertTrue(self.scraper.validate_town("  Middletown  "))  # With spaces

        # Invalid towns
        self.assertFalse(self.scraper.validate_town("Boston"))  # Massachusetts town
        self.assertFalse(self.scraper.validate_town("InvalidTown"))
        self.assertFalse(self.scraper.validate_town(""))

    def test_get_county_for_town(self):
        """Test getting county for a specific town"""
        # Use hardcoded data for consistent testing
        self.scraper.towns_data = self.scraper._get_hardcoded_ct_towns()

        # Test known town-county pairs
        self.assertEqual(self.scraper.get_county_for_town("Hartford"), "Hartford")
        self.assertEqual(self.scraper.get_county_for_town("Middletown"), "Middlesex")
        self.assertEqual(self.scraper.get_county_for_town("New Haven"), "New Haven")
        self.assertEqual(self.scraper.get_county_for_town("Stamford"), "Fairfield")

        # Test case insensitive
        self.assertEqual(self.scraper.get_county_for_town("hartford"), "Hartford")

        # Test invalid town
        self.assertIsNone(self.scraper.get_county_for_town("Boston"))

    def test_get_towns_by_county(self):
        """Test getting all towns in a specific county"""
        # Use hardcoded data for consistent testing
        self.scraper.towns_data = self.scraper._get_hardcoded_ct_towns()

        # Test Middlesex County
        middlesex_towns = self.scraper.get_towns_by_county("Middlesex")
        self.assertEqual(len(middlesex_towns), 15)  # Middlesex has 15 towns
        self.assertIn("Middletown", middlesex_towns)
        self.assertIn("Chester", middlesex_towns)

        # Test case insensitive
        middlesex_towns_lower = self.scraper.get_towns_by_county("middlesex")
        self.assertEqual(len(middlesex_towns_lower), 15)

        # Test invalid county
        invalid_county = self.scraper.get_towns_by_county("InvalidCounty")
        self.assertEqual(len(invalid_county), 0)

    def test_scrape_towns_and_counties(self):
        """Test the main scraping function"""
        # This test will either scrape from the website or use hardcoded data
        towns_data = self.scraper.scrape_towns_and_counties()

        # Should return 169 towns
        self.assertEqual(len(towns_data), 169)

        # Check format
        for town, county in towns_data:
            self.assertIsInstance(town, str)
            self.assertIsInstance(county, str)
            self.assertTrue(len(town) > 0)
            self.assertTrue(len(county) > 0)

        # After scraping, internal data should be populated
        self.assertEqual(len(self.scraper.towns_data), 169)

    def test_data_consistency(self):
        """Test that all data methods are consistent"""
        self.scraper.towns_data = self.scraper._get_hardcoded_ct_towns()

        # Get all counties
        counties = self.scraper.get_all_counties()

        # Count total towns by summing towns in each county
        total_towns = 0
        for county in counties:
            towns_in_county = self.scraper.get_towns_by_county(county)
            total_towns += len(towns_in_county)

        # Should equal total number of towns
        self.assertEqual(total_towns, 169)


def run_tests():
    """Run all tests with colored output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCTTownScraper)

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print colored summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ \033[92mALL TESTS PASSED\033[0m")
    else:
        print("❌ \033[91mSOME TESTS FAILED\033[0m")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("="*60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)