import json

def main():
    with open("./scenes.geojson", "r") as f:
        data = json.load(f)

        to_write = []
        with open("./simple.geojson", "w") as f:
            for feature in data["features"]:

                if "type" not in feature:
                    continue
                if "geometry" not in feature:
                    continue
                if "type" not in feature["geometry"]:
                    continue

                if feature["geometry"]["type"] == "Polygon":
                    to_write.append(feature["geometry"])
        
        with open("./simple.geojson", "w") as f:
            json.dump(to_write, f)

if __name__ == "__main__":
    main()
