import pandas as pd
import numpy as np

from load_data import load_smartphone_data


GRAVITY = 9.80665


if __name__ == "__main__":

    smartphone = load_smartphone_data()

    acc_x = smartphone["ACCELEROMETER X (m/s²)"]
    acc_y = smartphone["ACCELEROMETER Y (m/s²)"]
    acc_z = smartphone["ACCELEROMETER Z (m/s²)"]

    gravity_x = smartphone["GRAVITY X (m/s²)"]
    gravity_y = smartphone["GRAVITY Y (m/s²)"]
    gravity_z = smartphone["GRAVITY Z (m/s²)"]

    # Accelerometer magnitude
    acceleration_magnitude = np.sqrt(
        acc_x**2 +
        acc_y**2 +
        acc_z**2
    )

    # Gravity magnitude
    gravity_magnitude = np.sqrt(
        gravity_x**2 +
        gravity_y**2 +
        gravity_z**2
    )

    # Linear acceleration estimate
    linear_acc_x = acc_x - gravity_x
    linear_acc_y = acc_y - gravity_y
    linear_acc_z = acc_z - gravity_z

    linear_acceleration_magnitude = np.sqrt(
        linear_acc_x**2 +
        linear_acc_y**2 +
        linear_acc_z**2
    )

    print("ACCELEROMETER ANALYSIS")
    print("======================")

    print("\nACCELEROMETER MAGNITUDE SUMMARY:")

    print(
        acceleration_magnitude.describe()
    )

    print("\nGRAVITY MAGNITUDE SUMMARY:")

    print(
        gravity_magnitude.describe()
    )

    print("\nLINEAR ACCELERATION MAGNITUDE SUMMARY:")

    print(
        linear_acceleration_magnitude.describe()
    )

    print("\nACCELEROMETER MAGNITUDE ERROR FROM g:")

    acceleration_error = (
        acceleration_magnitude - GRAVITY
    )

    print(
        acceleration_error.describe()
    )

    print("\nPERCENTAGE WITHIN 0.5 m/s² OF g:")

    within_05 = (
        acceleration_error.abs() <= 0.5
    ).mean() * 100

    print(
        f"{within_05:.2f}%"
    )

    print("\nPERCENTAGE WITHIN 1.0 m/s² OF g:")

    within_10 = (
        acceleration_error.abs() <= 1.0
    ).mean() * 100

    print(
        f"{within_10:.2f}%"
    )

    print("\nFIRST 10 ACCELEROMETER MAGNITUDES:")

    print(
        acceleration_magnitude.head(10)
    )

    print("\nLAST 10 ACCELEROMETER MAGNITUDES:")

    print(
        acceleration_magnitude.tail(10)
    )

    print("\nFIRST 10 LINEAR ACCELERATION MAGNITUDES:")

    print(
        linear_acceleration_magnitude.head(10)
    )

    print("\nLAST 10 LINEAR ACCELERATION MAGNITUDES:")

    print(
        linear_acceleration_magnitude.tail(10)
    )