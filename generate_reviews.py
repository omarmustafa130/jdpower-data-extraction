import argparse
import pandas as pd
import openpyxl
import sys
import os
import time
import asyncio
from g4f.client import Client

# Set the appropriate event loop policy for Windows
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# File paths
input_file = 'full_dataset/vehicle_data.xlsx'
output_folder = 'output_blurbs'

# Initialize G4F client
client = Client()

# Function to generate a review using G4F API
def generate_review(year, make, model, trim):
    prompt = (f"Write a simple (max 150 word) review on {year} {make} {model} {trim} and only include these letters "
              "(english only):(abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890.?\"-!,:&;()'/)")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Function to process sheets based on the selected types
def process_sheets(selected_sheets):
    # Load the Excel file
    workbook = openpyxl.load_workbook(input_file)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for sheet_name in workbook.sheetnames:
        if sheet_name.lower() not in selected_sheets:
            continue

        print(f"Processing sheet: {sheet_name}")
        sheet = workbook[sheet_name]
        df = pd.DataFrame(sheet.values)
        df.columns = df.iloc[0]  # Use the first row as column headers
        df = df[1:]  # Skip the header row

        # Rename Review column to Blurb or add it if not present
        if 'Review' in df.columns:
            df.rename(columns={'Review': 'Blurb'}, inplace=True)
        elif 'Blurb' not in df.columns:
            df['Blurb'] = ''

        # Output CSV file for the current sheet
        output_csv_path = f"{output_folder}/{sheet_name}.csv"

        # Check if the CSV file already exists
        file_exists = os.path.exists(output_csv_path)
        processed_rows = set()
        if file_exists:
            existing_df = pd.read_csv(output_csv_path, encoding='utf-8-sig')
            processed_rows = set(existing_df.index)

        with open(output_csv_path, mode='a', encoding='utf-8-sig', newline='') as f:
            # Write headers if the file doesn't exist
            if not file_exists:
                f.write(','.join(df.columns) + '\n')

            for index, row in df.iterrows():
                # Skip rows already processed
                if index in processed_rows:
                    continue

                try:
                    # Generate a review for the current row
                    year = row.get('Year', 'unknown year')
                    make = row.get('Make', 'unknown make')
                    model = row.get('Model', 'unknown model')
                    trim = row.get('Trim', 'unknown trim')

                    while True:
                        try:
                            review = generate_review(year, make, model, trim)
                            print(f"Generated review: {review}")

                            # Validate review for allowed characters
                            if all(ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890.-!,:&;()'/" for ch in review):
                                row['Blurb'] = review
                                # Write the row to the CSV, ensuring the review is in a single cell
                                row_data = [str(val) if i != 'Blurb' else f'"{review}"' for i, val in row.items()]
                                f.write(','.join(row_data) + '\n')
                                print(f"Blurb added for {make} {model} {trim}: {review}")
                                break
                            else:
                                print(f"Invalid characters found. Retrying blurb for {make} {model} {trim}.")
                                continue
                        except Exception as retry_error:
                            print(f"Retrying due to error: {retry_error}")
                            continue
                except Exception as e:
                    print(f"Error generating blurb for row {index}: {str(e)}")
                    continue

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate vehicle reviews.")
    parser.add_argument(
        "-c", action="store_true", help="Generate reviews for Cars"
    )
    parser.add_argument(
        "-r", action="store_true", help="Generate reviews for RVs"
    )
    parser.add_argument(
        "-b", action="store_true", help="Generate reviews for Boats"
    )
    parser.add_argument(
        "-m", action="store_true", help="Generate reviews for Motorcycles"
    )
    args = parser.parse_args()

    # Map arguments to sheet names
    selected_sheets = []
    if args.c:
        selected_sheets.append("cars")
    if args.r:
        selected_sheets.append("rvs")
    if args.b:
        selected_sheets.append("boats")
    if args.m:
        selected_sheets.append("motorcycles")

    # Check if no arguments were provided
    if not selected_sheets:
        print("No vehicle types selected. Use -c, -r, -b, -m or combinations.")
        sys.exit(1)

    # Start tracking execution time
    start_time = time.time()

    try:
        process_sheets(selected_sheets)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Total execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()
