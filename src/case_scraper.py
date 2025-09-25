import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import csv
from site_connector import SiteConnector
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class CaseScraper:
    def __init__(self, town):
        self.town = town
        self.url = "https://civilinquiry.jud.ct.gov/PropertyAddressSearch.aspx"
        self.connector = SiteConnector(self.url)
        self.driver = None

    def scrape_cases(self):
        """
        Scrape the case information for a given town.
        """
        self.driver = self.connector.connect()
        if not self.driver:
            print("Failed to connect to the website")
            return []

        try:
            print(f"Connected to: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Find the town input field and enter the town name
            town_input = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtCityTown")
            town_input.send_keys(self.town)
            print(f"Entered town: {self.town}")

            # Find and click the submit button
            submit_button = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSubmit")
            submit_button.click()
            print("Clicked submit button")

            # Wait for the page to load and get the page source
            import time
            time.sleep(5)  # Give more time for results to load
            page_source = self.driver.page_source

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            cases = []
            table = soup.find('table', id='ctl00_ContentPlaceHolder1_gvPropertyResults')
            if not table:
                print("No results table found")
                # Try to find any error messages
                error_msg = soup.find('span', id='ctl00_ContentPlaceHolder1_lblMessage')
                if error_msg:
                    print(f"Error message: {error_msg.text}")
                return []

            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue

                case_name = cells[3].text.strip()
                defendant = case_name.split(' v. ')[-1]

                docket_number_cell = cells[4]
                docket_number = docket_number_cell.text.strip()
                docket_link = docket_number_cell.find('a')
                docket_url = docket_link['href'] if docket_link else ''

                case = {
                    'case_name': case_name,
                    'docket_number': docket_number,
                    'docket_url': f"https://civilinquiry.jud.ct.gov/{docket_url}",
                    'address': cells[1].text.strip(),
                    'defendant': defendant
                }
                cases.append(case)
            
            return cases

        except Exception as e:
            print(f"An error occurred while scraping: {e}")
            return []
        finally:
            self.connector.close()
    
    def save_to_csv(self, cases, filename=None):
        """
        Save scraped cases to a CSV file.
        """
        if not filename:
            filename = f"cases_{self.town.lower().replace(' ', '_')}.csv"
        
        if not cases:
            print(f"No cases to save to {filename}")
            return filename
        
        # Define CSV headers
        fieldnames = ['case_name', 'defendant', 'address', 'docket_number', 'docket_url']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for case in cases:
                    writer.writerow(case)
            print(f"Successfully saved {len(cases)} cases to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
        
        return filename

if __name__ == '__main__':
    # Example usage
    town = "Middletown"
    scraper = CaseScraper(town)
    cases = scraper.scrape_cases()
    if cases:
        print(f"Found {len(cases)} cases for {town}:")
        for case in cases[:3]:  # Show first 3 cases
            print(case)
        # Save to CSV
        csv_filename = scraper.save_to_csv(cases)
        print(f"Results saved to: {csv_filename}")
    else:
        print(f"No cases found for {town}.")