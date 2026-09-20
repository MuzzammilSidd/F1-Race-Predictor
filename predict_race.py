import pandas as pd
import numpy as np
import joblib


# ============================================================
# LOAD MODEL + DATA
# ============================================================

MODEL_FILE = "f1_random_forest_model.pkl"
MEDIANS_FILE = "f1_feature_medians.pkl"
FEATURES_FILE = "f1_features.pkl"

# IMPORTANT:
# Use the new 2022-2026 historical dataset.
DATA_FILE = "f1_2022_2026_raw.csv"

INPUT_FILE = "race_input.csv"


model = joblib.load(MODEL_FILE)
medians = joblib.load(MEDIANS_FILE)
features = joblib.load(FEATURES_FILE)

history = pd.read_csv(DATA_FILE)


# ============================================================
# CREATE STABLE RACE IDENTIFIER
# ============================================================

history["race_id"] = (
    history["season"].astype(str)
    + "_"
    + history["round"].astype(str)
)


# ============================================================
# SORT HISTORICAL DATA
# ============================================================

history = history.sort_values(
    ["season", "round", "driver"]
).reset_index(drop=True)


# ============================================================
# HISTORICAL TARGET
# ============================================================

history["position_change"] = (
    history["grid_position"]
    - history["finish_position"]
)


# ============================================================
# LOAD RACE INPUT
# ============================================================

race = pd.read_csv(INPUT_FILE)


required_columns = [
    "driver",
    "constructor",
    "circuit",
    "grid_position",
    "qualifying_position"
]


missing_columns = [
    column
    for column in required_columns
    if column not in race.columns
]


if missing_columns:
    raise ValueError(
        "race_input.csv is missing these columns: "
        + ", ".join(missing_columns)
    )


# ============================================================
# START
# ============================================================

print()
print("=" * 60)
print("F1 RACE PREDICTOR")
print("=" * 60)

print()
print(f"Historical rows: {len(history)}")
print(f"Historical races: {history['race_id'].nunique()}")
print(f"Drivers supplied: {len(race)}")


if len(race) < 2:
    raise ValueError(
        "race_input.csv must contain multiple drivers."
    )


# ============================================================
# 1. QUALIFYING → GRID GAP
# ============================================================

race["qualifying_grid_gap"] = (
    race["grid_position"]
    - race["qualifying_position"]
)


# ============================================================
# 2. DRIVER RECENT FORM
# ============================================================

