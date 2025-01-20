# jdpower-data-extraction
python scripts to extract vehicles data on jdpower with playwright, then provide AI-generated feedback on it.

# How to use
1- Open cmd

2- Run generate_dataset.py 
* This will generate 4 CSV files (cars, motorcycles, boats, and RVs: with makes and years available)

3- Run main.py with the following command: python main.py years
* the year flag will determine which year to extract data for (Specify a single year (e.g., 2025) or a range of years (e.g., 2020-2025))
* This will generate full dataset of "Year, Make, Model, Trim, Type, Blurb"
