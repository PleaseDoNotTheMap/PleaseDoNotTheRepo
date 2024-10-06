from pystac_client import Client
import json
import requests
import sys
import threading
import datetime
import csv
LONGITU = 35
LATITU= 45


maxthreads = 5  # Threads count for parallel metadata requests
sema = threading.Semaphore(value=maxthreads)
threads = []

# send http request
def sendRequest(url, data, apiKey=None):
    pos = url.rfind('/') + 1
    endpoint = url[pos:]
    json_data = json.dumps(data)
    
    if apiKey is None:
        response = requests.post(url, json_data)
    else:
        headers = {'X-Auth-Token': apiKey}              
        response = requests.post(url, json_data, headers=headers)    
    
    try:
        httpStatusCode = response.status_code 
        if response is None:
            print("No output from service")
            sys.exit()
        output = json.loads(response.text)    
        if output.get('errorCode') is not None:
            print("Failed Request ID", output.get('requestId'))
            print(output['errorCode'], "-", output['errorMessage'])
            sys.exit()
        if httpStatusCode == 404:
            print("404 Not Found")
            sys.exit()
        elif httpStatusCode == 401: 
            print("401 Unauthorized")
            sys.exit()
        elif httpStatusCode == 400:
            print("Error Code", httpStatusCode)
            sys.exit()
    except Exception as e: 
        response.close()
        pos = url.find('api')
        print(f"Failed to parse request {endpoint} response. Re-check the input {json_data}. The input examples can be found at {url[:pos]}api/docs/reference/#{endpoint}\n")
        sys.exit()
    response.close()    
    print(f"Finished request {endpoint} with request ID {output.get('requestId')}\n")
    
    return output.get('data')

def getMetadata(datasetName, entityId, apiKey):
    payload = {
        "datasetName": datasetName,
        "entityId": entityId,
        "idType": "displayId",  # You can change this to entityId or orderingId if needed
        # "idType": "entityId", 
        "metadataType": "full",  # You can also use "summary", "fgdc", "iso"
        "useCustomization": False
    }

    return sendRequest(serviceUrl + "scene-metadata", payload, apiKey)

all_metadata = []
def processSceneMetadata(datasetName, entityId, apiKey):
    sema.acquire()
    try:
        metadata = getMetadata(datasetName, entityId, apiKey)
        if metadata:
            print(f"Scene Metadata for {entityId}:\n", json.dumps(metadata, indent=2))
            all_metadata.append(metadata)
        else: 
            print("Can't find scene metadata")
        sema.release()
    except Exception as e:
        print(f"Failed to retrieve metadata for {entityId}. Error: {e}")
        sema.release()
        
        
def getIds(long, lati):
    LandsatSTAC = Client.open("https://landsatlook.usgs.gov/stac-server", headers=[])

    def BuildSquare(lon, lat, delta):
        c1 = [lon + delta, lat + delta]
        c2 = [lon + delta, lat - delta]
        c3 = [lon - delta, lat - delta]
        c4 = [lon - delta, lat + delta]
        geometry = {"type": "Polygon", "coordinates": [[ c1, c2, c3, c4, c1 ]]}
        return geometry

    geometry = BuildSquare(long, lati, 0.01)
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
        
    return ids

def runMetadataRetrieval(threads, datasetName, entityId, apiKey):
    thread = threading.Thread(target=processSceneMetadata, args=(datasetName, entityId, apiKey))
    threads.append(thread)
    thread.start()

if __name__ == '__main__': 
    username = 'pvgandhi404'
    token = 'Gi82g@NP@CQJMuKAwSNLXdM9sE6H6wb5KKefbO75j3op@JudGYSgDMAis8inAu5X'

    print("\nRunning Scripts...\n")
    
    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    
    # login-token
    payload = {'username': username, 'token': token}
    
    apiKey = sendRequest(serviceUrl + "login-token", payload)
    
    print("API Key: " + apiKey + "\n")
    
    # Use dataset and entityId as per your needs
    datasetName = "landsat_ot_c2_l2"
    
    ids = getIds(LONGITU, LATITU)
    if not ids:
        print("No IDs found.")
        sys.exit()
        
    for entityId in ids:  # This directly iterates through the list of IDs
        runMetadataRetrieval(threads, datasetName, entityId, apiKey)
          # Add more entityIds if needed

        # entityIds = ["LC08_L2SP_012025_20201231_20210308_02_T1"]
         
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
        
    print("Complete Metadata Retrieval")
                
    with open ('scene_metadata.json', 'w')as json_file:
        json.dump(all_metadata, json_file, indent=2)
    # Logout so the API Key cannot be used anymore
    endpoint = "logout"  
    if sendRequest(serviceUrl + endpoint, None, apiKey) is None:        
        print("Logged Out\n\n")
    else:
        print("Logout Failed\n\n")
