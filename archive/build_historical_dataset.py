import requests
import pandas as pd
import time

headers = {
    "User-Agent": "F1RacePredictor/1.0"
}

seasons = [2022, 2023, 2024]

all_race_data = []

for season in seasons:

    print(f"\n========== SEASON {season} ==========")

    # Get the race calendar
    calendar_url = f"https://api.jolpi.ca/ergast/f1/{season}/races/"
    calendar_response = requests.get(calendar_url, headers=headers)

    calendar_data = calendar_response.json()
    races = calendar_data["MRData"]["RaceTable"]["Races"]

    for race in races:

        round_number = int(race["round"])

        print(
            f"Getting {season} Round {round_number}: "
            f"{race['raceName']}"
        )

        # -------------------------
        # Race results
        # -------------------------

        race_url = (
            f"https://api.jolpi.ca/ergast/f1/"
            f"{season}/{round_number}/results/"
        )

        race_response = requests.get(
            race_url,
            headers=headers
        )

        race_data = race_response.json()

        results = (
            race_data["MRData"]
            ["RaceTable"]
            ["Races"][0]
            ["Results"]
        )

        race_list = []

        for result in results:

            race_list.append({
                "driver": (
                    result["Driver"]["givenName"]
                    + " "
                    + result["Driver"]["familyName"]
                ),
                "constructor": result["Constructor"]["name"],
                "grid_position": result["grid"],
                "finish_position": result["position"]
            })

        race_df = pd.DataFrame(race_list)

        # -------------------------
        # Qualifying results
        # -------------------------

        qualifying_url = (
            f"https://api.jolpi.ca/ergast/f1/"
            f"{season}/{round_number}/qualifying/"
        )

        qualifying_response = requests.get(
            qualifying_url,
            headers=headers
        )

        qualifying_data = qualifying_response.json()

        qualifying = (
            qualifying_data["MRData"]
            ["RaceTable"]
            ["Races"][0]
            ["QualifyingResults"]
        )

        qualifying_list = []

        for result in qualifying:

            qualifying_list.append({
                "driver": (
                    result["Driver"]["givenName"]
                    + " "
                    + result["Driver"]["familyName"]
                ),
                "qualifying_position": result["position"]
            })

        qualifying_df = pd.DataFrame(qualifying_list)

        # -------------------------
        # Combine race + qualifying
        # -------------------------

        combined_df = pd.merge(
            race_df,
            qualifying_df,
            on="driver"
        )

        # -------------------------
        # Add race information
        # -------------------------

        combined_df["season"] = season
        combined_df["round"] = round_number
        combined_df["race_name"] = race["raceName"]
        combined_df["date"] = race["date"]
        combined_df["circuit"] = race["Circuit"]["circuitName"]

        all_race_data.append(combined_df)

        time.sleep(0.5)


# -------------------------
# Combine all seasons
# -------------------------

full_dataset = pd.concat(
    all_race_data,
    ignore_index=True
)

print("\n========== COMPLETE ==========")

print("Dataset shape:")
print(full_dataset.shape)

print("\nRows per season:")
print(full_dataset.groupby("season").size())

print("\nMissing values:")
print(full_dataset.isna().sum())

# Save
full_dataset.to_csv(
    "f1_2022_2024_raw.csv",
    index=False
)

print("\nSaved dataset as f1_2022_2024_raw.csv")