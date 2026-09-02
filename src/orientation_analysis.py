import pandas as pd
import numpy as np

from load_data import load_smartphone_data


def analyze_magnetic_field(data):

    x = data["MAGNETIC FIELD X (Î¼T)"]
    y = data["MAGNETIC FIELD Y (Î¼T)"]
    z = data["MAGNETIC FIELD Z (Î¼T)"]

    magnitude = np.sqrt(
        x**2 +
        y**2 +
        z**2
    )

    print("MAGNETIC FIELD MAGNITUDE SUMMARY:")
    print(magnitude.describe())

    print("\nFIRST 10 MAGNITUDES:")
    print(magnitude.head(10))

    print("\nLAST 10 MAGNITUDES:")
    print(magnitude.tail(10))


if __name__ == "__main__":

    smartphone = load_smartphone_data()

    analyze_magnetic_field(smartphone)