import json
import requests
import sys
serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
url = serviceUrl + "login-token"
# login-token
payload = {"username" : "pvgandhi404", "token" : "Gi82g@NP@CQJMuKAwSNLXdM9sE6H6wb5KKefbO75j3op@JudGYSgDMAis8inAu5X"}
json_data = json.dumps(payload)
response = requests.post(url, json_data)
try:
    httpStatusCode = response.status_code
    if response == None:
        print("No output from service")
        sys.exit()

    output = json.loads(response.text)
    if output['errorCode'] != None:
        print(output)
        sys.exit()
    if httpStatusCode == 404:
        print("404 Not Found")
        sys.exit()

    elif httpStatusCode == 403:
        print("401 Unauthorized")
        sys.exit()
    elif httpStatusCode == 500:
        print("Error Code", httpStatusCode)
        sys.exit()
except Exception as e:
 response.close()
 print(e)

response.close()
apiKey = output['data']
print("API Key: " + apiKey)