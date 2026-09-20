import requests
import pandas as pd

url = "https://api.jolpi.ca/ergast/f1/2024/1/results/"

headers = {
    "User-Agent": "F1RacePredictor/1.0"
}

response = requests.get(url, headers=headers)

data = response.json()

results = data["MRData"]["RaceTable"]["Races"][0]["Results"]

result_list = []

for result in results:
    result_list.append({
        "driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
        "constructor": result["Constructor"]["name"],
        "grid_position": result["grid"],
        "finish_position": result["position"]
    })

df = pd.DataFrame(result_list)

print(df)