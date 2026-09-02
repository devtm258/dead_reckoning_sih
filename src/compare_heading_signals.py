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

        key = str(name).strip().lower()

        if key in lookup:
            return lookup[key]

    return None


def wrap(angle):

    return (
        angle + 180.0
    ) % 360.0 - 180.0


def circular_mean(x):

    r = np.radians(x)

    return np.degrees(
        np.arctan2(
            np.mean(np.sin(r)),
            np.mean(np.cos(r))
        )
    )


def evaluate(
    name,
    smartphone_heading,
    vbox_heading,
    speed
):

    valid = (

        np.isfinite(
            smartphone_heading
        )

        &

        np.isfinite(
            vbox_heading
        )

        &

        np.isfinite(
            speed
        )

        &

        (speed >= 10.0)

    )


    h = smartphone_heading[valid]

    v = vbox_heading[valid]


    # Try both possible relationships:
    #
    # VBox = Smartphone + offset
    #
    # and
    #
    # VBox = -Smartphone + offset

    normal_difference = wrap(
        v - h
    )

    reverse_difference = wrap(
        v + h
    )


    normal_offset = circular_mean(
        normal_difference
    )

    reverse_offset = circular_mean(
        reverse_difference
    )


    normal_error = wrap(

        normal_difference
        -
        normal_offset

    )


    reverse_error = wrap(

        reverse_difference
        -
        reverse_offset

    )


    normal_abs = np.abs(
        normal_error
    )

    reverse_abs = np.abs(
        reverse_error
    )


    print(
        "\n" + "=" * 70
    )

    print(
        name
    )

    print(
        "=" * 70
    )


    print(
        f"Samples: {len(h)}"
    )


    print(
        "\nNORMAL:"
    )

    print(
        f"Offset : "
        f"{normal_offset:.3f}°"
    )

    print(
        f"Mean   : "
        f"{np.mean(normal_abs):.3f}°"
    )

    print(
        f"Median : "
        f"{np.median(normal_abs):.3f}°"
    )

    print(
        f"P95    : "
        f"{np.percentile(normal_abs, 95):.3f}°"
    )


    print(
        "\nREVERSED:"
    )

    print(
        f"Offset : "
        f"{reverse_offset:.3f}°"
    )

    print(
        f"Mean   : "
        f"{np.mean(reverse_abs):.3f}°"
    )

    print(
        f"Median : "
        f"{np.median(reverse_abs):.3f}°"
    )

    print(
        f"P95    : "
        f"{np.percentile(reverse_abs, 95):.3f}°"
    )


def main():

    print(
        "\nHEADING SIGNAL DIAGNOSTIC"
    )

    print(
        "========================="
    )


    smartphone = load_smartphone_data()

    vbox = load_vbox_data()


    gps_orientation_col = find_column(

        smartphone,

        [
            "GPS ORIENTATION (Â°)",
            "GPS ORIENTATION (°)"
        ]

    )


    orientation_yaw_col = find_column(

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


    if gps_orientation_col is None:

        raise ValueError(
            "GPS orientation column missing."
        )


    if orientation_yaw_col is None:

        raise ValueError(
            "Orientation yaw column missing."
        )


    if vbox_heading_col is None:

        raise ValueError(
            "VBox heading column missing."
        )


    if vbox_speed_col is None:

        raise ValueError(
            "VBox velocity column missing."
        )


    gps_orientation = pd.to_numeric(

        smartphone[
            gps_orientation_col
        ],

        errors="coerce"

    ).to_numpy(float)


    orientation_yaw = pd.to_numeric(

        smartphone[
            orientation_yaw_col
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


    print(
        f"\nGPS orientation : "
        f"{gps_orientation_col}"
    )

    print(
        f"Orientation yaw : "
        f"{orientation_yaw_col}"
    )

    print(
        f"VBox heading    : "
        f"{vbox_heading_col}"
    )


    evaluate(

        "GPS ORIENTATION",

        gps_orientation,

        vbox_heading,

        vbox_speed

    )


    evaluate(

        "SMARTPHONE ORIENTATION YAW",

        orientation_yaw,

        vbox_heading,

        vbox_speed

    )


    print(
        "\nDIAGNOSTIC COMPLETE"
    )


if __name__ == "__main__":

    main()