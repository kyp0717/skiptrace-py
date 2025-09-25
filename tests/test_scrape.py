
import unittest
from src.site_connector import SiteConnector

class TestSiteConnector(unittest.TestCase):

    def test_connection(self):
        """
        Test the connection to the website.
        """
        url = "https://civilinquiry.jud.ct.gov/PropertyAddressSearch.aspx"
        connector = SiteConnector(url)
        driver = connector.connect()

        self.assertIsNotNone(driver, "Driver should not be None")
        self.assertEqual(driver.title, "Property Address Search")

        connector.close()

if __name__ == '__main__':
    unittest.main()
