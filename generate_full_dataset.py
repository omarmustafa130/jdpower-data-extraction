import csv
import argparse
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from openpyxl import Workbook, load_workbook

import sys
import time
# Define input and output files
input_csv_files = {
    "cars": "initial_dataset/cars_makes_and_years.csv",
    "rvs": "initial_dataset/rvs_makes_and_years.csv",
    "boats": "initial_dataset/boats_makes_and_years.csv",
    "motorcycles": "initial_dataset/motorcycles_makes_and_years.csv",
}
output_xlsx = "full_dataset/vehicle_data.xlsx"

# Base URL patterns for different vehicle types
base_urls = {
    "cars": "http://www.jdpower.com/cars/{year}/{make}",
    "rvs": "http://www.jdpower.com/rvs/{year}/{make}",
    "boats": "http://www.jdpower.com/boats/{year}/{make}",
    "motorcycles": "http://www.jdpower.com/motorcycles/{year}/{make}",
}

# Headers for different types
headers = {
    "cars": ["Year", "Vehicle Type", "Make", "Model", "Trim"],
    "rvs": ["Year", "Vehicle Type", "Make", "Model", "Trim"],
    "boats": ["Year", "Vehicle Type", "Make", "Model", "Length", "Model Type", "Hull", "CC's", "Engine(s)", "HP", "Weight (lbs)", "Fuel Type"],
    "motorcycles": ["Year", "Vehicle Type", "Make", "Model", "Trim"],
}



def validate_workbook():
    """Validate or create a new workbook."""
    if os.path.exists(output_xlsx):
        try:
            return load_workbook(output_xlsx)
        except Exception as e:
            print(f"Error loading workbook: {e}. Creating a new workbook.")
            #os.remove(output_xlsx)
    return Workbook()


