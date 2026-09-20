import pandas as pd
import numpy as np

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("f1_2022_2026_raw.csv")

# ============================================================
# IMPORTANT:
# REMOVE 2026 SPANISH GP AND EVERYTHING AFTER IT
#
# Spain = 2026 Round 14
# Therefore the model's latest known race will be:
# 2026 Round 13 = Italian GP
# ============================================================

df = df[
    ~(
        (df["season"] == 2026)
        & (df["round"] >= 14)
    )
].copy()

# Create a stable race identifier
df["race_id"] = (
    df["season"].astype(str)
    + "_"
    + df["round"].astype(str)
)

# Sort races chronologically
df = df.sort_values(
    ["season", "round", "driver"]
).reset_index(drop=True)

print("=" * 60)
print("BUILDING LEAKAGE-SAFE TRAINING DATASET")
print("=" * 60)

print(f"Raw rows after Spain cutoff: {len(df)}")
print(f"Raw races after Spain cutoff: {df['race_id'].nunique()}")
print(
    f"Latest race included: "
    f"2026 Round {df[df['season'] == 2026]['round'].max()}"
)

# ============================================================
# TARGET
# ============================================================

df["position_change"] = (
    df["grid_position"] - df["finish_position"]
)

# ============================================================
# 1. DRIVER RECENT FORM
# ============================================================

df["recent_avg_finish"] = (
    df.groupby("driver")["finish_position"]
      .transform(
          lambda x: x.shift(1).rolling(3, min_periods=1).mean()
      )
)

df["recent_finish_std"] = (
    df.groupby("driver")["finish_position"]
      .transform(
          lambda x: x.shift(1).rolling(3, min_periods=2).std()
      )
)

df["recent_avg_qualifying"] = (
    df.groupby("driver")["qualifying_position"]
      .transform(
          lambda x: x.shift(1).rolling(3, min_periods=1).mean()
      )
)

# ============================================================
# 2. DRIVER RECENT POSITION CHANGE
# ============================================================

df["recent_avg_position_change"] = (
    df.groupby("driver")["position_change"]
      .transform(
          lambda x: x.shift(1).rolling(3, min_periods=1).mean()
      )
)

# ============================================================
# 3. QUALIFYING → FINISH HISTORY
# ============================================================

df["qualifying_to_finish_gap"] = (
    df["qualifying_position"] - df["finish_position"]
)

df["recent_avg_qualifying_to_finish"] = (
    df.groupby("driver")["qualifying_to_finish_gap"]
      .transform(
          lambda x: x.shift(1).rolling(3, min_periods=1).mean()
      )
)

# ============================================================
# 4. CONSTRUCTOR RACE-LEVEL HISTORY
# ============================================================

constructor_race = (
    df.groupby(["constructor", "race_id"], as_index=False)
      .agg(
          constructor_race_finish=("finish_position", "mean"),
          constructor_race_qualifying=("qualifying_position", "mean")
      )
)

# Restore chronological order using season + round
race_order = (
    df[["race_id", "season", "round"]]
    .drop_duplicates("race_id")
    .sort_values(["season", "round", "race_id"])
)

constructor_race = constructor_race.merge(
    race_order,
    on="race_id",
    how="left"
)

constructor_race = constructor_race.sort_values(
    ["constructor", "season", "round", "race_id"]
)

# IMPORTANT:
# shift(1) means the current race is NOT included.
constructor_race["recent_avg_constructor_finish"] = (
    constructor_race.groupby("constructor")[
        "constructor_race_finish"
    ]
    .transform(
        lambda x: x.shift(1).rolling(3, min_periods=1).mean()
    )
)

constructor_race["recent_avg_constructor_qualifying"] = (
    constructor_race.groupby("constructor")[
        "constructor_race_qualifying"
    ]
    .transform(
        lambda x: x.shift(1).rolling(3, min_periods=1).mean()
    )
)

df = df.merge(
    constructor_race[
        [
            "constructor",
            "race_id",
            "recent_avg_constructor_finish",
            "recent_avg_constructor_qualifying"
        ]
    ],
    on=["constructor", "race_id"],
    how="left"
)

# ============================================================
# 5. DRIVER CIRCUIT HISTORY
# ============================================================

df["driver_circuit_history"] = (
    df.groupby(["driver", "circuit"])["finish_position"]
      .transform(
          lambda x: x.shift(1).expanding().mean()
      )
)

# ============================================================
# 6. CIRCUIT-WIDE HISTORICAL POSITION CHANGE
# ============================================================

circuit_race = (
    df.groupby(["circuit", "race_id"], as_index=False)
      .agg(
          circuit_race_position_change=("position_change", "mean")
      )
)

circuit_race = circuit_race.merge(
    race_order,
    on="race_id",
    how="left"
)

circuit_race = circuit_race.sort_values(
    ["circuit", "season", "round", "race_id"]
)

