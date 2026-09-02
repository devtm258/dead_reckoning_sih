import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from load_data import load_smartphone_data
from load_data import load_vbox_data


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()
vbox = load_vbox_data()


# ============================================================
# PREPARE DATA
# ============================================================

gyro_yaw = smartphone["GYROSCOPE Yaw (rad/s)"] * (180 / np.pi)
gyro_pitch = smartphone["GYROSCOPE Pitch (rad/s)"] * (180 / np.pi)
gyro_roll = smartphone["GYROSCOPE Roll (rad/s)"] * (180 / np.pi)

vbox_yaw = vbox["Yaw Rate (deg/sec)"]


X = pd.DataFrame({
    "GYRO_YAW": gyro_yaw,
    "GYRO_PITCH": gyro_pitch,
    "GYRO_ROLL": gyro_roll
})

y = vbox_yaw


# ============================================================
# REMOVE INVALID VALUES
# ============================================================

valid = X.notna().all(axis=1) & y.notna()

X = X.loc[valid].reset_index(drop=True)
y = y.loc[valid].reset_index(drop=True)


# ============================================================
# BASELINE MODEL
# TRAINED USING ALL DATA
# ============================================================

baseline_model = LinearRegression()

baseline_model.fit(X, y)

baseline_prediction = baseline_model.predict(X)


# ============================================================
# IDENTIFY GYRO OUTLIERS
# ============================================================

gyro_outlier = (
    (np.abs(X["GYRO_YAW"]) > 20) |
    (np.abs(X["GYRO_PITCH"]) > 20) |
    (np.abs(X["GYRO_ROLL"]) > 20)
)


# ============================================================
# ROBUST MODEL
# TRAINED WITHOUT GYRO OUTLIERS
# ============================================================

X_robust = X.loc[~gyro_outlier]
y_robust = y.loc[~gyro_outlier]

robust_model = LinearRegression()

robust_model.fit(X_robust, y_robust)


# ============================================================
# IMPORTANT:
# EVALUATE ROBUST MODEL ON ALL DATA
# ============================================================

robust_prediction_all = robust_model.predict(X)


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def calculate_metrics(actual, predicted):

    error = actual.to_numpy() - predicted
    absolute_error = np.abs(error)

    return {
        "R2": r2_score(actual, predicted),
        "MAE": mean_absolute_error(actual, predicted),
        "MEDIAN_AE": np.median(absolute_error),
        "RMSE": np.sqrt(
            mean_squared_error(actual, predicted)
        ),
        "MAX_ERROR": np.max(absolute_error)
    }


# ============================================================
# CALCULATE METRICS
# ============================================================

baseline_metrics = calculate_metrics(
    y,
    baseline_prediction
)

robust_metrics = calculate_metrics(
    y,
    robust_prediction_all
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("GYROSCOPE CALIBRATION VALIDATION")
print("================================")


print("\nDATASET:")
print(f"TOTAL SAMPLES          : {len(X)}")
print(f"GYRO OUTLIER SAMPLES   : {gyro_outlier.sum()}")
print(
    f"OUTLIER PERCENTAGE     : "
    f"{gyro_outlier.mean() * 100:.4f}%"
)


# ============================================================
# BASELINE MODEL
# ============================================================

print("\n\nBASELINE MODEL")
print("--------------")

print(
    f"VBOX_YAW_RATE = "
    f"{baseline_model.coef_[0]:.6f} * GYRO_YAW + "
    f"{baseline_model.coef_[1]:.6f} * GYRO_PITCH + "
    f"{baseline_model.coef_[2]:.6f} * GYRO_ROLL + "
    f"{baseline_model.intercept_:.6f}"
)

print(
    f"\nR-SQUARED           : "
    f"{baseline_metrics['R2']:.6f}"
)

print(
    f"MEAN ABS ERROR      : "
    f"{baseline_metrics['MAE']:.6f} deg/s"
)

print(
    f"MEDIAN ABS ERROR    : "
    f"{baseline_metrics['MEDIAN_AE']:.6f} deg/s"
)

print(
    f"RMSE                : "
    f"{baseline_metrics['RMSE']:.6f} deg/s"
)

print(
    f"MAX ABS ERROR       : "
    f"{baseline_metrics['MAX_ERROR']:.6f} deg/s"
)


# ============================================================
# ROBUST MODEL
# ============================================================

print("\n\nROBUST MODEL")
print("------------")

print(
    f"VBOX_YAW_RATE = "
    f"{robust_model.coef_[0]:.6f} * GYRO_YAW + "
    f"{robust_model.coef_[1]:.6f} * GYRO_PITCH + "
    f"{robust_model.coef_[2]:.6f} * GYRO_ROLL + "
    f"{robust_model.intercept_:.6f}"
)

print("\nEVALUATED ON ALL SAMPLES:")

print(
    f"R-SQUARED           : "
    f"{robust_metrics['R2']:.6f}"
)

print(
    f"MEAN ABS ERROR      : "
    f"{robust_metrics['MAE']:.6f} deg/s"
)

print(
    f"MEDIAN ABS ERROR    : "
    f"{robust_metrics['MEDIAN_AE']:.6f} deg/s"
)

print(
    f"RMSE                : "
    f"{robust_metrics['RMSE']:.6f} deg/s"
)

print(
    f"MAX ABS ERROR       : "
    f"{robust_metrics['MAX_ERROR']:.6f} deg/s"
)


# ============================================================
# DIRECT COMPARISON
# ============================================================

print("\n\nFAIR MODEL COMPARISON")
print("=====================")

comparison = pd.DataFrame({
    "METRIC": [
        "R-SQUARED",
        "MAE (deg/s)",
        "MEDIAN ABS ERROR (deg/s)",
        "RMSE (deg/s)",
        "MAX ABS ERROR (deg/s)"
    ],

    "BASELINE": [
        baseline_metrics["R2"],
        baseline_metrics["MAE"],
        baseline_metrics["MEDIAN_AE"],
        baseline_metrics["RMSE"],
        baseline_metrics["MAX_ERROR"]
    ],

    "ROBUST": [
        robust_metrics["R2"],
        robust_metrics["MAE"],
        robust_metrics["MEDIAN_AE"],
        robust_metrics["RMSE"],
        robust_metrics["MAX_ERROR"]
    ]
})

print(comparison.to_string(index=False))


# ============================================================
# IMPROVEMENT
# ============================================================

print("\n\nROBUST MODEL IMPROVEMENT")
print("========================")

mae_improvement = (
    (baseline_metrics["MAE"] - robust_metrics["MAE"])
    / baseline_metrics["MAE"]
) * 100

rmse_improvement = (
    (baseline_metrics["RMSE"] - robust_metrics["RMSE"])
    / baseline_metrics["RMSE"]
) * 100

max_improvement = (
    (baseline_metrics["MAX_ERROR"] - robust_metrics["MAX_ERROR"])
    / baseline_metrics["MAX_ERROR"]
) * 100

r2_change = robust_metrics["R2"] - baseline_metrics["R2"]


print(
    f"MAE CHANGE       : "
    f"{mae_improvement:.2f}%"
)

print(
    f"RMSE CHANGE      : "
    f"{rmse_improvement:.2f}%"
)

print(
    f"MAX ERROR CHANGE : "
    f"{max_improvement:.2f}%"
)

print(
    f"R² CHANGE        : "
    f"{r2_change:.6f}"
)


# ============================================================
# SAVE VALIDATION RESULTS
# ============================================================

comparison.to_csv(
    "data/processed/gyro_calibration_validation.csv",
    index=False
)

print("\nValidation results saved to:")
print(
    "data/processed/gyro_calibration_validation.csv"
)