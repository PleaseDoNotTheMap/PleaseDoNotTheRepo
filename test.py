import csv

# Path to the CSV file
# csv_file_path = '/home/peri/Downloads/LANDSAT_OT_C2_L1.csv'  # Replace with your actual file path
csv_file_path = '/home/peri/Downloads/LANDSAT_OT_C2_L2.csv'  # Replace with your actual file path


# The Display ID to search for
# target_display_id = 'LE07_L2SP_226084_20210527_20210622_02_T1_SR'
target_display_id = 'LC08_L2SP_226084_20210519_20210528_02_T1_SR'

# Function to search for the Display ID in the CSV
def find_display_id(csv_file_path, target_display_id):
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # Iterate through each row in the CSV
        for row in reader:
            # Check if the Display ID matches
            if row['Display ID'] == target_display_id:
                return row  # Return the matching row

    return None  # Return None if no match is found

# Call the function
result = find_display_id(csv_file_path, target_display_id)

# Output the result
if result:
    print("Found entry:", result)
else:
    print("No entry found for Display ID:", target_display_id)
