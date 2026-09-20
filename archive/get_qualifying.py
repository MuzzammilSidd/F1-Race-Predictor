import requests
import pandas as pd

url = "https://api.jolpi.ca/ergast/f1/2024/1/qualifying/"

headers = {
    "User-Agent": "F1RacePredictor/1.0"
}

response = requests.get(url, headers=headers)

data = response.json()

qualifying = data["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"]

qualifying_list = []

for result in qualifying:
    qualifying_list.append({
        "driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
        "constructor": result["Constructor"]["name"],
        "qualifying_position": result["position"]
    })

df = pd.DataFrame(qualifying_list)

print(df)