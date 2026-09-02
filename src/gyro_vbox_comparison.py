import pandas as pd
import numpy as np

from load_data import load_smartphone_data, load_vbox_data


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    # Smartphone gyroscope yaw is in rad/s.
    # Convert it to degrees/second.
    smartphone_gyro_yaw = np.degrees(
        smartphone["GYROSCOPE Yaw (rad/s)"]
    )

    vbox_yaw_rate = vbox["Yaw Rate (deg/sec)"]

    comparison = pd.DataFrame({
        "SMARTPHONE_GYRO_YAW": smartphone_gyro_yaw,
        "VBOX_YAW_RATE": vbox_yaw_rate
    })

    comparison["DIFFERENCE"] = (
        comparison["SMARTPHONE_GYRO_YAW"]
        - comparison["VBOX_YAW_RATE"]
    )

    comparison["ABSOLUTE_ERROR"] = (
        comparison["DIFFERENCE"].abs()
    )

    print("SMARTPHONE GYROSCOPE VS VBOX YAW RATE")
    print("======================================")

    print("\nSMARTPHONE GYRO YAW SUMMARY:")

    print(
        comparison["SMARTPHONE_GYRO_YAW"].describe()
    )

    print("\nVBOX YAW RATE SUMMARY:")

    print(
        comparison["VBOX_YAW_RATE"].describe()
    )

    print("\nDIFFERENCE SUMMARY:")

    print(
        comparison["DIFFERENCE"].describe()
    )

    print("\nABSOLUTE ERROR SUMMARY:")

    print(
        comparison["ABSOLUTE_ERROR"].describe()
    )

    print("\nCORRELATION:")

    print(
        comparison[
            [
                "SMARTPHONE_GYRO_YAW",
                "VBOX_YAW_RATE"
            ]
        ].corr()
    )

    print("\nFIRST 20 SAMPLES:")

    print(
        comparison.head(20).to_string(index=False)
    )

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

    print("\nHIGHEST ABSOLUTE DIFFERENCES:")

    print(
        comparison
        .sort_values(
            "ABSOLUTE_ERROR",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )