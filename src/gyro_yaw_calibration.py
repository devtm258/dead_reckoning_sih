import pandas as pd
import numpy as np

from load_data import load_smartphone_data, load_vbox_data


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    # ---------------------------------------------------------
    # Smartphone Gyroscope Pitch
    # Convert rad/s -> deg/s
    # ---------------------------------------------------------

    smartphone_gyro_pitch = np.degrees(
        smartphone["GYROSCOPE Pitch (rad/s)"]
    )

    # ---------------------------------------------------------
    # VBOX reference yaw rate
    # ---------------------------------------------------------

    vbox_yaw_rate = vbox["Yaw Rate (deg/sec)"]

    # ---------------------------------------------------------
    # Create comparison dataframe
    # ---------------------------------------------------------

    data = pd.DataFrame({
        "SMARTPHONE_GYRO_PITCH": smartphone_gyro_pitch,
        "VBOX_YAW_RATE": vbox_yaw_rate
    })

    # ---------------------------------------------------------
    # Linear regression
    #
    # VBOX_YAW_RATE = slope * GYRO_PITCH + intercept
    # ---------------------------------------------------------

    x = data["SMARTPHONE_GYRO_PITCH"].values
    y = data["VBOX_YAW_RATE"].values

    slope, intercept = np.polyfit(x, y, 1)

    predicted = slope * x + intercept

    residual = y - predicted

    absolute_error = np.abs(residual)

    # ---------------------------------------------------------
    # R²
    # ---------------------------------------------------------

    ss_res = np.sum(residual ** 2)

    ss_tot = np.sum(
        (y - np.mean(y)) ** 2
    )

    r_squared = 1 - (ss_res / ss_tot)

    # ---------------------------------------------------------
    # Print calibration
    # ---------------------------------------------------------

    print("GYROSCOPE PITCH → VBOX YAW RATE CALIBRATION")
    print("============================================")

    print("\nLINEAR MODEL:")

    print(
        f"VBOX_YAW_RATE = "
        f"{slope:.6f} * GYRO_PITCH "
        f"+ {intercept:.6f}"
    )

    print("\nSLOPE:")
    print(slope)

    print("\nINTERCEPT:")
    print(intercept)

    print("\nR-SQUARED:")
    print(r_squared)

    # ---------------------------------------------------------
    # Error statistics
    # ---------------------------------------------------------

    print("\nCALIBRATION ERROR:")

    print(
        "Mean Error:",
        np.mean(residual),
        "deg/s"
    )

    print(
        "Mean Absolute Error:",
        np.mean(absolute_error),
        "deg/s"
    )

    print(
        "Median Absolute Error:",
        np.median(absolute_error),
        "deg/s"
    )

    print(
        "Maximum Absolute Error:",
        np.max(absolute_error),
        "deg/s"
    )

    print(
        "RMSE:",
        np.sqrt(np.mean(residual ** 2)),
        "deg/s"
    )

    # ---------------------------------------------------------
    # Compare original smartphone pitch vs calibrated pitch
    # ---------------------------------------------------------

    data["PREDICTED_VBOX_YAW_RATE"] = predicted
    data["ERROR"] = residual
    data["ABSOLUTE_ERROR"] = absolute_error

    print("\nFIRST 20 CALIBRATED SAMPLES:")

    print(
        data.head(20).to_string(index=False)
    )

    # ---------------------------------------------------------
    # Best and worst calibration samples
    # ---------------------------------------------------------

    print("\nLOWEST CALIBRATION ERRORS:")

    print(
        data.sort_values(
            "ABSOLUTE_ERROR",
            ascending=True
        )
        .head(10)
        .to_string(index=False)
    )

    print("\nHIGHEST CALIBRATION ERRORS:")

    print(
        data.sort_values(
            "ABSOLUTE_ERROR",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )