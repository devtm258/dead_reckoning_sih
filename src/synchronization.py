import pandas as pd

from load_data import load_smartphone_data, load_vbox_data


def add_elapsed_time(smartphone, vbox):
    """
    Convert both datasets to elapsed time starting from 0 seconds.
    """

    smartphone = smartphone.copy()
    vbox = vbox.copy()

    # Smartphone time is in milliseconds.
    smartphone["elapsed_time"] = (
        smartphone[" TIME SINCE START (ms)"]
        - smartphone[" TIME SINCE START (ms)"].iloc[0]
    ) / 1000.0

    # VBOX time is in seconds.
    vbox["elapsed_time"] = (
        vbox[" Time Since Start of Day (seconds)"]
        - vbox[" Time Since Start of Day (seconds)"].iloc[0]
    )

    return smartphone, vbox


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    smartphone, vbox = add_elapsed_time(
        smartphone,
        vbox
    )

    print("SMARTPHONE ELAPSED TIME:")
    print(smartphone["elapsed_time"].head())

    print("\nVBOX ELAPSED TIME:")
    print(vbox["elapsed_time"].head())

    print("\nFINAL SMARTPHONE TIME:",
          smartphone["elapsed_time"].iloc[-1])

    print("FINAL VBOX TIME:",
          vbox["elapsed_time"].iloc[-1])