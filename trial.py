import csv
csv_file_path = '/Users/lakshanakathirkamaranjan/Downloads/LANDSAT_OT_C2_L2.csv'  # Replace with your actual file path


target_display_id = 'LC08_L2SP_225084_20210528_20210607_02_T1_SR'

def find_display_id(csv_file_path, target_display_id):
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)


        for row in reader:
            # Check if the Display ID matches
            if row['Display ID'] == target_display_id:
                return row  # Return the matching row

    return None  # Return None if no match is found

result = find_display_id(csv_file_path, target_display_id)


if result:
    print("Found entry:", result)
else:
    print("No entry found for Display ID:", target_display_id)