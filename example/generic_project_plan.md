
# Project plan 

## AI Directive
1. Create comprehensive project plan (if not already exisit)
2. If project plan already exist, modify and update as work progress.
3. Modify and update tasks.md as needed as project progess.
4. Utilize sub agents for specific tasks

## Goal
- Build a web scraper in rust.
- First the web scraper will scrape a civil inquiry site from Connecticut Judiciary to get a list of court cases with docket number by town.
- Use the docket number to scrape the for the defendant name and address 
- Once the name and address and discovered, the name and address will be use to search for phone number in a people search site
- Finally, return the name and phone numbers.

## Phase 1 Requirement
- Implement web scrape for case docket number from Connecticut Judicial Site 
   1. Implement case struct with the `case.rs` file
   2. Create a file call `court_case_scraper.rs` (rename `scraper.rs` to this new name)
     * implement CaseScraper struct 

## Phase 2 
1.  Search for phone number from this site:
  - `https://www.truepeoplesearch.com/`
2.  Implement web scrape to extract phone number base on defendant's name and address
  - Create another file call `phone_lookup.rs` 
  - Implement the PhoneLookup struct similar to the CaseScraper struct.
3.  Multiple phone numbers may be associated with each person.  App must be able to store up to 4 phone numbers connected to an individual.


## Phase 3 Test
