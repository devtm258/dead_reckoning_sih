import pandas as pd
import numpy as np

from load_data import load_vbox_data


if __name__ == "__main__":

    vbox = load_vbox_data()

    velocity = vbox["Velocity (km/hr)"]

    wheel_columns = [
        "Wheel Speed Front Left (rad/sec)",
        "Wheel Speed Front Right (rad/sec)",
        "Wheel Speed Rear Left (rad/sec)",
        "Wheel Speed Rear Right (rad/sec)"
    ]

    indicated = vbox["Indicated Vehicle Speed (km/hr)"]

    # Average wheel speed
    wheel_mean = vbox[wheel_columns].mean(axis=1)

    # Difference between VBOX velocity and wheel-speed estimate
    velocity_difference = velocity - wheel_mean

    # Difference between VBOX velocity and indicated speed
    indicated_difference = velocity - indicated

    analysis = pd.DataFrame({
        "VELOCITY": velocity,
        "INDICATED_SPEED": indicated,
        "WHEEL_MEAN": wheel_mean,
        "VELOCITY_WHEEL_DIFFERENCE": velocity_difference,
        "VELOCITY_INDICATED_DIFFERENCE": indicated_difference
    })

    print("VBOX VELOCITY ANOMALY ANALYSIS")
    print("==============================")

    print("\nVELOCITY - WHEEL SPEED DIFFERENCE:")
    print(
        velocity_difference.describe()
    )

    print("\nVELOCITY - INDICATED SPEED DIFFERENCE:")
    print(
        indicated_difference.describe()
    )

    # Flag suspicious velocity samples
    suspicious = analysis[
        analysis["VELOCITY_WHEEL_DIFFERENCE"].abs() > 5
    ]

    print("\nNUMBER OF SUSPICIOUS SAMPLES:")
    print(
        len(suspicious)
    )

    print("\nPERCENTAGE OF SUSPICIOUS SAMPLES:")
    print(
        len(suspicious) / len(analysis) * 100
    )

    print("\nSUSPICIOUS SAMPLES:")
    print(
        suspicious.head(30).to_string(index=False)
    )

    print("\nLARGEST VELOCITY-WHEEL DIFFERENCES:")

    print(
        analysis
        .assign(
            ABS_DIFFERENCE=
            analysis["VELOCITY_WHEEL_DIFFERENCE"].abs()
        )
        .sort_values(
            "ABS_DIFFERENCE",
            ascending=False
        )
        .head(30)
        .to_string(index=False)
    )