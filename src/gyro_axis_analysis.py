import pandas as pd
import numpy as np

from load_data import load_smartphone_data, load_vbox_data


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    # ---------------------------------------------------------
    # Convert smartphone gyroscope from rad/s to deg/s
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

    vbox_yaw_rate = vbox["Yaw Rate (deg/sec)"]

    # ---------------------------------------------------------
    # Create comparison dataframe
    # ---------------------------------------------------------

    comparison = pd.DataFrame({

        "GYRO_YAW": gyro_yaw,

        "GYRO_PITCH": gyro_pitch,

        "GYRO_ROLL": gyro_roll,

        "VBOX_YAW_RATE": vbox_yaw_rate

    })

    # ---------------------------------------------------------
    # Correlation analysis
    # ---------------------------------------------------------

    print("GYROSCOPE AXIS VS VBOX YAW RATE")
    print("================================")

    print("\nCORRELATION MATRIX:")

    print(
        comparison.corr()
    )

    # ---------------------------------------------------------
    # Individual correlations
    # ---------------------------------------------------------

    print("\nINDIVIDUAL CORRELATIONS:")

    print(
        "GYRO YAW   :", comparison["GYRO_YAW"].corr(
            comparison["VBOX_YAW_RATE"]
        )
    )

    print(
        "GYRO PITCH :", comparison["GYRO_PITCH"].corr(
            comparison["VBOX_YAW_RATE"]
        )
    )

    print(
        "GYRO ROLL  :", comparison["GYRO_ROLL"].corr(
            comparison["VBOX_YAW_RATE"]
        )
    )

    # ---------------------------------------------------------
    # Absolute correlation strengths
    # ---------------------------------------------------------

    correlations = {

        "GYRO_YAW":
            comparison["GYRO_YAW"].corr(
                comparison["VBOX_YAW_RATE"]
            ),

        "GYRO_PITCH":
            comparison["GYRO_PITCH"].corr(
                comparison["VBOX_YAW_RATE"]
            ),

        "GYRO_ROLL":
            comparison["GYRO_ROLL"].corr(
                comparison["VBOX_YAW_RATE"]
            )

    }

    print("\nABSOLUTE CORRELATION STRENGTH:")

    for axis, correlation in correlations.items():

        print(
            f"{axis}: {abs(correlation):.6f}"
        )

    best_axis = max(
        correlations,
        key=lambda x: abs(correlations[x])
    )

    print("\nBEST CORRELATED SMARTPHONE AXIS:")

    print(best_axis)

    print(
        "Correlation:",
        correlations[best_axis]
    )

    # ---------------------------------------------------------
    # Summary statistics
    # ---------------------------------------------------------

    print("\nSMARTPHONE GYROSCOPE SUMMARY (deg/s):")

    print(
        comparison[
            [
                "GYRO_YAW",
                "GYRO_PITCH",
                "GYRO_ROLL"
            ]
        ].describe()
    )

    print("\nVBOX YAW RATE SUMMARY (deg/s):")

    print(
        comparison[
            "VBOX_YAW_RATE"
        ].describe()
    )

    # ---------------------------------------------------------
    # First 20 samples
    # ---------------------------------------------------------

    print("\nFIRST 20 SAMPLES:")

    print(
        comparison
        .head(20)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Highest VBOX yaw-rate samples
    # ---------------------------------------------------------

    print("\nHIGHEST VBOX YAW RATE SAMPLES:")

    print(
        comparison
        .sort_values(
            "VBOX_YAW_RATE",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Strongest negative VBOX yaw-rate samples
    # ---------------------------------------------------------

    print("\nLOWEST VBOX YAW RATE SAMPLES:")

    print(
        comparison
        .sort_values(
            "VBOX_YAW_RATE",
            ascending=True
        )
        .head(20)
        .to_string(index=False)
    )