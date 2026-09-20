import requests
import pandas as pd
import time

headers = {
    "User-Agent": "F1RacePredictor/1.0"
}

season = 2024

# Get the race calendar
url = f"https://api.jolpi.ca/ergast/f1/{season}/races/"

response = requests.get(url, headers=headers)

data = response.json()

races = data["MRData"]["RaceTable"]["Races"]

race_calendar = []

for race in races:
    race_calendar.append({
        "round": int(race["round"]),
        "race_name": race["raceName"],
        "date": race["date"],
        "circuit": race["Circuit"]["circuitName"]
    })

calendar_df = pd.DataFrame(race_calendar)

print(calendar_df)
all_race_data = []

for _, race in calendar_df.iterrows():

    round_number = race["round"]

    print(f"Getting data for Round {round_number}: {race['race_name']}")

    # Race results
    race_url = f"https://api.jolpi.ca/ergast/f1/{season}/{round_number}/results/"
    race_response = requests.get(race_url, headers=headers)
    race_data = race_response.json()

    results = race_data["MRData"]["RaceTable"]["Races"][0]["Results"]

    # Qualifying results
    qualifying_url = f"https://api.jolpi.ca/ergast/f1/{season}/{round_number}/qualifying/"
    qualifying_response = requests.get(qualifying_url, headers=headers)
    qualifying_data = qualifying_response.json()

    qualifying = qualifying_data["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"]

    # Create race results table
    race_list = []

    for result in results:
        race_list.append({
            "driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
            "constructor": result["Constructor"]["name"],
            "grid_position": result["grid"],
            "finish_position": result["position"]
        })

    race_df = pd.DataFrame(race_list)

    # Create qualifying table
    qualifying_list = []

    for result in qualifying:
        qualifying_list.append({
            "driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
            "qualifying_position": result["position"]
        })

    qualifying_df = pd.DataFrame(qualifying_list)

    # Combine race results and qualifying
    combined_df = pd.merge(
        race_df,
        qualifying_df,
        on="driver"
    )

    # Add race information
    combined_df["season"] = season
    combined_df["round"] = round_number
    combined_df["race_name"] = race["race_name"]
    combined_df["date"] = race["date"]
    combined_df["circuit"] = race["circuit"]

    all_race_data.append(combined_df)

    time.sleep(0.5)

print("Finished collecting all races!")

full_dataset = pd.concat(all_race_data, ignore_index=True)

print(full_dataset)
print("\nDataset shape:")
print(full_dataset.shape)

print("\nMissing values:")
print(full_dataset.isna().sum())

print("\nRows per race:")
print(full_dataset.groupby("round").size())

full_dataset.to_csv("f1_2024_raw.csv", index=False)

print("\nSaved dataset as f1_2024_raw.csv")