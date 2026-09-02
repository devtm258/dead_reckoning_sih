import os
import re

from load_data import (
    load_smartphone_data,
    load_vbox_data
)


# ============================================================
# DATASET INSPECTION
# ============================================================

def print_columns(name, df):

    print("\n" + "=" * 80)
    print(name)
    print("=" * 80)

    print(
        f"ROWS    : {len(df)}"
    )

    print(
        f"COLUMNS : {len(df.columns)}"
    )

    print("\nCOLUMN LIST")
    print("-" * 80)

    for i, column in enumerate(df.columns):

        print(
            f"{i:3d} : {column}"
        )


# ============================================================
# FIND INTERESTING COLUMNS
# ============================================================

def find_matching_columns(
    df,
    keywords
):

    matches = []

    for column in df.columns:

        text = str(
            column
        ).lower()


        for keyword in keywords:

            if keyword.lower() in text:

                matches.append(
                    column
                )

                break

    return matches


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\nDATASET INSPECTION"
    )

    print(
        "=================="
    )


    # ========================================================
    # LOAD DATA
    # ========================================================

    print(
        "\nLoading smartphone dataset..."
    )

    smartphone = (
        load_smartphone_data()
    )


    print(
        "Loading VBox dataset..."
    )

    vbox = (
        load_vbox_data()
    )


    # ========================================================
    # PRINT FULL COLUMNS
    # ========================================================

    print_columns(
        "SMARTPHONE DATASET",
        smartphone
    )


    print_columns(
        "VBOX DATASET",
        vbox
    )


    # ========================================================
    # SPEED / VELOCITY SEARCH
    # ========================================================

    keywords = [

        "speed",

        "velocity",

        "vel",

        "kmh",

        "km/h",

        "m/s",

        "ms"

    ]


    print(
        "\n" + "=" * 80
    )

    print(
        "POSSIBLE SPEED / VELOCITY COLUMNS"
    )

    print(
        "=" * 80
    )


    smartphone_matches = (
        find_matching_columns(
            smartphone,
            keywords
        )
    )


    vbox_matches = (
        find_matching_columns(
            vbox,
            keywords
        )
    )


    print(
        "\nSMARTPHONE:"
    )


    if smartphone_matches:

        for column in smartphone_matches:

            print(
                f"  - {column}"
            )

    else:

        print(
            "  None found"
        )


    print(
        "\nVBOX:"
    )


    if vbox_matches:

        for column in vbox_matches:

            print(
                f"  - {column}"
            )

    else:

        print(
            "  None found"
        )


    # ========================================================
    # POSITION COLUMNS
    # ========================================================

    position_keywords = [

        "latitude",

        "longitude",

        "lat",

        "lon",

        "long",

        "position",

        "north",

        "east",

        "distance"

    ]


    print(
        "\n" + "=" * 80
    )

    print(
        "POSSIBLE POSITION / DISTANCE COLUMNS"
    )

    print(
        "=" * 80
    )


    smartphone_position = (
        find_matching_columns(
            smartphone,
            position_keywords
        )
    )


    vbox_position = (
        find_matching_columns(
            vbox,
            position_keywords
        )
    )


    print(
        "\nSMARTPHONE:"
    )


    for column in smartphone_position:

        print(
            f"  - {column}"
        )


    print(
        "\nVBOX:"
    )


    for column in vbox_position:

        print(
            f"  - {column}"
        )


    # ========================================================
    # HEADING COLUMNS
    # ========================================================

    heading_keywords = [

        "heading",

        "yaw",

        "orientation",

        "course",

        "direction"

    ]


    print(
        "\n" + "=" * 80
    )

    print(
        "POSSIBLE HEADING / ORIENTATION COLUMNS"
    )

    print(
        "=" * 80
    )


    smartphone_heading = (
        find_matching_columns(
            smartphone,
            heading_keywords
        )
    )


    vbox_heading = (
        find_matching_columns(
            vbox,
            heading_keywords
        )
    )


    print(
        "\nSMARTPHONE:"
    )


    for column in smartphone_heading:

        print(
            f"  - {column}"
        )


    print(
        "\nVBOX:"
    )


    for column in vbox_heading:

        print(
            f"  - {column}"
        )


    # ========================================================
    # DATASET SHAPES
    # ========================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "DATASET SHAPES"
    )

    print(
        "=" * 80
    )

    print(
        f"Smartphone : {smartphone.shape}"
    )

    print(
        f"VBox       : {vbox.shape}"
    )


    # ========================================================
    # TIME COLUMNS
    # ========================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "TIME COLUMNS"
    )

    print(
        "=" * 80
    )


    time_keywords = [

        "time",

        "timestamp",

        "elapsed",

        "since start"

    ]


    print(
        "\nSMARTPHONE:"
    )

    for column in find_matching_columns(
        smartphone,
        time_keywords
    ):

        print(
            f"  - {column}"
        )


    print(
        "\nVBOX:"
    )

    for column in find_matching_columns(
        vbox,
        time_keywords
    ):

        print(
            f"  - {column}"
        )


    # ========================================================
    # END
    # ========================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "INSPECTION COMPLETE"
    )

    print(
        "=" * 80
    )


if __name__ == "__main__":

    main()