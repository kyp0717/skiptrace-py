use csv::Writer;
use std::error::Error;
use std::fs::File;

#[derive(Debug, Clone)]
pub struct Case {
    pub name: String,
    pub docket: String,
    pub defendant: String,
    pub property_address: String,
    pub phone_numbers: Vec<String>,
}

impl Case {
    pub fn new(name: String, docket: String) -> Self {
        Self {
            name,
            docket,
            defendant: String::new(),
            property_address: String::new(),
            phone_numbers: Vec::new(),
        }
    }

    pub fn to_csv_record(&self) -> Vec<String> {
        vec![
            self.name.clone(),
            self.docket.clone(),
            self.defendant.clone(),
            self.property_address.clone(),
            self.phone_numbers.join("; "),
        ]
    }
}

pub fn save_cases_to_csv(cases: &[Case], filename: &str) -> Result<(), Box<dyn Error>> {
    let file = File::create(filename)?;
    let mut wtr = Writer::from_writer(file);

    // Write header
    wtr.write_record(&["Name", "Docket", "Defendant", "Property Address", "Phone Numbers"])?;

    // Write case records
    for case in cases {
        wtr.write_record(&case.to_csv_record())?;
    }

    wtr.flush()?;
    Ok(())
}
