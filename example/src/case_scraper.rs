use crate::case::Case;
use scraper::{Html, Selector};
use std::error::Error;
use thirtyfour::prelude::*;

pub struct CaseScraper {
    driver: WebDriver,
}

pub struct SearchBuilder {
    driver: WebDriver,
    town: String,
}

impl CaseScraper {
    pub fn new(driver: WebDriver) -> Self {
        Self { driver }
    }

    pub fn search_by_town(self, town: &str) -> SearchBuilder {
        SearchBuilder {
            driver: self.driver,
            town: town.to_string(),
        }
    }
}

impl SearchBuilder {
    pub async fn extract_cases(self) -> Result<Vec<Case>, Box<dyn Error + Send + Sync>> {
        // Navigate to the search page
        let site = "https://civilinquiry.jud.ct.gov/PropertyAddressSearch.aspx";
        self.driver.goto(site).await?;

        // Enter city name
        self.driver
            .find(By::Id("ctl00_ContentPlaceHolder1_txtCityTown"))
            .await?
            .send_keys(&self.town)
            .await?;

        // Click search button
        self.driver
            .find(By::Id("ctl00_ContentPlaceHolder1_btnSubmit"))
            .await?
            .click()
            .await?;

        // Wait for the table to appear
        let table_id = "ctl00_ContentPlaceHolder1_gvPropertyResults";
        self.driver.query(By::Id(table_id)).first().await?;

        // Get updated page HTML
        let html = self.driver.source().await?;

        // Extract cases from the search results
        let mut cases = Vec::new();
        if let Some(table_html) = Self::get_html_table(&html, table_id) {
            cases = Self::extract_cases_from_html(&table_html);
        }

        // Enhance each case with detailed information
        let site_case =
            "https://civilinquiry.jud.ct.gov/CaseDetail/PublicCaseDetail.aspx?DocketNo=";

        for case in &mut cases {
            let docket_cleaned = case.docket.replace("-", "");
            let case_url = format!("{}{}", site_case, docket_cleaned);

            self.driver.goto(&case_url).await?;
            self.driver
                .query(By::Id("ctl00_tblContent"))
                .first()
                .await?;

            let case_html = self.driver.source().await?;
            let doc = Html::parse_document(&case_html);

            if let Some(defendant) = Self::get_defendant(&doc) {
                case.defendant = defendant;
            }

            if let Some(property_address) = Self::get_property_address(&doc) {
                case.property_address = property_address;
            }
        }

        Ok(cases)
    }

    fn get_html_table(html: &str, table_id: &str) -> Option<String> {
        let doc = Html::parse_document(html);
        let selector = Selector::parse(&format!(r#"table[id="{}"]"#, table_id)).ok()?;
        let table_element = doc.select(&selector).next()?;
        Some(table_element.html())
    }

    fn extract_cases_from_html(html: &str) -> Vec<Case> {
        let mut cases = Vec::new();
        let doc = Html::parse_document(html);

        let row_selector = Selector::parse(r#"tr"#).unwrap();
        let td_selector = Selector::parse("td").unwrap();
        let a_selector = Selector::parse("a").unwrap();

        for row in doc.select(&row_selector) {
            let tds: Vec<_> = row.select(&td_selector).collect();

            if tds.len() >= 5 {
                let name = tds[3].text().collect::<String>().trim().to_string();
                let docket_link = tds[4].select(&a_selector).next();

                if let Some(link) = docket_link {
                    let docket = link.text().collect::<String>().trim().to_string();
                    cases.push(Case {
                        name,
                        docket,
                        defendant: String::new(),
                        property_address: String::new(),
                        phone_numbers: Vec::new(),
                    });
                }
            }
        }

        cases
    }

    fn get_defendant(doc: &Html) -> Option<String> {
        let selector = Selector::parse(
            r#"span#ctl00_ContentPlaceHolder1_CaseDetailParties1_gvParties_ctl05_lblPtyPartyName"#,
        )
        .ok()?;

        doc.select(&selector)
            .next()
            .map(|el| el.text().collect::<String>().trim().to_string())
    }

    fn get_property_address(doc: &Html) -> Option<String> {
        let selector = Selector::parse(
            r#"span#ctl00_ContentPlaceHolder1_CaseDetailBasicInfo1_lblPropertyAddress"#,
        )
        .ok()?;

        doc.select(&selector)
            .next()
            .map(|el| el.text().collect::<String>().trim().to_string())
    }
}
