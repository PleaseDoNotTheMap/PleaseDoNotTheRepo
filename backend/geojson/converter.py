#converts CSV file to GeoJSON file
#change csv_file and geojson_file to corresponding paths

import csv
import json

def csv_to_geojson(csv_file, geojson_file):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        #iterate through csv file
        for row in reader:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [float(row["CTR LAT"]), float(row["CTR LON"]), 1],
                            [float(row["UL LAT"]), float(row["UL LON"]), 1],
                            [float(row["UR LAT"]), float(row["UR LON"]), 1],
                            [float(row["LL LAT"]), float(row["LL LON"]), 1],
                            [float(row["LR LAT"]), float(row["LR LON"]), 1],
                        ]
                    ]
                }
                ,
                "properties": {
                    "path": int(row["PATH"]),
                    "row": int(row["ROW"])
                }
            }
            geojson["features"].append(feature)

    with open(geojson_file, 'w') as f:
        json.dump(geojson, f, indent=4)


csv_file = "backend\geojson\\test.csv"
geojson_file = "output.geojson"
csv_to_geojson(csv_file, geojson_file)
