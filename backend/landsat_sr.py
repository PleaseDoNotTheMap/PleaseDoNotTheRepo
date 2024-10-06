import pystac_client
import planetary_computer
import odc.stac
import matplotlib.pyplot as plt
import logging

from pystac.extensions.eo import EOExtension as eo

from get_wrs import ConvertToWRS

wrs_converter = ConvertToWRS(shapefile="./WRS2_descending.shp")


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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    lat_lng_to_wrs(47.60357, -122.32945)
