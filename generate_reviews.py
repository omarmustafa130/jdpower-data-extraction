import argparse
import pandas as pd
import openpyxl
import sys
import os
import time
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


# Set the appropriate event loop policy for Windows
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# File paths
input_file = 'full_dataset/vehicle_data.xlsx'
output_folder = 'output_blurbs'



# Function to generate a review using G4F API
def generate_review(year, make, model_name, trim=None, **details):
    template = """Question: {question}

    Anser: Let's think step by step."""

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="deepseek-r1", base_url = "http://127.0.0.1:11434/")

    chain = prompt | model
    # Create the prompt based on available details
    print(f"Write a simple (max 150 word) review on {year} {make} {model_name} {trim}.")
    if trim:
        result = chain.invoke({"question": f"Write a simple (max 150 word) review on {year} {make} {model_name} {trim}. The review should be similar in structure with the following: The 2023 Acura Integra Sedan 4D offers an excellent balance of style, reliability, and value for its price. With a sleek design that combines modern aesthetics, it captures attention while maintaining comfort and efficiency. Under the hood, it features a 1.5L turbocharged engine delivering impressive power without compromising on fuel economy. Inside, the cabin is comfortable, equipped with supportive seats and a user-friendly infotainment system, making it ideal for daily commutes or casual drives. Its overall value ensures you get high-quality performance at an accessible price point, making it a top choice for those seeking a reliable yet stylish car."})
        result = result.split('</think>')[1]

    else:
        result = chain.invoke({"question": f"Write a simple (max 150 word) review on {year} {make} {model_name}. The review should be similar in structure with the following: The 2023 Acura Integra Sedan 4D offers an excellent balance of style, reliability, and value for its price. With a sleek design that combines modern aesthetics, it captures attention while maintaining comfort and efficiency. Under the hood, it features a 1.5L turbocharged engine delivering impressive power without compromising on fuel economy. Inside, the cabin is comfortable, equipped with supportive seats and a user-friendly infotainment system, making it ideal for daily commutes or casual drives. Its overall value ensures you get high-quality performance at an accessible price point, making it a top choice for those seeking a reliable yet stylish car."})

    # Filter out N/A or unknown values
    filtered_details = {k: v for k, v in details.items() if v.lower() not in ["n/a", "unknown", "unknown length", "unknown model type", "unknown hull", "unknown ccs", "unknown engines", "unknown hp", "unknown weight", "unknown fuel type"]}


    return result

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

        # Check if the sheet has data
        if df.empty:
            print(f"No data found in sheet: {sheet_name}. Skipping...")
            continue

        # Use the first row as column headers
        df.columns = df.iloc[0]
        df = df[1:]  # Skip the header row

        # Determine if this is the boats sheet
        is_boats = sheet_name.lower() == "boats"

        # Add a Blurb column if it doesn't exist
        if 'Blurb' not in df.columns:
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

                    if is_boats:
                        # For boats, use additional details in the review
                        details = {
                            "Length": row.get('Length', 'unknown length'),
                            "Model Type": row.get('Model Type', 'unknown model type'),
                            "Hull": row.get('Hull', 'unknown hull'),
                            "CC's": row.get("CC's", 'unknown CCs'),
                            "Engine(s)": row.get('Engine(s)', 'unknown engines'),
                            "HP": row.get('HP', 'unknown HP'),
                            "Weight (lbs)": row.get('Weight (lbs)', 'unknown weight'),
                            "Fuel Type": row.get('Fuel Type', 'unknown fuel type')
                        }
                        review = generate_review(year, make, model, **details)
                    else:
                        # For other vehicle types, use the standard review generation
                        trim = row.get('Trim', 'unknown trim')
                        review = generate_review(year, make, model, trim)

                    print(f"Generated review: {review}\n\n")

                    # Validate review for allowed characters
                    row['Blurb'] = review
                    # Write the row to the CSV, ensuring the review is in a single cell
                    row_data = [str(val) if i != 'Blurb' else f'"{review}"' for i, val in row.items()]
                    f.write(','.join(row_data) + '\n')

                except Exception as retry_error:
                    print(f"Retrying due to error: {retry_error}")
                    continue
                except Exception as e:
                    print(f"Error generating blurb for row {index}: {str(e)}")
                    continue

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
    parser.add_argument(
        "-all", action="store_true", help="Generate reviews for all vehicle types (Cars, RVs, Boats, Motorcycles)"
    )
    args = parser.parse_args()

    # If -all is provided, set all other flags to True
    if args.all:
        args.c = True
        args.r = True
        args.b = True
        args.m = True

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
        print("No vehicle types selected. Use -c, -r, -b, -m, -all or combinations.")
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