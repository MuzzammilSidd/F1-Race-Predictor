import requests
import pandas as pd
import time
import os

# ============================================================
# F1 HISTORICAL DATA UPDATER
# Downloads race + qualifying data from Jolpica/Ergast API
# ============================================================

BASE_URL = "https://api.jolpi.ca/ergast/f1"

HEADERS = {
    "User-Agent": "F1RacePredictor/1.0"
}

EXISTING_FILE = "f1_2022_2024_raw.csv"
OUTPUT_FILE = "f1_2022_2026_raw.csv"

# We want:
# 2025 = complete season
# 2026 = completed races through Spain (Round 14)
SEASONS = {
    2025: None,   # None = automatically find all available rounds
    2026: 14      # Spain was Round 14
}


def get_json(url):
    """Download JSON data from the API."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_season_rounds(season):
    """Get all available race rounds for a season."""

    url = f"{BASE_URL}/{season}.json"

    data = get_json(url)

    races = data["MRData"]["RaceTable"]["Races"]

    rounds = []

    for race in races:
        rounds.append({
            "round": int(race["round"]),
            "race_name": race["raceName"],
            "circuit": race["Circuit"]["circuitName"]
        })

    return rounds


def get_race_results(season, round_number):
    """Download race results for one race."""

    url = f"{BASE_URL}/{season}/{round_number}/results/"

    data = get_json(url)

    races = data["MRData"]["RaceTable"]["Races"]

    if not races:
        return []

    race = races[0]

    race_name = race["raceName"]
    circuit = race["Circuit"]["circuitName"]

    results = race.get("Results", [])

    rows = []

    for result in results:

        # Some results may not have a usable finishing position.
        # We skip those because our model needs a numeric target.
        try:
            finish_position = int(result["position"])
        except (ValueError, TypeError, KeyError):
            continue

        try:
            grid_position = int(result["grid"])
        except (ValueError, TypeError, KeyError):
            grid_position = None

        driver = (
            result["Driver"]["givenName"]
            + " "
            + result["Driver"]["familyName"]
        )

        constructor = result["Constructor"]["name"]

        rows.append({
            "season": season,
            "round": round_number,
            "race_id": f"{season}_{round_number}",
            "race_name": race_name,
            "circuit": circuit,
            "driver": driver,
            "constructor": constructor,
            "grid_position": grid_position,
            "finish_position": finish_position
        })

    return rows


def get_qualifying_results(season, round_number):
    """Download qualifying results for one race."""

    url = f"{BASE_URL}/{season}/{round_number}/qualifying/"

    try:
        data = get_json(url)
    except requests.HTTPError:
        print(
            f"      No qualifying data available for "
            f"{season} Round {round_number}"
        )
        return {}

    races = data["MRData"]["RaceTable"]["Races"]

    if not races:
        return {}

    qualifying = races[0].get("QualifyingResults", [])

    qualifying_positions = {}

    for result in qualifying:

        driver = (
            result["Driver"]["givenName"]
            + " "
            + result["Driver"]["familyName"]
        )

        try:
            position = int(result["position"])
        except (ValueError, TypeError, KeyError):
            continue

        qualifying_positions[driver] = position

    return qualifying_positions


# ============================================================
# START
# ============================================================

print("=" * 60)
print("F1 HISTORICAL DATA UPDATE")
print("=" * 60)

# ------------------------------------------------------------
# Load existing 2022-2024 data
# ------------------------------------------------------------

if not os.path.exists(EXISTING_FILE):
    print(f"\nERROR: {EXISTING_FILE} was not found.")
    print("Make sure this script is inside your F1 Race Predictor folder.")
    raise SystemExit

print(f"\nLoading existing data: {EXISTING_FILE}")

existing_df = pd.read_csv(EXISTING_FILE)

print(f"Existing rows: {len(existing_df)}")

# ------------------------------------------------------------
# Download new seasons
# ------------------------------------------------------------

new_rows = []

for season, max_round in SEASONS.items():

    print("\n" + "=" * 60)
    print(f"PROCESSING {season}")
    print("=" * 60)

    rounds = get_season_rounds(season)

    if max_round is not None:
        rounds = [
            race
            for race in rounds
            if race["round"] <= max_round
        ]

    print(f"Races to download: {len(rounds)}")

    for race_info in rounds:

        round_number = race_info["round"]
        race_name = race_info["race_name"]

        print(
            f"\n  Round {round_number}: {race_name}"
        )

        # ----------------------------------------------------
        # Race results
        # ----------------------------------------------------

        race_rows = get_race_results(
            season,
            round_number
        )

        if not race_rows:
            print("      WARNING: No race results found.")
            continue

        # ----------------------------------------------------
        # Qualifying
        # ----------------------------------------------------

        qualifying = get_qualifying_results(
            season,
            round_number
        )

        # ----------------------------------------------------
        # Combine qualifying with race results
        # ----------------------------------------------------

        for row in race_rows:

            driver = row["driver"]

            row["qualifying_position"] = qualifying.get(
                driver,
                None
            )

            new_rows.append(row)

        print(
            f"      Race results: {len(race_rows)} drivers"
        )

        print(
            f"      Qualifying results: {len(qualifying)} drivers"
        )

        time.sleep(0.2)


# ------------------------------------------------------------
# Convert downloaded data to DataFrame
# ------------------------------------------------------------

new_df = pd.DataFrame(new_rows)

if new_df.empty:
    print("\nERROR: No new data was downloaded.")
    raise SystemExit


# ------------------------------------------------------------
# Match the important columns
# ------------------------------------------------------------

required_columns = [
    "season",
    "round",
    "race_id",
    "race_name",
    "circuit",
    "driver",
    "constructor",
    "grid_position",
    "qualifying_position",
    "finish_position"
]

new_df = new_df[required_columns]


# ------------------------------------------------------------
# Make sure existing data has the same structure
# ------------------------------------------------------------

for column in required_columns:

    if column not in existing_df.columns:

        if column == "race_name":
            existing_df[column] = existing_df["race_id"]

        else:
            existing_df[column] = None


existing_df = existing_df[required_columns]


# ------------------------------------------------------------
# Combine old + new
# ------------------------------------------------------------

combined_df = pd.concat(
    [
        existing_df,
        new_df
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Remove duplicate driver/race entries
# ------------------------------------------------------------

before = len(combined_df)

combined_df = combined_df.drop_duplicates(
    subset=[
        "season",
        "round",
        "driver"
    ],
    keep="last"
)

after = len(combined_df)

print("\n" + "=" * 60)
print("DATA CLEANUP")
print("=" * 60)

print(f"Rows before duplicate removal: {before}")
print(f"Rows after duplicate removal:  {after}")
print(f"Duplicates removed:            {before - after}")


# ------------------------------------------------------------
# Sort chronologically
# ------------------------------------------------------------

combined_df = combined_df.sort_values(
    by=[
        "season",
        "round",
        "driver"
    ]
).reset_index(drop=True)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

combined_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Final summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("UPDATE COMPLETE")
print("=" * 60)

print(f"\nSaved file:")
print(OUTPUT_FILE)

print(f"\nTotal rows: {len(combined_df)}")

print("\nRows by season:")

print(
    combined_df
    .groupby("season")
    .size()
    .to_string()
)

print("\nRaces by season:")

print(
    combined_df
    .groupby("season")["race_id"]
    .nunique()
    .to_string()
)

print("\nMissing qualifying positions:")

print(
    combined_df["qualifying_position"]
    .isna()
    .sum()
)

print("\nFirst few rows:")

print(
    combined_df.head().to_string(index=False)
)

print("\n" + "=" * 60)
print("READY FOR FEATURE REBUILD")
print("=" * 60)