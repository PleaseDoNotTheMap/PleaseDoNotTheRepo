#converts CSV file to GeoJSON file
#change csv_file and geojson_file to corresponding paths

import csv
import json

def csv_to_geojson(csv_file, geojson_file):
    data = {}

    with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        #iterate through csv file
        for row in reader:
            path = int(row["PATH"])

            if path not in data:
                data[path] = [(float(row["CTR LON"]), float(row["CTR LAT"]))]
            else:
                data[path].append((float(row["CTR LON"]), float(row["CTR LAT"])))
        with open(f"{geojson_file}", 'w') as f:
            json.dump(data, f)

csv_file = "./WRScornerPoints.csv"
geojson_file = "output.json"
csv_to_geojson(csv_file, geojson_file)
