from pystac_client import Client
import json

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
