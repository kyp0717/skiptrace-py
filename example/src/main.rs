mod case;
mod case_scraper;
mod phone_lookup;

use case::save_cases_to_csv;
use case_scraper::CaseScraper;
use phone_lookup::PhoneLookup;
use std::error::Error;
use thirtyfour::prelude::*;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync>> {
    let caps = DesiredCapabilities::chrome();
    // caps.add_arg("--headless=new")?; // enable in headless mode
    let port = "46107";
    let driver_path = format!("http://localhost:{}", port);

    let driver = WebDriver::new(driver_path, caps).await?;

    // Use the new fluent API
    let mut cases = CaseScraper::new(driver.clone())
        .search_by_town("Middletown")
        .extract_cases()
        .await?;

    // Initialize phone lookup
    // let phone_lookup = PhoneLookup::new(driver.clone()).await?;

    // Look up phone numbers for each case

    // Save results to CSV
    if let Err(e) = save_cases_to_csv(&cases, "./output/cases.csv") {
        eprintln!("Error saving cases to CSV: {}", e);
    } else {
        println!("Cases saved to ./output/cases.csv");
    }

    // Print the cases for verification
    for case in &cases {
        println!(
            "Name: {}, Docket: {}, Defendant: {}, Property Address: {}, Phone Numbers: {}",
            case.name,
            case.docket,
            case.defendant,
            case.property_address,
            if case.phone_numbers.is_empty() {
                "None".to_string()
            } else {
                case.phone_numbers.join(", ")
            }
        );
    }

    Ok(())
}
