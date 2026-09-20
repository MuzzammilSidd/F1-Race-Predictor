import pandas as pd
import numpy as np

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)

from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("f1_training_dataset.csv")

print(f"Dataset shape: {df.shape}")


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
# MODEL DEFINITIONS
# ============================================================

def create_models():

    models = {

        "Random Forest": RandomForestRegressor(
            n_estimators=400,
            max_depth=8,
            max_features="sqrt",
            min_samples_leaf=1,
            min_samples_split=2,
            random_state=42,
            n_jobs=-1
        ),

        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=3,
            min_samples_leaf=3,
            min_samples_split=4,
            loss="huber",
            random_state=42
        ),

        "Hist Gradient Boosting": HistGradientBoostingRegressor(
            max_iter=300,
            learning_rate=0.05,
            max_leaf_nodes=15,
            min_samples_leaf=10,
            l2_regularization=1.0,
            random_state=42
        )
    }

    return models


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(model, train, test):

    X_train = train[features].copy()
    y_train = train[target].copy()

    X_test = test[features].copy()
    y_test = test[target].copy()


    # --------------------------------------------------------
    # TRAINING-ONLY MEDIAN IMPUTATION
    # --------------------------------------------------------

    medians = X_train.median()

    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    model.fit(X_train, y_train)

    predicted_position_change = model.predict(X_test)


    # --------------------------------------------------------
    # CREATE RESULTS
    # --------------------------------------------------------

    results = test[
        [
            "race_id",
            "driver",
            "grid_position",
            "qualifying_position",
            "position_change"
        ]
    ].copy()

    results["predicted_position_change"] = (
        predicted_position_change
    )

    results["actual_finish"] = (
        results["grid_position"]
        - results["position_change"]
    )

    results["predicted_finish_raw"] = (
        results["grid_position"]
        - results["predicted_position_change"]
    )


    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------

    baseline_mae = mean_absolute_error(
        results["actual_finish"],
        results["grid_position"]
    )

    baseline_rmse = np.sqrt(
        mean_squared_error(
            results["actual_finish"],
            results["grid_position"]
        )
    )


    # --------------------------------------------------------
    # RACE-LEVEL RANKING
    # --------------------------------------------------------

    results["predicted_finish"] = (
        results
        .groupby("race_id")["predicted_finish_raw"]
        .rank(method="first")
    )


    # --------------------------------------------------------
    # MODEL METRICS
    # --------------------------------------------------------

    mae = mean_absolute_error(
        results["actual_finish"],
        results["predicted_finish"]
    )

    rmse = np.sqrt(
        mean_squared_error(
            results["actual_finish"],
            results["predicted_finish"]
        )
    )


    # --------------------------------------------------------
    # POSITION ACCURACY
    # --------------------------------------------------------

    error = (
        results["predicted_finish"]
        - results["actual_finish"]
    ).abs()

    exact = (
        error == 0
    ).mean() * 100

    within_one = (
        error <= 1
    ).mean() * 100

    within_two = (
        error <= 2
    ).mean() * 100


    # --------------------------------------------------------
    # PODIUM
    # --------------------------------------------------------

    actual_podium = (
        results["actual_finish"] <= 3
    )

    predicted_podium = (
        results["predicted_finish"] <= 3
    )

    true_podium = (
        actual_podium & predicted_podium
    ).sum()

    podium_precision = (
        true_podium
        / predicted_podium.sum()
        * 100
    )

    podium_recall = (
        true_podium
        / actual_podium.sum()
        * 100
    )


    # --------------------------------------------------------
    # TOP 5
    # --------------------------------------------------------

    actual_top5 = (
        results["actual_finish"] <= 5
    )

    predicted_top5 = (
        results["predicted_finish"] <= 5
    )

    true_top5 = (
        actual_top5 & predicted_top5
    ).sum()

    top5_precision = (
        true_top5
        / predicted_top5.sum()
        * 100
    )

    top5_recall = (
        true_top5
        / actual_top5.sum()
        * 100
    )


    return {
        "model": model,
        "baseline_mae": baseline_mae,
        "baseline_rmse": baseline_rmse,
        "mae": mae,
        "rmse": rmse,
        "exact": exact,
        "within_one": within_one,
        "within_two": within_two,
        "podium_precision": podium_precision,
        "podium_recall": podium_recall,
        "top5_precision": top5_precision,
        "top5_recall": top5_recall,
        "results": results
    }


# ============================================================
# RUN VALIDATION
# ============================================================

def run_validation(train, test, validation_name):

    print()
    print("=" * 65)
    print(validation_name)
    print("=" * 65)

    print(
        f"Training rows: {len(train)}"
    )

    print(
        f"Testing rows: {len(test)}"
    )


    models = create_models()

    all_results = []


    for model_name, model in models.items():

        print()
        print(f"Training {model_name}...")

        result = evaluate_model(
            model,
            train,
            test
        )

        result["model_name"] = model_name

        all_results.append(result)


    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------

    baseline_mae = all_results[0]["baseline_mae"]
    baseline_rmse = all_results[0]["baseline_rmse"]

    print()
    print("---------- GRID BASELINE ----------")
    print(f"MAE: {baseline_mae:.3f}")
    print(f"RMSE: {baseline_rmse:.3f}")


    # --------------------------------------------------------
    # COMPARISON TABLE
    # --------------------------------------------------------

    comparison = []

    for result in all_results:

        comparison.append({
            "Model": result["model_name"],
            "MAE": round(result["mae"], 3),
            "RMSE": round(result["rmse"], 3),
            "Exact %": round(result["exact"], 2),
            "Within ±1 %": round(result["within_one"], 2),
            "Within ±2 %": round(result["within_two"], 2),
            "Podium %": round(result["podium_precision"], 2),
            "Top-5 %": round(result["top5_precision"], 2)
        })

    comparison_df = pd.DataFrame(comparison)


    print()
    print("---------- MODEL COMPARISON ----------")
    print(
        comparison_df.to_string(index=False)
    )


    # --------------------------------------------------------
    # BEST MODEL BY MAE
    # --------------------------------------------------------

    best_result = min(
        all_results,
        key=lambda x: x["mae"]
    )

    print()
    print("---------- BEST MODEL ----------")
    print(
        f"Model: {best_result['model_name']}"
    )

    print(
        f"MAE: {best_result['mae']:.3f}"
    )

    print(
        f"RMSE: {best_result['rmse']:.3f}"
    )

    print(
        f"Within ±1: "
        f"{best_result['within_one']:.2f} %"
    )

    print(
        f"Within ±2: "
        f"{best_result['within_two']:.2f} %"
    )


    return all_results


# ============================================================
# VALIDATION 1
# 2022 → 2023
# ============================================================

train_2022 = df[
    df["season"] == 2022
].copy()

test_2023 = df[
    df["season"] == 2023
].copy()

results_2023 = run_validation(
    train_2022,
    test_2023,
    "VALIDATION 1: 2022 → 2023"
)


# ============================================================
# VALIDATION 2
# 2022 + 2023 → 2024
# ============================================================

train_2024 = df[
    df["season"].isin([2022, 2023])
].copy()

test_2024 = df[
    df["season"] == 2024
].copy()

results_2024 = run_validation(
    train_2024,
    test_2024,
    "VALIDATION 2: 2022 + 2023 → 2024"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 65)
print("MODEL COMPARISON COMPLETE")
print("=" * 65)

print()
print(
    "We compared three different regression approaches "
    "using the same features and chronological validation."
)

print()
print("Next step: choose the model based on the validation results.")