import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("f1_training_dataset.csv")


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
# PREPARE DATA
# ============================================================

X = df[features].copy()
y = df[target].copy()


# ============================================================
# FINAL-DATASET MEDIAN IMPUTATION
# ============================================================

# The model is now being trained on the complete historical
# dataset available to us (2022-2026 through Spain).
#
# Therefore the medians are calculated from the full training
# dataset and saved for use when making future predictions.

medians = X.median()

X = X.fillna(medians)


# ============================================================
# CREATE FINAL RANDOM FOREST
# ============================================================

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=8,
    max_features="sqrt",
    min_samples_leaf=1,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)


# ============================================================
# TRAIN
# ============================================================

print("=" * 60)
print("TRAINING FINAL RANDOM FOREST")
print("=" * 60)

print(f"Training rows: {len(df)}")
print(f"Features: {len(features)}")

print()
print("Training model...")

model.fit(X, y)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    "f1_random_forest_model.pkl"
)

joblib.dump(
    medians,
    "f1_feature_medians.pkl"
)

joblib.dump(
    features,
    "f1_features.pkl"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 60)
print("FINAL MODEL TRAINED")
print("=" * 60)

print(f"Training rows: {len(df)}")
print(f"Features: {len(features)}")
print("Model: Random Forest")
print("Trees: 400")
print("Max depth: 8")
print('Max features: "sqrt"')
print("Random state: 42")

print()
print("Saved files:")
print("  f1_random_forest_model.pkl")
print("  f1_feature_medians.pkl")
print("  f1_features.pkl")

print()
print("=" * 60)
print("PRODUCTION MODEL READY")
print("=" * 60)