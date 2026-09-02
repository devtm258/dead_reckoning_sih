import pandas as pd
import numpy as np

from load_data import load_vbox_data


if __name__ == "__main__":

    vbox = load_vbox_data()

    columns = [
        "Velocity (km/hr)",
        "Indicated Vehicle Speed (km/hr)",
        "Wheel Speed Front Left (rad/sec)",
        "Wheel Speed Front Right (rad/sec)",
        "Wheel Speed Rear Left (rad/sec)",
        "Wheel Speed Rear Right (rad/sec)"
    ]

    data = vbox[columns].copy()

    print("VBOX SPEED VALIDATION")
    print("=====================")

    print("\nVBOX SPEED SUMMARY:")
    print(
        data.describe()
    )

    print("\nCORRELATION MATRIX:")

    print(
        data.corr()
    )

    print("\nFIRST 20 ROWS:")

    print(
        data.head(20).to_string(index=False)
    )

    print("\nHIGHEST VBOX VELOCITY VALUES:")

    print(
        data
        .sort_values(
            "Velocity (km/hr)",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )