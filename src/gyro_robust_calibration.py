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
# PREPARE GYROSCOPE DATA
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
# REMOVE NaN VALUES
# ============================================================

valid = X.notna().all(axis=1) & y.notna()

X = X.loc[valid].reset_index(drop=True)
y = y.loc[valid].reset_index(drop=True)


# ============================================================
# BASELINE MODEL
# ============================================================

baseline_model = LinearRegression()

baseline_model.fit(X, y)

baseline_prediction = baseline_model.predict(X)

baseline_error = y.to_numpy() - baseline_prediction
baseline_abs_error = np.abs(baseline_error)


# ============================================================
# OUTLIER ANALYSIS
# ============================================================

# Large smartphone gyro measurements are treated as potential
# sensor/frame anomalies for this calibration experiment.

gyro_outlier = (
    (np.abs(X["GYRO_YAW"]) > 20) |
    (np.abs(X["GYRO_PITCH"]) > 20) |
    (np.abs(X["GYRO_ROLL"]) > 20)
)

calibration_outlier = baseline_abs_error > 10

print("ROBUST GYROSCOPE CALIBRATION")
print("============================")

print("\nBASELINE MODEL:")
print(
    f"VBOX_YAW_RATE = "
    f"{baseline_model.coef_[0]:.6f} * GYRO_YAW + "
    f"{baseline_model.coef_[1]:.6f} * GYRO_PITCH + "
    f"{baseline_model.coef_[2]:.6f} * GYRO_ROLL + "
    f"{baseline_model.intercept_:.6f}"
)

print("\nOUTLIER COUNTS:")

print(
    f"GYRO OUTLIER SAMPLES (>20 deg/s): "
    f"{gyro_outlier.sum()}"
)

print(
    f"CALIBRATION ERROR OUTLIERS (>10 deg/s): "
    f"{calibration_outlier.sum()}"
)


# ============================================================
# CREATE ROBUST TRAINING DATA
# ============================================================

robust_mask = ~gyro_outlier

X_robust = X.loc[robust_mask].reset_index(drop=True)
y_robust = y.loc[robust_mask].reset_index(drop=True)


print(
    f"\nORIGINAL SAMPLES: "
    f"{len(X)}"
)

print(
    f"ROBUST TRAINING SAMPLES: "
    f"{len(X_robust)}"
)

print(
    f"REMOVED SAMPLES: "
    f"{len(X) - len(X_robust)}"
)

print(
    f"REMOVED PERCENTAGE: "
    f"{(len(X) - len(X_robust)) / len(X) * 100:.4f}%"
)


# ============================================================
# ROBUST MODEL
# ============================================================

robust_model = LinearRegression()

robust_model.fit(X_robust, y_robust)

robust_prediction = robust_model.predict(X_robust)


# ============================================================
# ROBUST MODEL PARAMETERS
# ============================================================

print("\n\nROBUST MODEL:")
print(
    f"VBOX_YAW_RATE = "
    f"{robust_model.coef_[0]:.6f} * GYRO_YAW + "
    f"{robust_model.coef_[1]:.6f} * GYRO_PITCH + "
    f"{robust_model.coef_[2]:.6f} * GYRO_ROLL + "
    f"{robust_model.intercept_:.6f}"
)

print("\nROBUST COEFFICIENTS:")

print(
    f"GYRO_YAW   : "
    f"{robust_model.coef_[0]:.6f}"
)

print(
    f"GYRO_PITCH : "
    f"{robust_model.coef_[1]:.6f}"
)

print(
    f"GYRO_ROLL  : "
    f"{robust_model.coef_[2]:.6f}"
)

print(
    f"\nINTERCEPT  : "
    f"{robust_model.intercept_:.6f}"
)


# ============================================================
# ROBUST MODEL PERFORMANCE
# ============================================================

r2 = r2_score(y_robust, robust_prediction)

mae = mean_absolute_error(y_robust, robust_prediction)

median_ae = np.median(
    np.abs(y_robust.to_numpy() - robust_prediction)
)

rmse = np.sqrt(
    mean_squared_error(y_robust, robust_prediction)
)

max_error = np.max(
    np.abs(y_robust.to_numpy() - robust_prediction)
)


print("\nROBUST MODEL PERFORMANCE:")

print(f"R-SQUARED           : {r2:.6f}")
print(f"MEAN ABSOLUTE ERROR : {mae:.6f} deg/s")
print(f"MEDIAN ABS ERROR    : {median_ae:.6f} deg/s")
print(f"RMSE                : {rmse:.6f} deg/s")
print(f"MAX ABS ERROR       : {max_error:.6f} deg/s")


# ============================================================
# BASELINE VS ROBUST
# ============================================================

baseline_r2 = r2_score(y, baseline_prediction)

baseline_mae = mean_absolute_error(
    y,
    baseline_prediction
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y,
        baseline_prediction
    )
)


print("\n\nBASELINE VS ROBUST:")
print("===================")

print(
    f"Baseline R² : {baseline_r2:.6f}"
)

print(
    f"Robust R²   : {r2:.6f}"
)

print(
    f"Baseline MAE: {baseline_mae:.6f} deg/s"
)

print(
    f"Robust MAE  : {mae:.6f} deg/s"
)

print(
    f"Baseline RMSE: {baseline_rmse:.6f} deg/s"
)

print(
    f"Robust RMSE  : {rmse:.6f} deg/s"
)


# ============================================================
# SAVE ROBUST CALIBRATION
# ============================================================

calibration = pd.DataFrame({
    "GYRO_AXIS": [
        "GYRO_YAW",
        "GYRO_PITCH",
        "GYRO_ROLL"
    ],
    "COEFFICIENT": robust_model.coef_
})

calibration["INTERCEPT"] = robust_model.intercept_

calibration.to_csv(
    "data/processed/gyro_robust_calibration.csv",
    index=False
)


print("\nRobust calibration saved to:")
print(
    "data/processed/gyro_robust_calibration.csv"
)