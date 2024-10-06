import pystac_client
import planetary_computer
import odc.stac
import matplotlib.pyplot as plt
import logging
import json
from datetime import datetime
from pystac.extensions.eo import EOExtension as eo

from get_wrs import ConvertToWRS
#wrs_converter = ConvertToWRS(shapefile="./WRS2_descending.shp")

cycles = None
with open("cycles_full.json", "r") as f:
    cycles = json.load(f)


def lat_lng_to_wrs(lat: float, lng: float) -> list:
    """[{'path': 201, 'row': 25}, {'path': 202, 'row': 25} ...]"""
    return wrs_converter.get_wrs(lat, lng)


def get_with_params(bbox: list, datestr: str, max_cloud_cover: int) -> None:
    """bbox: [-122.2751, 47.5469, -121.9613, 47.7458]"""
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    target_collections = [
        "landsat-c2-l2",
    ]

    search = catalog.search(
        collections=target_collections,
        bbox=bbox,
        datetime=datestr,
        query={"eo:cloud_cover": {"lt": max_cloud_cover}}
    )
    
    items = search.item_collection()
    logging.info(f"Found {len(items)} items")

    selected_item = min(items, key=lambda item: eo.ext(item).cloud_cover)

    logging.info(
        f"Choosing {selected_item.id} from {selected_item.datetime.date()}"
        + f" with {selected_item.properties['eo:cloud_cover']}% cloud cover"
    )


    bands_of_interest = ["nir08", "red", "green", "blue", "qa_pixel", "lwir11"]
    data = odc.stac.stac_load(
        [selected_item], bands=bands_of_interest, bbox=bbox
    ).isel(time=0)

    fig, ax = plt.subplots(figsize=(10,10))
    data[["red", "green", "blue"]].to_array().plot.imshow(robust=True, ax=ax)
    ax.set_title("Natural Color, Redmond, WA")
    plt.show()


def get_next_acq(lat: float, lng: float) -> dict:
    """
    {
        "landsat_7": {
            "1/1/2021": {
                "path": "100,116,132",
                "cycle": "3"
            }
        },
    }

    Returns

    {
        "landsat_7": datetime,
        "landsat_8": datetime,
        "landsat_9": datetime
    }
    """
    values = {
#        "landsat_7": None,
        "landsat_8": None,
        "landsat_9": None
    }

    now = datetime.now()

    path = 67

    for satellite in values.keys():
        for mission in cycles[satellite].keys():
            mission_date = datetime.strptime(mission, "%m/%d/%Y")
            if mission_date > now and str(path) in cycles[satellite][mission]["path"]:
                values[satellite] = mission_date
                break
    return values


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(get_next_acq(47.5469, -122.2751))
