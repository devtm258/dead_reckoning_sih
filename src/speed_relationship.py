import pandas as pd
import numpy as np

from load_data import load_smartphone_data, load_vbox_data


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    smartphone_speed = smartphone["GPS SPEED (Kmh)"]
    vbox_speed = vbox["Velocity (km/hr)"]

    analysis = pd.DataFrame({
        "SMARTPHONE_SPEED": smartphone_speed,
        "VBOX_SPEED": vbox_speed
    })

    # Difference
    analysis["SPEED_DIFFERENCE"] = (
        analysis["SMARTPHONE_SPEED"]
        - analysis["VBOX_SPEED"]
    )

    # Absolute difference
    analysis["ABSOLUTE_ERROR"] = (
        analysis["SPEED_DIFFERENCE"].abs()
    )

    # Ratio
    analysis["SPEED_RATIO"] = (
        analysis["SMARTPHONE_SPEED"]
        / analysis["VBOX_SPEED"].replace(0, np.nan)
    )

    print("SPEED RELATIONSHIP ANALYSIS")
    print("===========================")

    print("\nSMARTPHONE SPEED SUMMARY:")
    print(
        smartphone_speed.describe()
    )

    print("\nVBOX SPEED SUMMARY:")
    print(
        vbox_speed.describe()
    )

    print("\nSPEED DIFFERENCE SUMMARY:")
    print(
        analysis["SPEED_DIFFERENCE"].describe()
    )

    print("\nABSOLUTE SPEED ERROR SUMMARY:")
    print(
        analysis["ABSOLUTE_ERROR"].describe()
    )

    print("\nSPEED RATIO SUMMARY:")
    print(
        analysis["SPEED_RATIO"].describe()
    )

    print("\nCORRELATION:")
    print(
        analysis[
            ["SMARTPHONE_SPEED", "VBOX_SPEED"]
        ].corr()
    )

    print("\nFIRST 20 SPEED VALUES:")

    print(
        analysis.head(20).to_string(index=False)
    )

    print("\nHIGHEST VBOX SPEED SAMPLES:")

    print(
        analysis
        .sort_values("VBOX_SPEED", ascending=False)
        .head(20)
        .to_string(index=False)
    )