circuit_race["circuit_avg_position_change"] = (
    circuit_race.groupby("circuit")[
        "circuit_race_position_change"
    ]
    .transform(
        lambda x: x.shift(1).expanding().mean()
    )
)

df = df.merge(
    circuit_race[
        [
            "circuit",
            "race_id",
            "circuit_avg_position_change"
        ]
    ],
    on=["circuit", "race_id"],
    how="left"
)

# ============================================================
# 7. DRIVER + CIRCUIT POSITION CHANGE HISTORY
# ============================================================

df["driver_circuit_avg_position_change"] = (
    df.groupby(["driver", "circuit"])["position_change"]
      .transform(
          lambda x: x.shift(1).expanding().mean()
      )
)

# ============================================================
# 8. PRE-RACE QUALIFYING / GRID INFORMATION
# ============================================================

df["qualifying_grid_gap"] = (
    df["grid_position"] - df["qualifying_position"]
)

# ============================================================
# FEATURES
# ============================================================

features = [
    "grid_position",
    "qualifying_position",
    "qualifying_grid_gap",
    "recent_avg_finish",
    "recent_finish_std",
    "recent_avg_qualifying",
    "recent_avg_qualifying_to_finish",
    "recent_avg_constructor_finish",
    "recent_avg_constructor_qualifying",
    "driver_circuit_history",
    "circuit_avg_position_change",
    "driver_circuit_avg_position_change",
    "recent_avg_position_change"
]

target = "position_change"

# ============================================================
# DATASET AUDIT
# ============================================================

dataset = df[
    features
    + [
        target,
        "season",
        "round",
        "race_id",
        "driver"
    ]
].copy()

print()
print("=" * 60)
print("PRE-IMPUTATION AUDIT")
print("=" * 60)

print("\nMissing values:")
print(dataset[features].isna().sum())

# ============================================================
# MEDIAN IMPUTATION
# ============================================================

for column in features:
    median_value = dataset[column].median()
    dataset[column] = dataset[column].fillna(median_value)

# ============================================================
# FINAL DATASET AUDIT
# ============================================================

print()
print("=" * 60)
print("FINAL DATASET AUDIT")
print("=" * 60)

print(f"\nDataset shape: {dataset.shape}")

print("\nMissing values after imputation:")
print(dataset[features].isna().sum())

print("\nSeason distribution:")
print(dataset["season"].value_counts().sort_index())

print("\nRaces per season:")
print(
    dataset.groupby("season")["race_id"]
    .nunique()
)

print("\nDrivers per race:")
print(
    dataset.groupby("race_id")["driver"]
    .nunique()
    .value_counts()
    .sort_index()
)

print("\nDuplicate driver/race rows:")
print(
    dataset.duplicated(
        subset=["race_id", "driver"]
    ).sum()
)

# ============================================================
# HISTORICAL FEATURE RANGE AUDIT
# ============================================================

print()
print("=" * 60)
print("HISTORICAL FEATURE RANGE AUDIT")
print("=" * 60)

historical_features = [
    "recent_avg_finish",
    "recent_finish_std",
    "recent_avg_qualifying",
    "recent_avg_qualifying_to_finish",
    "recent_avg_constructor_finish",
    "recent_avg_constructor_qualifying",
    "driver_circuit_history",
    "circuit_avg_position_change",
    "driver_circuit_avg_position_change",
    "recent_avg_position_change"
]

for feature in historical_features:
    print(
        f"{feature:40s}"
        f" min={dataset[feature].min():8.3f}"
        f" max={dataset[feature].max():8.3f}"
        f" mean={dataset[feature].mean():8.3f}"
    )

# ============================================================
# SEASON-BY-SEASON HISTORICAL FEATURE AUDIT
# ============================================================

print()
print("=" * 60)
print("SEASON-BY-SEASON HISTORICAL FEATURE AUDIT")
print("=" * 60)

season_summary = (
    dataset
    .groupby("season")[historical_features]
    .mean()
    .round(3)
)

print(season_summary.to_string())

# ============================================================
# COLD-START AUDIT
# ============================================================

print()
print("=" * 60)
print("COLD-START AUDIT")
print("=" * 60)

first_race = (
    dataset
    .sort_values(["season", "round", "driver"])
    .groupby("season")
    .head(20)
)

print(
    "\nFirst-race historical features after median imputation:"
)

print(
    first_race[
        [
            "season",
            "round",
            "driver"
        ] + historical_features
    ].head(20).to_string(index=False)
)

# ============================================================
# SAVE
# ============================================================

dataset.to_csv(
    "f1_training_dataset.csv",
    index=False
)

print()
print("=" * 60)
print("DATASET SAVED")
print("=" * 60)

print("File: f1_training_dataset.csv")
print(f"Rows: {len(dataset)}")
print(f"Columns: {len(dataset.columns)}")
print(f"Races: {dataset['race_id'].nunique()}")

print()
print("BUILD COMPLETE.")