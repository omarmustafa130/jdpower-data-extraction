import csv
import argparse
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Define input and output CSV files
input_csv_files = {
    #"cars": "cars_makes_and_years.csv",
    #"rvs": "rvs_makes_and_years.csv",
    "boats": "boats_makes_and_years.csv",
    #"motorcycles": "motorcycles_makes_and_years.csv",
}
output_csv = "year_make_model_trim.csv"

# Base URL patterns for different vehicle types
base_urls = {
    "cars": "https://www.jdpower.com/cars/{year}/{make}",
    "rvs": "https://www.jdpower.com/rvs/{year}/{make}",
    "boats": "https://www.jdpower.com/boats/{year}/{make}",
    "motorcycles": "https://www.jdpower.com/motorcycles/{year}/{make}",
}

# Function to fetch data
def fetch_data(selected_years):
    with sync_playwright() as p:
        # Launch Firefox with stealth mode
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Apply stealth mode
        stealth_sync(page)

        # Open output CSV and write a header (if not already existing)
        try:
            with open(output_csv, mode="x", newline="", encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow(["Year", "Vehicle Type", "Make", "Model", "Trim"])  # Write header
        except FileExistsError:
            print(f"File '{output_csv}' already exists. Appending to it.")

        # Iterate through each vehicle type
        for vehicle_type, input_csv in input_csv_files.items():
            print(f"Processing {vehicle_type} from {input_csv}...")
            # Read the corresponding input CSV
            with open(input_csv, mode="r", encoding="utf-8") as input_file:
                reader = csv.reader(input_file)
                next(reader)  # Skip the header row

                for row in reader:
                    make = row[0].replace(' ', '-').replace('/', '-')
                    years = row[1].split(", ")  # Split available years

                    # Check if the make matches the selected years
                    if not any(year in years for year in selected_years):
                        continue

                    print(f"Processing {make} for years {selected_years} ({vehicle_type})...")

                    # Construct the URL for the make
                    for year in selected_years:
                        make_url = base_urls[vehicle_type].format(year=year, make=make.lower())
                        page.goto(make_url)

                        try:
                            # General handling for boats
                            page.wait_for_selector(".yearMake_model-wrapper__t8GAv", timeout=10000)

                            # Get all model names
                            model_elements = page.query_selector_all(".yearMake_model-wrapper-h3__npC2B h3")
                            for model_element in model_elements:
                                model_name = model_element.inner_text().strip()
                                print(f"Fetching trims for model: {model_name} ({vehicle_type})...")

                                with context.expect_page() as new_tab_event:
                                    model_url = model_element.evaluate(
                                        "node => node.closest('.yearMake_model-wrapper__t8GAv').querySelector('a').href"
                                    )
                                    page.evaluate(f"window.open('{model_url}', '_blank')")

                                new_tab = new_tab_event.value
                                new_tab.wait_for_load_state()

                                try:
                                    new_tab.wait_for_selector(".trimSelection_image-card__GS7Sd", timeout=10000)
                                    trims = new_tab.query_selector_all(".trimSelection_card-info__O02As h3")
                                    for trim in trims:
                                        trim_name = trim.inner_text().strip()
                                        print(f"Found trim: {trim_name}")

                                        # Append to the output CSV file
                                        with open(output_csv, mode="a", newline="", encoding="utf-8") as output_file:
                                            writer = csv.writer(output_file)
                                            writer.writerow([year, vehicle_type, make, model_name, trim_name])

                                except Exception as e:
                                    print(f"Error fetching trims for {model_name} ({vehicle_type}): {e}")

                                finally:
                                    # Close the new tab and return to the main page
                                    new_tab.close()

                        except Exception as e:
                            print(f"Error processing {make} ({vehicle_type}): {e}")

        browser.close()
        print(f"Data appended to {output_csv}.")

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape vehicle data from JDPower.")
    parser.add_argument(
        "--years",
        type=str,
        required=True,
        help="Specify a single year (e.g., 2025) or a range of years (e.g., 2020-2025)."
    )
    args = parser.parse_args()

    # Process the year or range of years
    if "-" in args.years:
        start_year, end_year = map(int, args.years.split("-"))
        selected_years = list(map(str, range(start_year, end_year + 1)))
    else:
        selected_years = [args.years]

    return selected_years

# Run the function
if __name__ == "__main__":
    selected_years = parse_arguments()
    fetch_data(selected_years)