def fetch_data(selected_years, selected_types):
    workbook = validate_workbook()


    sheet_map = {}

    # Initialize sheets for each selected vehicle type if not already present
    for vehicle_type in selected_types:
        if vehicle_type.capitalize() in workbook.sheetnames:
            sheet = workbook[vehicle_type.capitalize()]
        else:
            sheet = workbook.create_sheet(title=vehicle_type.capitalize())
            sheet.append(headers[vehicle_type])  # Add header if sheet is new
        sheet_map[vehicle_type] = sheet

    with sync_playwright() as p:
        # Iterate through each vehicle type
        for vehicle_type in selected_types:
            input_csv = input_csv_files[vehicle_type]

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
                        count = 0
                        while True:
                            try:
                                # Launch Firefox with stealth mode
                                browser = p.firefox.launch(headless=False)
                                context = browser.new_context()
                                page = context.new_page()
                                stealth_sync(page)

                                print(make_url)


                                page.goto(make_url, timeout=30000)
                                time.sleep(5)
                                # Wait for the page to load completely
                                break
                            except:
                                print('retrying..closing browsers')
                                browser.close()
                                continue

                        while True:
                            try:
                                if vehicle_type == "rvs":
                                    # Wait for the RV table to load
                                    page.wait_for_selector("table.table-enhanced--model-years", timeout=10000)

                                    rows = page.query_selector_all("table.table-enhanced--model-years tr")
                                    current_model = None
                                    consecutive_tr_count = 0

                                    for row in rows:
                                        # Handle consecutive <tr> tags for models
                                        if not row.get_attribute("class"):
                                            consecutive_tr_count += 1
                                            if consecutive_tr_count == 2:  # Second consecutive <tr> is the model
                                                model_header = row.query_selector("td[colspan='6'] h4")
                                                if model_header:
                                                    current_model = model_header.inner_text().strip()
                                                    print(f"Found model (from consecutive <tr>): {current_model}")
                                                consecutive_tr_count = 0
                                            continue
                                        else:
                                            consecutive_tr_count = 0

                                        # Check for <th> headers as models
                                        th_header = row.query_selector("th h3.category")
                                        if th_header:
                                            current_model = th_header.inner_text().strip()
                                            print(f"Found model (from <th>): {current_model}")
                                            continue

                                        # Check if the row defines a trim
                                        if row.get_attribute("class") == "detail-row":
                                            trim_element = row.query_selector("td a")
                                            if trim_element and current_model:
                                                trim_name = trim_element.inner_text().strip()
                                                print(f"Found trim: {trim_name} for model: {current_model}")

                                                # Append to the XLSX sheet
                                                sheet_map[vehicle_type].append(
                                                    [year, vehicle_type, make, current_model, trim_name]
                                                )
                                                workbook.save(output_xlsx)  # Save the workbook after every row
                                elif vehicle_type == "cars":
                                    # General handling for cars
                                    page.wait_for_selector(".yearMake_model-wrapper__t8GAv", timeout=10000)

                                    # Get all model names
                                    model_elements = page.query_selector_all(".yearMake_model-wrapper-h3__npC2B h3")
                                    for model_element in model_elements:
                                        model_name = model_element.inner_text().strip()
                                        print(f"Fetching trims for model: {model_name} ({vehicle_type})...")

                                        
                                        while True:
                                            with context.expect_page() as new_tab_event:
                                                model_url = model_element.evaluate(
                                                    "node => node.closest('.yearMake_model-wrapper__t8GAv').querySelector('a').href"
                                                )
                                                page.evaluate(f"window.open('{model_url}', '_blank')")

                                            new_tab = new_tab_event.value
                                            new_tab.wait_for_load_state()
                                            try:
                                                # Wait for the trims section to load
                                                new_tab.wait_for_selector(".trimSelection_card-info__O02As", timeout=10000)

                                                # Locate all trim containers
                                                trim_containers = new_tab.query_selector_all(
                                                    ".MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-6.trimSelection_card-info__O02As"
                                                )

                                                for trim_container in trim_containers:
                                                    # Locate the trim name header
                                                    trim_name_element = trim_container.query_selector("h3.heading-xs.title.spacing-s")
                                                    model_name = trim_name_element.inner_text().strip() if trim_name_element else "Unknown Model"

                                                    # Locate all trims under the model
                                                    trim_links = trim_container.query_selector_all(
                                                        ".MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-12.MuiGrid-grid-md-12 a"
                                                    )

                                                    for trim_link in trim_links:
                                                        trim_name = trim_link.inner_text().strip()
                                                        trim_href = trim_link.get_attribute("href")
                                                        print(f"Model: {model_name}, Trim: {trim_name}")

                                                        # Append to the XLSX sheet
                                                        sheet_map[vehicle_type].append([year, vehicle_type, make, model_name, trim_name])

                                                        # Save the workbook after each trim
                                                        workbook.save(output_xlsx)

                                            except Exception as e:
                                                print(f"Error while processing trims: {e}")
                                                print('Retrying')
                                                new_tab.close()
                                                continue

                                            finally:
                                                # Close the new tab and return to the main page
                                                new_tab.close()
                                                break



                                # Handling for boats
                                elif vehicle_type == "boats":
                                    page.wait_for_selector(".MuiGrid-container", timeout=10000)
                                    rows = page.query_selector_all(".MuiGrid-item")
                                    count = 0
                                    for row in rows:
                                        
                                        columns = row.query_selector_all(".MuiGrid-item")

                                        # Ensure the number of columns matches the expected structure (excluding Year, Vehicle Type, and Make)
                                        if len(columns) == len(headers[vehicle_type]) - 3:  # Subtract 3 for Year, Vehicle Type, and Make
                                            count +=1
                                            # Extract the data for the boat
                                            boat_data = [col.inner_text().strip() for col in columns]

                                            # Prepend Year, Vehicle Type, and Make
                                            boat_data.insert(0, make)
                                            boat_data.insert(0, vehicle_type)
                                            boat_data.insert(0, year)
                                            if count == 1:
                                                count+=1
                                                continue
                                            # Append the row to the sheet
                                            sheet_map[vehicle_type].append(boat_data)

                                            # Save the workbook after each row
                                            workbook.save(output_xlsx)
                                            print(f"Appended for boats: {boat_data}")


                                # Handling for motorcycles
                                elif vehicle_type == "motorcycles":
                                    page.wait_for_selector(".spacing-xs h3.heading-s", timeout=10000)
                                    sections = page.query_selector_all(".spacing-xs + .spacing-s")  # Select the second `.spacing-s` div

                                    for section in sections:
                                        model_element = section.query_selector("h4.bh-l")
                                        if not model_element:
                                            continue

                                        model_name = model_element.inner_text().strip()
                                        print(f"Processing model: {model_name}")

                                        # Fetch trims under the current model
                                        trims = section.query_selector_all(
                                            ".motorcyclesYearMake_model-link-container__JIYG4 a.motorcyclesYearMake_model-link__Db22K"
                                        )

                                        for trim_element in trims:
                                            trim_name = trim_element.inner_text().strip()
                                            print(f"Found trim: {trim_name} for model: {model_name}")

                                            # Append the data to the corresponding sheet
                                            if vehicle_type in sheet_map:
                                                sheet_map[vehicle_type].append(
                                                    [year, vehicle_type, make, model_name, trim_name]
                                                )
                                                workbook[vehicle_type.capitalize()].append(
                                                    [year, vehicle_type, make, model_name, trim_name]
                                                )
                                                workbook.save(output_xlsx)  # Save after every row

                                break
                            except Exception as e:
                                print(f"Error processing {make} ({vehicle_type}): {e}")
                                continue

        browser.close()

    print(f"Data saved to {output_xlsx}.")


# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape vehicle data from JDPower.")
    parser.add_argument(
        "--years",
        type=str,
        required=True,
        help="Specify a single year (e.g., 2025) or a range of years (e.g., 2020-2025).",
    )
    parser.add_argument("-c", action="store_true", help="Process data for cars")
    parser.add_argument("-r", action="store_true", help="Process data for RVs")
    parser.add_argument("-b", action="store_true", help="Process data for boats")
    parser.add_argument("-m", action="store_true", help="Process data for motorcycles")

    args = parser.parse_args()

    if "-" in args.years:
        start_year, end_year = map(int, args.years.split("-"))
        selected_years = list(map(str, range(start_year, end_year + 1)))
    else:
        selected_years = [args.years]

    selected_types = []
    if args.c:
        selected_types.append("cars")
    if args.r:
        selected_types.append("rvs")
    if args.b:
        selected_types.append("boats")
    if args.m:
        selected_types.append("motorcycles")

    if not selected_types:
        print("No vehicle types selected. Use -c, -r, -b, -m or combinations.")
        sys.exit(1)

    return selected_years, selected_types


if __name__ == "__main__":
    selected_years, selected_types = parse_arguments()
    fetch_data(selected_years, selected_types)