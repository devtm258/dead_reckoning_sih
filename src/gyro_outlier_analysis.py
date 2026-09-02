import pandas as pd
import numpy as np

from load_data import load_smartphone_data, load_vbox_data


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    # ---------------------------------------------------------
    # Convert gyroscope values to deg/s
    # ---------------------------------------------------------

    gyro_yaw = np.degrees(
        smartphone["GYROSCOPE Yaw (rad/s)"]
    )

    gyro_pitch = np.degrees(
        smartphone["GYROSCOPE Pitch (rad/s)"]
    )

    gyro_roll = np.degrees(
        smartphone["GYROSCOPE Roll (rad/s)"]
    )

    vbox_yaw = vbox["Yaw Rate (deg/sec)"]

    # ---------------------------------------------------------
    # Create analysis dataframe
    # ---------------------------------------------------------

    data = pd.DataFrame({

        "GYRO_YAW": gyro_yaw,

        "GYRO_PITCH": gyro_pitch,

        "GYRO_ROLL": gyro_roll,

        "VBOX_YAW_RATE": vbox_yaw,

        "GRAVITY_X":
            smartphone["GRAVITY X (m/s²)"],

        "GRAVITY_Y":
            smartphone["GRAVITY Y (m/s²)"],

        "GRAVITY_Z":
            smartphone["GRAVITY Z (m/s²)"],

        "ORIENTATION_YAW":
            smartphone["ORIENTATION (Yaw) (Â°)"],

        "ORIENTATION_PITCH":
            smartphone["ORIENTATION (Pitch) (Â°)"],

        "ORIENTATION_ROLL":
            smartphone["ORIENTATION (Roll ) (Â°)"],

        "GPS_SPEED":
            smartphone["GPS SPEED (Kmh)"]

    })

    # ---------------------------------------------------------
    # Predicted VBOX yaw rate using calibration
    # ---------------------------------------------------------

    slope = 0.8882434344455002
    intercept = 0.2690709862331858

    data["PREDICTED_YAW"] = (
        slope * data["GYRO_PITCH"]
        + intercept
    )

    # ---------------------------------------------------------
    # Calibration residual
    # ---------------------------------------------------------

    data["ERROR"] = (
        data["VBOX_YAW_RATE"]
        - data["PREDICTED_YAW"]
    )

    data["ABS_ERROR"] = data["ERROR"].abs()

    # ---------------------------------------------------------
    # Identify large gyro-pitch events
    # ---------------------------------------------------------

    data["LARGE_PITCH"] = (
        data["GYRO_PITCH"].abs() > 20
    )

    # ---------------------------------------------------------
    # Identify large calibration errors
    # ---------------------------------------------------------

    data["LARGE_ERROR"] = (
        data["ABS_ERROR"] > 10
    )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    print("GYROSCOPE OUTLIER ANALYSIS")
    print("==========================")

    print(
        "\nNUMBER OF LARGE GYRO PITCH SAMPLES (>20 deg/s):"
    )

    print(
        data["LARGE_PITCH"].sum()
    )

    print(
        "\nPERCENTAGE:"
    )

    print(
        data["LARGE_PITCH"].mean() * 100
    )

    print(
        "\nNUMBER OF LARGE CALIBRATION ERRORS (>10 deg/s):"
    )

    print(
        data["LARGE_ERROR"].sum()
    )

    print(
        "\nPERCENTAGE:"
    )

    print(
        data["LARGE_ERROR"].mean() * 100
    )

    # ---------------------------------------------------------
    # Large Pitch samples
    # ---------------------------------------------------------

    print(
        "\nLARGE GYRO PITCH SAMPLES:"
    )

    columns = [
        "GYRO_PITCH",
        "GYRO_YAW",
        "GYRO_ROLL",
        "VBOX_YAW_RATE",
        "GRAVITY_X",
        "GRAVITY_Y",
        "GRAVITY_Z",
        "ORIENTATION_PITCH",
        "ORIENTATION_ROLL",
        "GPS_SPEED",
        "ABS_ERROR"
    ]

    print(
        data[
            data["LARGE_PITCH"]
        ]
        .sort_values(
            "GYRO_PITCH",
            key=lambda x: x.abs(),
            ascending=False
        )
        [columns]
        .head(30)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Largest calibration errors
    # ---------------------------------------------------------

    print(
        "\nLARGEST CALIBRATION ERRORS:"
    )

    print(
        data
        .sort_values(
            "ABS_ERROR",
            ascending=False
        )
        [columns]
        .head(30)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Correlation of VBOX yaw with other phone signals
    # ---------------------------------------------------------

    print(
        "\nCORRELATION WITH VBOX YAW RATE:"
    )

    correlation_columns = [
        "GYRO_YAW",
        "GYRO_PITCH",
        "GYRO_ROLL",
        "GRAVITY_X",
        "GRAVITY_Y",
        "GRAVITY_Z",
        "ORIENTATION_YAW",
        "ORIENTATION_PITCH",
        "ORIENTATION_ROLL",
        "GPS_SPEED"
    ]

    print(
        data[
            correlation_columns +
            ["VBOX_YAW_RATE"]
        ]
        .corr()["VBOX_YAW_RATE"]
        .sort_values(
            ascending=False
        )
    )

    # ---------------------------------------------------------
    # Relationship at different speed ranges
    # ---------------------------------------------------------

    data["SPEED_RANGE"] = pd.cut(
        data["GPS_SPEED"],
        bins=[-1, 5, 10, 15, 20],
        labels=[
            "0-5",
            "5-10",
            "10-15",
            "15-20"
        ]
    )

    print(
        "\nCALIBRATION ERROR BY SPEED RANGE:"
    )

    print(
        data
        .groupby(
            "SPEED_RANGE",
            observed=False
        )["ABS_ERROR"]
        .agg(
            ["count", "mean", "median", "max"]
        )
    )