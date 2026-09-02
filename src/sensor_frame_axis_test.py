import pandas as pd
import numpy as np

from load_data import load_smartphone_data


# ============================================================
# LOAD SMARTPHONE DATA
# ============================================================

smartphone = load_smartphone_data()


# ============================================================
# FIND SENSOR COLUMNS
# ============================================================

def find_column(prefix):
    matches = [
        col for col in smartphone.columns
        if col.startswith(prefix)
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one column starting with "
            f"'{prefix}', found: {matches}"
        )

    return matches[0]


acc_x_col = "ACCELEROMETER X (m/s²)"
acc_y_col = "ACCELEROMETER Y (m/s²)"
acc_z_col = "ACCELEROMETER Z (m/s²)"

grav_x_col = "GRAVITY X (m/s²)"
grav_y_col = "GRAVITY Y (m/s²)"
grav_z_col = "GRAVITY Z (m/s²)"

gyro_yaw_col = "GYROSCOPE Yaw (rad/s)"
gyro_pitch_col = "GYROSCOPE Pitch (rad/s)"
gyro_roll_col = "GYROSCOPE Roll (rad/s)"

mag_x_col = find_column("MAGNETIC FIELD X")
mag_y_col = find_column("MAGNETIC FIELD Y")
mag_z_col = find_column("MAGNETIC FIELD Z")

orientation_yaw_col = "ORIENTATION (Yaw) (Â°)"
orientation_pitch_col = "ORIENTATION (Pitch) (Â°)"
orientation_roll_col = "ORIENTATION (Roll ) (Â°)"


# ============================================================
# LOAD ARRAYS
# ============================================================

acc = smartphone[
    [acc_x_col, acc_y_col, acc_z_col]
].to_numpy(dtype=float)

gravity = smartphone[
    [grav_x_col, grav_y_col, grav_z_col]
].to_numpy(dtype=float)

mag = smartphone[
    [mag_x_col, mag_y_col, mag_z_col]
].to_numpy(dtype=float)

orientation = smartphone[
    [
        orientation_yaw_col,
        orientation_pitch_col,
        orientation_roll_col
    ]
].to_numpy(dtype=float)


# ============================================================
# NORMALIZE VECTORS
# ============================================================

def normalize(v):

    magnitude = np.linalg.norm(
        v,
        axis=1,
        keepdims=True
    )

    magnitude = np.maximum(
        magnitude,
        1e-12
    )

    return v / magnitude


gravity_n = normalize(gravity)
mag_n = normalize(mag)


# ============================================================
# BASIC SENSOR-FRAME ANALYSIS
# ============================================================

print("\nSENSOR FRAME AXIS TEST")
print("======================")

print("\nGRAVITY MEAN VECTOR:")

print(
    f"X : {gravity[:, 0].mean():.6f}"
)

print(
    f"Y : {gravity[:, 1].mean():.6f}"
)

print(
    f"Z : {gravity[:, 2].mean():.6f}"
)


print("\nNORMALIZED GRAVITY MEAN:")

print(
    f"X : {gravity_n[:, 0].mean():.6f}"
)

print(
    f"Y : {gravity_n[:, 1].mean():.6f}"
)

print(
    f"Z : {gravity_n[:, 2].mean():.6f}"
)


# ============================================================
# TEST WHETHER ACCELEROMETER AND GRAVITY ARE CONSISTENT
# ============================================================

acc_mag = np.linalg.norm(
    acc,
    axis=1
)

gravity_mag = np.linalg.norm(
    gravity,
    axis=1
)

print("\nACCELEROMETER MAGNITUDE:")
print(
    f"Mean : {acc_mag.mean():.6f} m/s²"
)
print(
    f"Std  : {acc_mag.std():.6f} m/s²"
)


print("\nGRAVITY MAGNITUDE:")
print(
    f"Mean : {gravity_mag.mean():.6f} m/s²"
)
print(
    f"Std  : {gravity_mag.std():.6f} m/s²"
)


# ============================================================
# MAGNETIC VECTOR
# ============================================================

mag_magnitude = np.linalg.norm(
    mag,
    axis=1
)

