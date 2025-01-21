# jdpower-data-extraction
Python scripts to extract vehicle data from JD Power using Playwright, with free AI-generated reviews.

## Features
* Initial Dataset Generation: Generate CSV files for cars, motorcycles, boats, and RVs with available makes and years.
* Full Dataset Generation: Extract detailed data (Year, Make, Model, Trim, Type, Blurb).
* Optional Review Data: Integrate reviews for each vehicle type using GPT 4 Free.
* Automated Environment Setup: Install all required dependencies and prepare the environment with a single command.

## Prerequisites
* Python 3.8 or higher installed.
* Pip package manager.
* Stable internet connection for Playwright and JD Power scraping.

## How to use
### Setup Environment
Run the setup script to install all necessary dependencies and configure the environment:
```bash
python main.py
```
and it will ask you for 5 options, choose the 5th one which is setting up the environment.

### Generate Initial Dataset 
To create a basic dataset with available makes and years for cars, motorcycles, boats, and RVs (You have to select this if you don't have the initial dataset, as it's required for the full dataset to be generated):
```bash
python main.py
```
and it will ask you for 5 options, choose the 1st option one which will generate an initial dataset.

### Generate Full Dataset Without Reviews
Run the script and specify the year(s) and vehicle types for the full dataset:
```bash
python main.py
```
Select option 2, then follow the prompts:
* Enter the year or range of years, e.g., 2025 or 2023-2025.
* Choose the vehicle types:

-c: Cars 

-b: Boats

-r: RVs

-m: Motorcycles

-cr: Cars and RVs

-crb: Cars, RVs, and Boats

-crbm: Cars, RVs, Boats, and Motorcycles

-all: All vehicle types.

### Generate Full Dataset With Reviews
To extract detailed vehicle data including AI-generated reviews, follow these steps:
```bash
python main.py
```
Select option 3, then follow the prompts:
* Enter the year or range of years, e.g., 2025 or 2023-2025.
* Choose the vehicle types:

-c: Cars 

-b: Boats

-r: RVs

-m: Motorcycles

-cr: Cars and RVs

-crb: Cars, RVs, and Boats

-crbm: Cars, RVs, Boats, and Motorcycles

-all: All vehicle types.


### Generate Reviews Only
If you have the full dataset and want to generate AI-generated feedback, follow these steps:
```bash
python main.py
```
Select option 4, then follow the prompts:
* Choose the vehicle types:

-c: Cars 

-b: Boats

-r: RVs

-m: Motorcycles

-cr: Cars and RVs

-crb: Cars, RVs, and Boats

-crbm: Cars, RVs, Boats, and Motorcycles

-all: All vehicle types.