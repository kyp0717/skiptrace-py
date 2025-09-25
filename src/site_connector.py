
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class SiteConnector:
    def __init__(self, url):
        self.url = url
        self.driver = None

    def connect(self):
        """
        Connect to the specified URL using Selenium.
        """
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            service = ChromeService(executable_path=ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.get(self.url)
            return self.driver
        except Exception as e:
            print(f"An error occurred while trying to connect to the URL: {e}")
            return None

    def close(self):
        """
        Close the browser.
        """
        if self.driver:
            self.driver.quit()

if __name__ == '__main__':
    # Example usage
    url = "https://civilinquiry.jud.ct.gov/PropertyAddressSearch.aspx"
    connector = SiteConnector(url)
    driver = connector.connect()
    if driver:
        print("Successfully connected to the website.")
        # You can now interact with the website using the driver object
        # For example, you can get the title of the page
        print(f"Page title: {driver.title}")
        connector.close()
