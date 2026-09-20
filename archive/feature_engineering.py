import pandas as pd

df = pd.read_csv("f1_2024_raw.csv")

print(df.head())
print("\nDataset shape:", df.shape)
# Sort the data chronologically
df = df.sort_values(["driver", "round"])

# Calculate the average finish from the previous 3 races
df["recent_avg_finish"] = (
    df.groupby("driver")["finish_position"]
      .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

print("\nRecent form:")
print(
    df[
        [
            "driver",
            "round",
            "finish_position",
            "recent_avg_finish"
        ]
    ].head(20)
)
# Calculate the average qualifying position from the previous 3 races
df["recent_avg_qualifying"] = (
    df.groupby("driver")["qualifying_position"]
      .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

print("\nRecent qualifying form:")
print(
    df[
        [
            "driver",
            "round",
            "qualifying_position",
            "recent_avg_qualifying"
        ]
    ].head(20)
)
# Calculate constructor performance from previous 3 races
constructor_race_avg = (
    df.groupby(["constructor", "round"])["finish_position"]
      .mean()
      .reset_index()
      .rename(columns={"finish_position": "constructor_race_avg_finish"})
)

# Shift the constructor's race performance so the current race is not included
constructor_race_avg["recent_avg_constructor_finish"] = (
    constructor_race_avg.groupby("constructor")["constructor_race_avg_finish"]
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

# Merge the constructor feature back into the main dataset
df = df.merge(
    constructor_race_avg[
        [
            "constructor",
            "round",
            "recent_avg_constructor_finish"
        ]
    ],
    on=["constructor", "round"],
    how="left"
)

print("\nConstructor form:")
print(
    df[
        [
            "driver",
            "constructor",
            "round",
            "finish_position",
            "recent_avg_constructor_finish"
        ]
    ].head(20)
)