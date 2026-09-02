import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from load_data import load_smartphone_data, load_vbox_data


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()
vbox = load_vbox_data()


# ============================================================
# PREPARE GYROSCOPE DATA
# ============================================================

# Convert smartphone gyroscope values from rad/s to deg/s
gyro_yaw = smartphone["GYROSCOPE Yaw (rad/s)"] * (180 / np.pi)
gyro_pitch = smartphone["GYROSCOPE Pitch (rad/s)"] * (180 / np.pi)
gyro_roll = smartphone["GYROSCOPE Roll (rad/s)"] * (180 / np.pi)

# VBOX reference yaw rate
vbox_yaw = vbox["Yaw Rate (deg/sec)"]


# ============================================================
# CREATE FEATURE MATRIX
# ============================================================

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
# THREE-AXIS LINEAR REGRESSION
# ============================================================

model = LinearRegression()

model.fit(X, y)

prediction = model.predict(X)


# ============================================================
# MODEL PARAMETERS
# ============================================================

print("GYROSCOPE 3-AXIS CALIBRATION")
print("============================")

print("\nMODEL:")

print(
    f"VBOX_YAW_RATE = "
    f"{model.coef_[0]:.6f} * GYRO_YAW + "
    f"{model.coef_[1]:.6f} * GYRO_PITCH + "
    f"{model.coef_[2]:.6f} * GYRO_ROLL + "
    f"{model.intercept_:.6f}"
)


print("\nCOEFFICIENTS:")

print(f"GYRO_YAW   : {model.coef_[0]:.6f}")
print(f"GYRO_PITCH : {model.coef_[1]:.6f}")
print(f"GYRO_ROLL  : {model.coef_[2]:.6f}")

print(f"\nINTERCEPT  : {model.intercept_:.6f}")


# ============================================================
# MODEL PERFORMANCE
# ============================================================

r2 = r2_score(y, prediction)

mae = mean_absolute_error(y, prediction)

median_ae = np.median(
    np.abs(y.to_numpy() - prediction)
)

rmse = np.sqrt(
    mean_squared_error(y, prediction)
)

max_error = np.max(
    np.abs(y.to_numpy() - prediction)
)


print("\nMODEL PERFORMANCE:")

print(f"R-SQUARED           : {r2:.6f}")
print(f"MEAN ABSOLUTE ERROR : {mae:.6f} deg/s")
print(f"MEDIAN ABS ERROR    : {median_ae:.6f} deg/s")
print(f"RMSE                : {rmse:.6f} deg/s")
print(f"MAX ABS ERROR       : {max_error:.6f} deg/s")


# ============================================================
# ERROR ANALYSIS
# ============================================================

error = y.to_numpy() - prediction

absolute_error = np.abs(error)


results = X.copy()

results["VBOX_YAW_RATE"] = y.to_numpy()

results["PREDICTED_YAW_RATE"] = prediction

results["ERROR"] = error

results["ABSOLUTE_ERROR"] = absolute_error


# ============================================================
# FIRST 20 CALIBRATED SAMPLES
# ============================================================

print("\nFIRST 20 CALIBRATED SAMPLES:")

print(
    results[
        [
            "GYRO_YAW",
            "GYRO_PITCH",
            "GYRO_ROLL",
            "VBOX_YAW_RATE",
            "PREDICTED_YAW_RATE",
            "ERROR",
            "ABSOLUTE_ERROR"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# LARGEST CALIBRATION ERRORS
# ============================================================

print("\nLARGEST CALIBRATION ERRORS:")

print(
    results
    .sort_values(
        "ABSOLUTE_ERROR",
        ascending=False
    )
    [
        [
            "GYRO_YAW",
            "GYRO_PITCH",
            "GYRO_ROLL",
            "VBOX_YAW_RATE",
            "PREDICTED_YAW_RATE",
            "ERROR",
            "ABSOLUTE_ERROR"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# COEFFICIENT IMPORTANCE
# ============================================================

print("\nABSOLUTE COEFFICIENT MAGNITUDES:")

print(f"GYRO_YAW   : {abs(model.coef_[0]):.6f}")
print(f"GYRO_PITCH : {abs(model.coef_[1]):.6f}")
print(f"GYRO_ROLL  : {abs(model.coef_[2]):.6f}")


# ============================================================
# SAVE CALIBRATION
# ============================================================

calibration = pd.DataFrame({
    "GYRO_AXIS": [
        "GYRO_YAW",
        "GYRO_PITCH",
        "GYRO_ROLL"
    ],
    "COEFFICIENT": model.coef_
})

calibration["INTERCEPT"] = model.intercept_


calibration.to_csv(
    "data/processed/gyro_3axis_calibration.csv",
    index=False
)


print("\nCalibration saved to:")

print(
    "data/processed/gyro_3axis_calibration.csv"
)