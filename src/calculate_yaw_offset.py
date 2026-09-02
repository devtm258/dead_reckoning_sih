import numpy as np
import pandas as pd

from load_data import (
    load_smartphone_data,
    load_vbox_data
)


def find_column(df, candidates):

    for name in candidates:

        if name in df.columns:
            return name

    lookup = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for name in candidates:

        key = (
            str(name)
            .strip()
            .lower()
        )

        if key in lookup:
            return lookup[key]

    return None


def wrap_angle(angle):

    return (
        angle + 180.0
    ) % 360.0 - 180.0


def circular_mean_deg(angles):

    radians = np.radians(angles)

    return np.degrees(
        np.arctan2(
            np.mean(np.sin(radians)),
            np.mean(np.cos(radians))
        )
    )


def main():

    print(
        "\nPHONE-TO-VEHICLE YAW CALIBRATION"
    )

    print(
        "================================="
    )


    # ========================================================
    # LOAD DATA
    # ========================================================

    smartphone = load_smartphone_data()

    vbox = load_vbox_data()


    # ========================================================
    # FIND COLUMNS
    # ========================================================

    smartphone_yaw_col = find_column(
        smartphone,
        [
            "ORIENTATION (Yaw) (Â°)",
            "ORIENTATION (Yaw) (°)"
        ]
    )


    vbox_heading_col = find_column(
        vbox,
        [
            "Heading (degrees)"
        ]
    )


    vbox_speed_col = find_column(
        vbox,
        [
            "Velocity (km/hr)"
        ]
    )


    if smartphone_yaw_col is None:

        raise ValueError(
            "Smartphone orientation yaw column not found."
        )


    if vbox_heading_col is None:

        raise ValueError(
            "VBox heading column not found."
        )


    if vbox_speed_col is None:

        raise ValueError(
            "VBox velocity column not found."
        )


    print(
        f"\nSmartphone yaw : {smartphone_yaw_col}"
    )

    print(
        f"VBox heading   : {vbox_heading_col}"
    )

    print(
        f"VBox velocity  : {vbox_speed_col}"
    )


    # ========================================================
    # EXTRACT DATA
    # ========================================================

    smartphone_yaw = pd.to_numeric(
        smartphone[
            smartphone_yaw_col
        ],
        errors="coerce"
    ).to_numpy(float)


    vbox_heading = pd.to_numeric(
        vbox[
            vbox_heading_col
        ],
        errors="coerce"
    ).to_numpy(float)


    vbox_speed = pd.to_numeric(
        vbox[
            vbox_speed_col
        ],
        errors="coerce"
    ).to_numpy(float)


    # ========================================================
    # VALID DATA
    # ========================================================

    valid = (

        np.isfinite(
            smartphone_yaw
        )

        &

        np.isfinite(
            vbox_heading
        )

        &

        np.isfinite(
            vbox_speed
        )

        &

        # Use moving vehicle samples.
        #
        # At very low speed, heading measurements can be
        # unreliable.

        (
            vbox_speed >= 10.0
        )

    )


    print(
        f"\nTOTAL SAMPLES : {len(smartphone_yaw)}"
    )

    print(
        f"VALID CALIBRATION SAMPLES : "
        f"{np.sum(valid)}"
    )


    if np.sum(valid) < 100:

        raise ValueError(
            "Not enough valid moving samples."
        )


    # ========================================================
    # ANGLE DIFFERENCE
    #
    # vehicle heading - smartphone yaw
    # ========================================================

    yaw_difference = wrap_angle(

        vbox_heading[valid]
        -
        smartphone_yaw[valid]

    )


    # ========================================================
    # REMOVE EXTREME OUTLIERS
    #
    # Keep only differences within 30 degrees of the
    # circular median.
    # ========================================================

    initial_offset = circular_mean_deg(
        yaw_difference
    )


    centered_error = wrap_angle(

        yaw_difference
        -
        initial_offset

    )


    stable = (

        np.abs(
            centered_error
        )
        <
        30.0

    )


    stable_difference = (
        yaw_difference[stable]
    )


    if len(
        stable_difference
    ) < 100:

        raise ValueError(
            "Too few stable yaw samples after outlier rejection."
        )


    # ========================================================
    # FINAL OFFSET
    # ========================================================

    offset = circular_mean_deg(
        stable_difference
    )


    # ========================================================
    # CALIBRATED SMARTPHONE HEADING
    # ========================================================

    calibrated_heading = wrap_angle(

        smartphone_yaw[valid]
        +
        offset

    )


    heading_error = wrap_angle(

        calibrated_heading
        -
        vbox_heading[valid]

    )


    # ========================================================
    # STATISTICS
    # ========================================================

    absolute_error = np.abs(
        heading_error
    )


    print(
        "\nYAW OFFSET RESULT"
    )

    print(
        "================="
    )

    print(
        f"Initial offset : "
        f"{initial_offset:.6f}°"
    )

    print(
        f"Final offset   : "
        f"{offset:.6f}°"
    )


    print(
        "\nAFTER OFFSET CALIBRATION"
    )

    print(
        "========================="
    )

    print(
        f"Mean absolute error   : "
        f"{np.mean(absolute_error):.6f}°"
    )

    print(
        f"Median absolute error : "
        f"{np.median(absolute_error):.6f}°"
    )

    print(
        f"P95 absolute error    : "
        f"{np.percentile(absolute_error, 95):.6f}°"
    )

    print(
        f"Maximum absolute error: "
        f"{np.max(absolute_error):.6f}°"
    )


    # ========================================================
    # SAVE CALIBRATION
    # ========================================================

    output = pd.DataFrame({

        "parameter": [

            "yaw_offset_deg",

            "calibration_samples",

            "mean_absolute_error_deg",

            "median_absolute_error_deg",

            "p95_absolute_error_deg"

        ],

        "value": [

            offset,

            len(stable_difference),

            np.mean(
                absolute_error
            ),

            np.median(
                absolute_error
            ),

            np.percentile(
                absolute_error,
                95
            )

        ]

    })


    output_file = (
        "data/processed/"
        "phone_vehicle_yaw_calibration.csv"
    )


    output.to_csv(
        output_file,
        index=False
    )


    print(
        "\nCALIBRATION SAVED:"
    )

    print(
        output_file
    )


    print(
        "\nIMPORTANT:"
    )

    print(
        "This calibration uses VBox ONLY "
        "offline."
    )

    print(
        "It will NOT be used as a runtime "
        "GNSS/VBox input."
    )


if __name__ == "__main__":

    main()