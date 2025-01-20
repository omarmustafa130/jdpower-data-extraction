import csv
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time

# Base URLs and their specific selectors for different vehicle types
vehicle_types = {
    #"cars": {
    #    "url": "https://www.jdpower.com/cars/manufacturers",
    #    "selector": "ul.selectMake_popularMakesList__X9qw1 li a"
    #},
    "rvs": {
        "url": "https://www.jdpower.com/rvs/manufacturers",
        "selector": "div.make-list__links a"
    },
    #"boats": {
    #    "url": "https://www.jdpower.com/boats/manufacturers",
    #    "selector": "ul.selectMake_popularMakesList__5WsOW li a"
    #},
    "motorcycles": {
        "url": "https://www.jdpower.com/motorcycles/manufacturers",
        "selector": "ul.selectMake_popularMakesList__5WsOW li a"
    }
}

# Function to scrape data for a given vehicle type
def scrape_makes_and_years(vehicle_type, details):
    output_file = f"{vehicle_type}_makes_and_years.csv"

    with sync_playwright() as p:
        while True:
            try:
                # Launch Firefox with stealth mode
                browser = p.firefox.launch(headless=True)  # Set to True for headless mode
                context = browser.new_context()
                page = context.new_page()
                page.goto(details["url"], wait_until="domcontentloaded", timeout=30000)

                time.sleep(5)
                break
            except:
                print('Retrying...')
                browser.close()
                continue

        # Open CSV file for appending
        with open(output_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            file.seek(0, 2)  # Move to the end of the file
            if file.tell() == 0:
                writer.writerow(["Make", "Available Years"])  # Write header if file is empty

            try:
                # Wait for the list of makes to load
                page.wait_for_selector(details["selector"], timeout=30000)

                # Find all make links
                makes = page.query_selector_all(details["selector"])

                for make in makes:
                    make_name = make.inner_text().strip()
                    make_url = make.get_attribute("href")
                    if not make_url:
                        continue
                    print(f"Fetching years for: {make_name} ({vehicle_type}) - {make_url}")
                    while True:
                        try:
                            # Open the make's page in a new tab
                            with context.expect_page() as new_tab_event:
                                page.evaluate(f"window.open('{make_url}', '_blank');")
                            new_tab = new_tab_event.value
                            new_tab.wait_for_load_state()

                            try:
                                if vehicle_type == "cars":
                                    # Keep cars functionality unchanged
                                    new_tab.wait_for_selector("#Year-customized-select", timeout=10000)
                                    new_tab.click("#Year-customized-select")
                                    year_options = new_tab.query_selector_all("li.MuiMenuItem-root")
                                    available_years = [option.inner_text().strip() for option in year_options]

                                elif vehicle_type == "rvs":
                                    # Handle RV dropdown
                                    new_tab.wait_for_selector("select.js-nav-select", timeout=10000)
                                    year_dropdown = new_tab.query_selector("select.js-nav-select")
                                    options = year_dropdown.query_selector_all("option")
                                    available_years = [option.inner_text().strip() for option in options]

                                elif vehicle_type in ["boats", "motorcycles"]:
                                    # Handle boats and motorcycles dropdown
                                    new_tab.wait_for_selector("#Year-customized-select", timeout=10000)
                                    new_tab.click("#Year-customized-select")
                                    year_options = new_tab.query_selector_all("li[role='option']")
                                    available_years = [option.inner_text().strip() for option in year_options]

                                print(f"Available years for {make_name} ({vehicle_type}): {available_years}")

                                # Append the make and years to the CSV file
                                writer.writerow([make_name, ", ".join(available_years)])

                            except Exception as e:
                                print(f"Error fetching years for {make_name} ({vehicle_type}): {e}")

                            finally:
                                # Close the new tab and return to the main page
                                new_tab.close()
                                break
                        except:
                            try:
                                new_tab.close()
                            except:
                                pass
                            continue

            except Exception as e:
                print(f"Error processing {vehicle_type} makes: {e}")

        browser.close()
        print(f"Data appended to {output_file}")

# Main function to scrape all vehicle types sequentially
def scrape_all_vehicle_types():
    for vehicle_type, details in vehicle_types.items():
        print(f"Starting scrape for {vehicle_type}...")
        scrape_makes_and_years(vehicle_type, details)
        print(f"Completed scrape for {vehicle_type}.\n")

# Run the function
scrape_all_vehicle_types()