history["recent_avg_finish"] = (
    history
    .groupby("driver")["finish_position"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


history["recent_finish_std"] = (
    history
    .groupby("driver")["finish_position"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=2
        )
        .std()
    )
)


history["recent_avg_qualifying"] = (
    history
    .groupby("driver")["qualifying_position"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


history["recent_avg_position_change"] = (
    history
    .groupby("driver")["position_change"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


# Get latest historical record for each driver.

driver_latest = (
    history
    .sort_values(
        [
            "driver",
            "season",
            "round"
        ]
    )
    .groupby("driver")
    .tail(1)
)


driver_latest = driver_latest[
    [
        "driver",
        "recent_avg_finish",
        "recent_finish_std",
        "recent_avg_qualifying",
        "recent_avg_position_change"
    ]
]


race = race.merge(
    driver_latest,
    on="driver",
    how="left"
)


# ============================================================
# 3. QUALIFYING → FINISH HISTORY
# ============================================================

history["qualifying_to_finish_gap"] = (
    history["qualifying_position"]
    - history["finish_position"]
)


history["recent_avg_qualifying_to_finish"] = (
    history
    .groupby("driver")["qualifying_to_finish_gap"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


qualifying_latest = (
    history
    .sort_values(
        [
            "driver",
            "season",
            "round"
        ]
    )
    .groupby("driver")
    .tail(1)
)


qualifying_latest = qualifying_latest[
    [
        "driver",
        "recent_avg_qualifying_to_finish"
    ]
]


race = race.merge(
    qualifying_latest,
    on="driver",
    how="left"
)


# ============================================================
# 4. CONSTRUCTOR HISTORICAL FEATURES
# ============================================================

constructor_race = (
    history
    .groupby(
        [
            "constructor",
            "race_id"
        ],
        as_index=False
    )
    .agg(
        constructor_race_finish=(
            "finish_position",
            "mean"
        ),
        constructor_race_qualifying=(
            "qualifying_position",
            "mean"
        )
    )
)


# Add chronological ordering information.

race_order = (
    history[
        [
            "race_id",
            "season",
            "round"
        ]
    ]
    .drop_duplicates("race_id")
)


constructor_race = constructor_race.merge(
    race_order,
    on="race_id",
    how="left"
)


constructor_race = constructor_race.sort_values(
    [
        "constructor",
        "season",
        "round"
    ]
)


constructor_race["recent_avg_constructor_finish"] = (
    constructor_race
    .groupby("constructor")[
        "constructor_race_finish"
    ]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


constructor_race["recent_avg_constructor_qualifying"] = (
    constructor_race
    .groupby("constructor")[
        "constructor_race_qualifying"
    ]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


constructor_latest = (
    constructor_race
    .sort_values(
        [
            "constructor",
            "season",
            "round"
        ]
    )
    .groupby("constructor")
    .tail(1)
)


constructor_latest = constructor_latest[
    [
        "constructor",
        "recent_avg_constructor_finish",
        "recent_avg_constructor_qualifying"
    ]
]


race = race.merge(
    constructor_latest,
    on="constructor",
    how="left"
)


# ============================================================
# 5. DRIVER + CIRCUIT HISTORY
# ============================================================

driver_circuit_history = (
    history
    .sort_values(
        [
            "driver",
            "circuit",
            "season",
            "round"
        ]
    )
    .copy()
)


driver_circuit_history[
    "driver_circuit_history"
] = (
    driver_circuit_history
    .groupby(
        [
            "driver",
            "circuit"
        ]
    )["finish_position"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)


driver_circuit_history[
    "driver_circuit_avg_position_change"
] = (
    driver_circuit_history
    .groupby(
        [
            "driver",
            "circuit"
        ]
    )["position_change"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)


driver_circuit_latest = (
    driver_circuit_history
    .sort_values(
        [
            "driver",
            "circuit",
            "season",
            "round"
        ]
    )
    .groupby(
        [
            "driver",
            "circuit"
        ]
    )
    .tail(1)
)


driver_circuit_latest = driver_circuit_latest[
    [
        "driver",
        "circuit",
        "driver_circuit_history",
        "driver_circuit_avg_position_change"
    ]
]


race = race.merge(
    driver_circuit_latest,
    on=[
        "driver",
        "circuit"
    ],
    how="left"
)


# ============================================================
# 6. CIRCUIT-WIDE HISTORICAL POSITION CHANGE
# ============================================================

circuit_race = (
    history
    .groupby(
        [
            "circuit",
            "race_id"
        ],
        as_index=False
    )
    .agg(
        circuit_race_position_change=(
            "position_change",
            "mean"
        )
    )
)


circuit_race = circuit_race.merge(
    race_order,
    on="race_id",
    how="left"
)


circuit_race = circuit_race.sort_values(
    [
        "circuit",
        "season",
        "round"
    ]
)


circuit_race[
    "circuit_avg_position_change"
] = (
    circuit_race
    .groupby("circuit")[
        "circuit_race_position_change"
    ]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)


circuit_latest = (
    circuit_race
    .sort_values(
        [
            "circuit",
            "season",
            "round"
        ]
    )
    .groupby("circuit")
    .tail(1)
)


circuit_latest = circuit_latest[
    [
        "circuit",
        "circuit_avg_position_change"
    ]
]


race = race.merge(
    circuit_latest,
    on="circuit",
    how="left"
)


# ============================================================
# 7. CHECK MODEL FEATURES
# ============================================================

print()
print("Building prediction features...")

missing_features = [
    feature
    for feature in features
    if feature not in race.columns
]


if missing_features:
    raise ValueError(
        "The following model features could not be created: "
        + ", ".join(missing_features)
    )


# ============================================================
# 8. PREPARE MODEL INPUT
# ============================================================

X = race[features].copy()


# ============================================================
# 9. MEDIAN IMPUTATION
# ============================================================

X = X.fillna(medians)


# ============================================================
# 10. PREDICT POSITION CHANGE
# ============================================================

print("Running Random Forest prediction...")

race["predicted_position_change"] = (
    model.predict(X)
)


# ============================================================
# 11. CONVERT TO PREDICTED FINISH
# ============================================================

race["predicted_finish_raw"] = (
    race["grid_position"]
    - race["predicted_position_change"]
)


# ============================================================
# 12. RACE-LEVEL RANKING
# ============================================================

race["predicted_position"] = (
    race["predicted_finish_raw"]
    .rank(method="first")
    .astype(int)
)


# ============================================================
# 13. SORT RESULT
# ============================================================

race = race.sort_values(
    "predicted_position"
)


# ============================================================
# 14. DISPLAY RESULT
# ============================================================

print()
print("---------- PREDICTED RACE RESULT ----------")
print()

for _, row in race.iterrows():

    print(
        f"P{int(row['predicted_position']):2d}  "
        f"{row['driver']:<25} "
        f"(Grid P{int(row['grid_position'])})"
    )


# ============================================================
# 15. SAVE RESULT
# ============================================================

output_columns = [
    "predicted_position",
    "driver",
    "constructor",
    "grid_position",
    "qualifying_position",
    "predicted_position_change",
    "predicted_finish_raw"
]


race[
    output_columns
].to_csv(
    "race_prediction.csv",
    index=False
)


print()
print("=" * 60)
print("PREDICTION SAVED")
print("=" * 60)

print("File: race_prediction.csv")