from pystac_client import Client
import json
import csv


def getIds():
    LandsatSTAC = Client.open("https://landsatlook.usgs.gov/stac-server", headers=[])

    def BuildSquare(lon, lat, delta):
        c1 = [lon + delta, lat + delta]
        c2 = [lon + delta, lat - delta]
        c3 = [lon - delta, lat - delta]
        c4 = [lon - delta, lat + delta]
        geometry = {"type": "Polygon", "coordinates": [[ c1, c2, c3, c4, c1 ]]}
        return geometry

    geometry = BuildSquare(-59.346271, -34.233076, 0.01)
    timeRange = '2024-09-01/2024-10-06'
    LandsatSearch = LandsatSTAC.search ( 
        intersects = geometry,
        datetime = timeRange,
        query =  ['eo:cloud_cover95'],
        collections = ["landsat-c2l2-sr"] )

    Landsat_items = [i.to_dict() for i in LandsatSearch.get_items()]
    print(f"{len(Landsat_items)} Landsat scenes fetched")

    ids = []
    for item in Landsat_items:
        ids.append(item['id'].replace('_SR', ''))
    
    
    
    
    
    
    
    
    
# Now, write the ids list to a CSV file
#with open('ids.csv', mode='w', newline='') as file:
   # writer = csv.writer(file)
    
    # If you want to write each id in a new row:
   # for id in ids:
      #  writer.writerow([id])

# Now the 'ids.csv' file will contain each id in a separate row


get_scene_metadata.getMetadata()
    
