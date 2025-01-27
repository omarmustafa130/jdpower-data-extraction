import openpyxl

# Load the workbook and select the 'Bots' worksheet
wb = openpyxl.load_workbook('full_dataset/vehicle_data.xlsx')
ws = wb['Boats']

# Define the target values starting from the fourth column
target = ["Model", "Length", "Model Type", "Hull", "CC's", 
          "Engine(s)", "HP", "Weight (lbs)", "Fuel Type"]

rows_to_delete = []
first_occurrence = None

# Iterate through each row to find matches
for row_idx, row in enumerate(ws.iter_rows(min_row=1, values_only=True), start=1):
    # Check if the row has enough columns and matches the target pattern
    if len(row) >= 12:
        # Compare from the 4th column (index 3) to the 12th column (index 11)
        if list(row[3:12]) == target:
            if first_occurrence is None:
                first_occurrence = row_idx
            else:
                rows_to_delete.append(row_idx)

# Delete rows in reverse order to avoid shifting issues
for row_idx in reversed(rows_to_delete):
    ws.delete_rows(row_idx)

# Save the modified workbook
wb.save('full_dataset/vehicle_data.xlsx')