print("\nMAGNETOMETER VECTOR:")
print(
    f"Mean X : {mag[:, 0].mean():.6f}"
)
print(
    f"Mean Y : {mag[:, 1].mean():.6f}"
)
print(
    f"Mean Z : {mag[:, 2].mean():.6f}"
)

print(
    f"Mean magnitude : "
    f"{mag_magnitude.mean():.6f} µT"
)


# ============================================================
# DOT PRODUCT BETWEEN GRAVITY AND MAGNETIC FIELD
#
# This tells us how much magnetic field is aligned with
# the vertical direction.
# ============================================================

mag_gravity_dot = np.sum(
    mag_n * gravity_n,
    axis=1
)

print("\nMAGNETIC / GRAVITY ALIGNMENT")
print("============================")

print(
    f"Mean dot product : "
    f"{mag_gravity_dot.mean():.6f}"
)

print(
    f"Minimum : "
    f"{mag_gravity_dot.min():.6f}"
)

print(
    f"Maximum : "
    f"{mag_gravity_dot.max():.6f}"
)


# ============================================================
# REMOVE VERTICAL MAGNETIC COMPONENT
# ============================================================

horizontal_mag = (
    mag_n -
    mag_gravity_dot[:, None] * gravity_n
)

horizontal_mag = normalize(
    horizontal_mag
)


# ============================================================
# TEST ALL HORIZONTAL AXIS COMBINATIONS
#
# Instead of assuming X/Y are horizontal, examine all
# coordinate pairs.
# ============================================================

axis_names = [
    "X",
    "Y",
    "Z"
]

axis_vectors = {
    "X": horizontal_mag[:, 0],
    "Y": horizontal_mag[:, 1],
    "Z": horizontal_mag[:, 2]
}


# ============================================================
# ORIENTATION YAW
# ============================================================

orientation_yaw = orientation[:, 0]


# ============================================================
# ANGLE DIFFERENCE FUNCTION
# ============================================================

def circular_difference(a, b):

    return (
        (
            a - b + 180
        ) % 360
    ) - 180


# ============================================================
# TEST AXIS PAIRS
# ============================================================

results = []


for first_axis in axis_names:

    for second_axis in axis_names:

        if first_axis == second_axis:
            continue

        a = axis_vectors[first_axis]
        b = axis_vectors[second_axis]

        heading = np.degrees(
            np.arctan2(
                b,
                a
            )
        )

        heading = (
            heading + 360
        ) % 360

        error = circular_difference(
            heading,
            orientation_yaw
        )

        absolute_error = np.abs(
            error
        )

        correlation = np.corrcoef(
            heading,
            orientation_yaw
        )[0, 1]

        results.append({

            "AXIS_FORMULA":
                f"atan2({second_axis}, {first_axis})",

            "CORRELATION":
                correlation,

            "MAE_DEG":
                absolute_error.mean(),

            "MEDIAN_ERROR_DEG":
                np.median(
                    absolute_error
                ),

            "MAX_ERROR_DEG":
                absolute_error.max()

        })


# ============================================================
# RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    "MAE_DEG"
)


print(
    "\nHORIZONTAL AXIS TEST RESULTS"
)

print(
    "============================"
)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x:
        f"{x:.6f}"
    )
)


# ============================================================
# BEST AXIS COMBINATION
# ============================================================

best = results_df.iloc[0]


print(
    "\nBEST AXIS COMBINATION"
)

print(
    "====================="
)

print(
    f"Formula : "
    f"{best['AXIS_FORMULA']}"
)

print(
    f"Correlation : "
    f"{best['CORRELATION']:.6f}"
)

print(
    f"Mean absolute error : "
    f"{best['MAE_DEG']:.6f}°"
)

print(
    f"Median absolute error : "
    f"{best['MEDIAN_ERROR_DEG']:.6f}°"
)

print(
    f"Maximum absolute error : "
    f"{best['MAX_ERROR_DEG']:.6f}°"
)


# ============================================================
# SAVE RESULTS
# ============================================================

output_path = (
    "data/processed/"
    "sensor_frame_axis_test.csv"
)

results_df.to_csv(
    output_path,
    index=False
)

print(
    "\nResults saved to:"
)

print(output_path)