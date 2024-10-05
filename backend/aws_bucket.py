import boto3
import boto3.session
import base64
import os
import rasterio as rio
from pystac_client import Client
from rasterio.features import bounds
from pyproj import Transformer

ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')

LandsatSTAC = Client.open("https://landsatlook.usgs.gov/stac-server", headers=[])

def BuildSquare(lon, lat, delta):
    c1 = [lon + delta, lat + delta]
    c2 = [lon + delta, lat - delta]
    c3 = [lon - delta, lat - delta]
    c4 = [lon - delta, lat + delta]
    geometry = {"type": "Polygon", "coordinates": [[ c1, c2, c3, c4, c1 ]]}
    return geometry

geometry = BuildSquare(-59.346271, -34.233076, 0.04)
timeRange = '2019-06-01/2021-06-01'
LandsatSearch = LandsatSTAC.search ( 
    intersects = geometry,
    datetime = timeRange,
    query =  ['eo:cloud_cover95'],
    collections = ["landsat-c2l2-sr"] )

Landsat_items = [i.to_dict() for i in LandsatSearch.get_items()]
print(f"{len(Landsat_items)} Landsat scenes fetched")

first = Landsat_items[0]['assets']['red']['alternate']['s3']['href']

print(first)

b_session = boto3.session.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-west-2'
)

aws_session = rio.session.AWSSession(b_session, requester_pays=True)

from pyproj import Transformer

def getSubset(geotiff_file, bbox):
    with rio.Env(aws_session):
        with rio.open(geotiff_file) as geo_fp:
            # Calculate pixels with PyProj 
            Transf = Transformer.from_crs("epsg:4326", geo_fp.crs) 
            lat_north, lon_west = Transf.transform(bbox[3], bbox[0])
            lat_south, lon_east = Transf.transform(bbox[1], bbox[2]) 
            x_top, y_top = geo_fp.index( lat_north, lon_west )
            x_bottom, y_bottom = geo_fp.index( lat_south, lon_east )
            # Define window in RasterIO
            window = rio.windows.Window.from_slices( ( x_top, x_bottom ), ( y_top, y_bottom ) )                
            # Actual HTTP range request
            subset = geo_fp.read(1, window=window)
    return subset


bbox = bounds(geometry)
print(getSubset(first, bbox))

#    s3.download_fileobj('usgs-landsat', 'collection02/level1/standard/oli-tirs/2013/030/030/LC08_L1TP_030030_20130320_20200913_02_T1/LC08_L1TP_030030_20130320_20200913_02_T1_B4.TIF', f, ExtraArgs={'RequestPayer': 'requester'})

