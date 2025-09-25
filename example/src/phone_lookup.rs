use serde::{Deserialize, Serialize};
use std::error::Error;
use std::thread;
use std::time::Duration;
use thirtyfour::{By, WebDriver};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhoneResult {
    pub name: String,
    pub address: String,
    pub phone_numbers: Vec<String>,
}

pub struct PhoneLookup {
    driver: WebDriver,
    rate_limit_delay: Duration,
}

impl PhoneLookup {
    pub async fn new(driver: WebDriver) -> Result<Self, Box<dyn Error + Send + Sync>> {
        Ok(Self {
            driver,
            rate_limit_delay: Duration::from_secs(2),
        })
    }

    pub async fn search_phone_number(
        &self,
        name: &str,
        address: &str,
    ) -> Result<Vec<PhoneResult>, Box<dyn Error + Send + Sync>> {
        thread::sleep(self.rate_limit_delay);

        let search_url = self.build_search_url(name, address);
        self.driver.goto(&search_url).await?;

        thread::sleep(Duration::from_secs(3));

        let results = self.extract_phone_results().await?;

        Ok(results)
    }

    pub fn build_search_url(&self, name: &str, address: &str) -> String {
        let name_parts: Vec<&str> = name.split_whitespace().collect();
        let (first_name, last_name) = if name_parts.len() >= 2 {
            (name_parts[0], name_parts[name_parts.len() - 1])
        } else if name_parts.len() == 1 {
            (name_parts[0], "")
        } else {
            ("", "")
        };

        let address_parts: Vec<&str> = address.split(',').collect();
        let city = if address_parts.len() >= 2 {
            address_parts[address_parts.len() - 2].trim()
        } else {
            ""
        };

        let state = if address_parts.len() >= 1 {
            let last_part = address_parts[address_parts.len() - 1].trim();
            last_part.split_whitespace().next().unwrap_or("CT")
        } else {
            "CT"
        };

        format!(
            "https://www.truepeoplesearch.com/results?name={} {}&citystatezip={}, {}",
            first_name, last_name, city, state
        )
    }

    async fn extract_phone_results(&self) -> Result<Vec<PhoneResult>, Box<dyn Error + Send + Sync>> {
        let mut results = Vec::new();

        let result_elements = self
            .driver
            .find_all(By::ClassName("search-result"))
            .await
            .unwrap_or_default();

        for (index, element) in result_elements.iter().take(5).enumerate() {
            let name = match element.find(By::ClassName("h4")).await {
                Ok(el) => el.text().await.unwrap_or_default(),
                Err(_) => String::new(),
            };

            let address = match element
                .find(By::XPath(".//div[@data-label='Current Address']//span[@itemprop='address']"))
                .await
            {
                Ok(el) => el.text().await.unwrap_or_default(),
                Err(_) => String::new(),
            };

            let phone_elements = element
                .find_all(By::XPath(".//div[@data-label='Phone Numbers']//a[@href^='tel:']"))
                .await
                .unwrap_or_default();

            let mut phone_numbers = Vec::new();
            for phone_el in phone_elements {
                if let Ok(phone) = phone_el.text().await {
                    phone_numbers.push(phone);
                }
            }

            if !phone_numbers.is_empty() {
                results.push(PhoneResult {
                    name,
                    address,
                    phone_numbers,
                });
            }
        }

        Ok(results)
    }

    pub fn set_rate_limit(&mut self, seconds: u64) {
        self.rate_limit_delay = Duration::from_secs(seconds);
    }
}