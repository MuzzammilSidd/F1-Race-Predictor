import requests
import pandas as pd

headers = {
    "User-Agent": "F1RacePredictor/1.0"
}

# Get race results
race_url = "https://api.jolpi.ca/ergast/f1/2024/1/results/"
race_response = requests.get(race_url, headers=headers)
race_data = race_response.json()

results = race_data["MRData"]["RaceTable"]["Races"][0]["Results"]

race_list = []

for result in results:
    race_list.append({
        "driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
        "constructor": result["Constructor"]["name"],
        "grid_position": result["grid"],
        "finish_position": result["position"]
    })

race_df = pd.DataFrame(race_list)


# Get qualifying results
qualifying_url = "https://api.jolpi.ca/ergast/f1/2024/1/qualifying/"
qualifying_response = requests.get(qualifying_url, headers=headers)
qualifying_data = qualifying_response.json()

qualifying = qualifying_data["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"]

qualifying_list = []

for result in qualifying:
    qualifying_list.append({
        "driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
        "qualifying_position": result["position"]
    })

qualifying_df = pd.DataFrame(qualifying_list)


# Combine the two tables
combined_df = pd.merge(
    race_df,
    qualifying_df,
    on="driver"
)

print(combined_df)