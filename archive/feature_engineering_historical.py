import pandas as pd

df = pd.read_csv("f1_2022_2024_raw.csv")

# Convert date to a real datetime value
df["date"] = pd.to_datetime(df["date"])

# Sort chronologically
df = df.sort_values("date")

print("Dataset shape:", df.shape)

print("\nSeasons:")
print(df.groupby("season").size())
# Calculate a driver's previous results at the same circuit
df["driver_circuit_history"] = (
    df.groupby(["driver", "circuit"])["finish_position"]
      .transform(
          lambda x: x.shift(1).expanding().mean()
      )
)
# Calculate position change
df["position_change"] = (
    df["grid_position"] - df["finish_position"]
)
# Calculate recent average position change
df["recent_avg_position_change"] = (
    df.groupby("driver")["position_change"]
      .transform(
          lambda x: x.shift(1).rolling(3, min_periods=1).mean()
      )
)
# Fill missing values for a driver's first race
df["recent_avg_position_change"] = (
    df["recent_avg_position_change"].fillna(0)
)

print("\nDriver circuit history:")

print(
    df[
        [
            "driver",
            "circuit",
            "season",
            "round",
            "finish_position",
            "driver_circuit_history"
        ]
    ].head(30)
)
print("\nExamples with previous circuit history:")

print(
    df[df["driver_circuit_history"].notna()][
        [
            "driver",
            "circuit",
            "season",
            "round",
            "finish_position",
            "driver_circuit_history"
        ]
    ].head(20)
)
print("\nRecent average position change:")

print(
    df[
        [
            "driver",
            "round",
            "grid_position",
            "finish_position",
            "position_change",
            "recent_avg_position_change"
        ]
    ].head(20)
)
print("\nExamples with previous position-change history:")

print(
    df[df["recent_avg_position_change"] != 0][
        [
            "driver",
            "season",
            "round",
            "grid_position",
            "finish_position",
            "position_change",
            "recent_avg_position_change"
        ]
    ].head(20)
)