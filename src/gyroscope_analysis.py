import pandas as pd
import numpy as np

from load_data import load_smartphone_data


if __name__ == "__main__":

    smartphone = load_smartphone_data()

    gyro_yaw = smartphone["GYROSCOPE Yaw (rad/s)"]
    gyro_pitch = smartphone["GYROSCOPE Pitch (rad/s)"]
    gyro_roll = smartphone["GYROSCOPE Roll (rad/s)"]

    # Convert rad/s to deg/s
    yaw_deg = np.degrees(gyro_yaw)
    pitch_deg = np.degrees(gyro_pitch)
    roll_deg = np.degrees(gyro_roll)

    # Total angular velocity magnitude
    angular_velocity_magnitude = np.sqrt(
        gyro_yaw**2 +
        gyro_pitch**2 +
        gyro_roll**2
    )

    print("GYROSCOPE ANALYSIS")
    print("==================")

    print("\nGYROSCOPE RAW DATA SUMMARY (rad/s):")

    print(
        smartphone[
            [
                "GYROSCOPE Yaw (rad/s)",
                "GYROSCOPE Pitch (rad/s)",
                "GYROSCOPE Roll (rad/s)"
            ]
        ].describe()
    )

    print("\nGYROSCOPE SUMMARY (deg/s):")

    gyro_deg = pd.DataFrame({
        "Yaw": yaw_deg,
        "Pitch": pitch_deg,
        "Roll": roll_deg
    })

    print(
        gyro_deg.describe()
    )

    print("\nANGULAR VELOCITY MAGNITUDE SUMMARY (rad/s):")

    print(
        angular_velocity_magnitude.describe()
    )

    print("\nANGULAR VELOCITY MAGNITUDE SUMMARY (deg/s):")

    print(
        np.degrees(
            angular_velocity_magnitude
        ).describe()
    )

    print("\nFIRST 10 GYROSCOPE VALUES (deg/s):")

    print(
        gyro_deg.head(10)
    )

    print("\nLAST 10 GYROSCOPE VALUES (deg/s):")

    print(
        gyro_deg.tail(10)
    )

    print("\nHIGHEST ANGULAR VELOCITY SAMPLES:")

    highest = pd.DataFrame({
        "Yaw": yaw_deg,
        "Pitch": pitch_deg,
        "Roll": roll_deg,
        "Magnitude": np.degrees(
            angular_velocity_magnitude
        )
    })

    print(
        highest
        .sort_values(
            "Magnitude",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )