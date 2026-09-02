import os
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = (
    "data/processed/imu_orientation_estimate.csv"
)


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(df, text):

    text = text.upper()

    for column in df.columns:

        if text in column.upper():

            return column

    raise KeyError(
        f"Could not find column containing: {text}\n"
        f"Available columns:\n{list(df.columns)}"
    )


# ============================================================
# ANGLE WRAPPING
# ============================================================

def wrap_angle(angle):

    return (
        (angle + 180.0) % 360.0
    ) - 180.0


# ============================================================
# LOAD SMARTPHONE DATA
# ============================================================

print()
print("SMARTPHONE IMU ORIENTATION ESTIMATOR")
print("====================================")
print()

smartphone = load_smartphone_data()


# ============================================================
# FIND REQUIRED COLUMNS
# ============================================================

time_column = find_column(
    smartphone,
    "TIME SINCE START"
)

gyro_yaw_column = find_column(
    smartphone,
    "GYROSCOPE YAW"
)

gyro_pitch_column = find_column(
    smartphone,
    "GYROSCOPE PITCH"
)

gyro_roll_column = find_column(
    smartphone,
    "GYROSCOPE ROLL"
)

gravity_x_column = find_column(
    smartphone,
    "GRAVITY X"
)

gravity_y_column = find_column(
    smartphone,
    "GRAVITY Y"
)

gravity_z_column = find_column(
    smartphone,
    "GRAVITY Z"
)


print("COLUMNS FOUND:")
print()
print("TIME        :", time_column)
print("GYRO YAW    :", gyro_yaw_column)
print("GYRO PITCH  :", gyro_pitch_column)
print("GYRO ROLL   :", gyro_roll_column)
print("GRAVITY X   :", gravity_x_column)
print("GRAVITY Y   :", gravity_y_column)
print("GRAVITY Z   :", gravity_z_column)
print()


# ============================================================
# EXTRACT DATA
# ============================================================

time_ms = smartphone[
    time_column
].to_numpy(dtype=float)

gyro_yaw = smartphone[
    gyro_yaw_column
].to_numpy(dtype=float)

gyro_pitch = smartphone[
    gyro_pitch_column
].to_numpy(dtype=float)

gyro_roll = smartphone[
    gyro_roll_column
].to_numpy(dtype=float)

gravity_x = smartphone[
    gravity_x_column
].to_numpy(dtype=float)

gravity_y = smartphone[
    gravity_y_column
].to_numpy(dtype=float)

gravity_z = smartphone[
    gravity_z_column
].to_numpy(dtype=float)


# ============================================================
# REMOVE INVALID VALUES
# ============================================================

valid = (
    np.isfinite(time_ms)
    &
    np.isfinite(gyro_yaw)
    &
    np.isfinite(gyro_pitch)
    &
    np.isfinite(gyro_roll)
    &
    np.isfinite(gravity_x)
    &
    np.isfinite(gravity_y)
    &
    np.isfinite(gravity_z)
)


time_ms = time_ms[valid]

gyro_yaw = gyro_yaw[valid]
gyro_pitch = gyro_pitch[valid]
gyro_roll = gyro_roll[valid]

gravity_x = gravity_x[valid]
gravity_y = gravity_y[valid]
gravity_z = gravity_z[valid]


print(
    "VALID SAMPLES :", len(time_ms)
)

print()


# ============================================================
# CONVERT GYROSCOPE
# ============================================================

# Smartphone gyroscope is supplied in rad/s.
#
# Convert to degrees/s.

gyro_yaw_deg = (
    gyro_yaw *
    180.0 /
    np.pi
)

gyro_pitch_deg = (
    gyro_pitch *
    180.0 /
    np.pi
)

gyro_roll_deg = (
    gyro_roll *
    180.0 /
    np.pi
)


# ============================================================
# TIME
# ============================================================

time_seconds = (
    time_ms /
    1000.0
)


# ============================================================
# GRAVITY-BASED ROLL AND PITCH
# ============================================================

# Gravity provides the vertical reference.
#
# Roll and pitch can therefore be estimated without GPS
# and without magnetometer.

roll_acc = np.degrees(
    np.arctan2(
        gravity_y,
        gravity_z
    )
)


pitch_acc = np.degrees(
    np.arctan2(
        -gravity_x,
        np.sqrt(
            gravity_y**2 +
            gravity_z**2
        )
    )
)


# ============================================================
# INITIAL ORIENTATION
# ============================================================

estimated_roll = np.zeros(
    len(time_seconds)
)

estimated_pitch = np.zeros(
    len(time_seconds)
)

estimated_yaw = np.zeros(
    len(time_seconds)
)


# Use gravity-derived orientation as the initial state.

estimated_roll[0] = roll_acc[0]

estimated_pitch[0] = pitch_acc[0]

# Yaw has no absolute reference from gravity.
#
# Therefore initialize yaw at zero.

estimated_yaw[0] = 0.0


# ============================================================
# GYROSCOPE INTEGRATION
# ============================================================

for i in range(1, len(time_seconds)):

    dt = (
        time_seconds[i]
        -
        time_seconds[i - 1]
    )

    # Ignore invalid / unreasonable time jumps.

    if dt <= 0 or dt > 1.0:

        estimated_roll[i] = (
            estimated_roll[i - 1]
        )

        estimated_pitch[i] = (
            estimated_pitch[i - 1]
        )

        estimated_yaw[i] = (
            estimated_yaw[i - 1]
        )

        continue


    # --------------------------------------------------------
    # GYROSCOPE INTEGRATION
    # --------------------------------------------------------

    estimated_roll[i] = (
        estimated_roll[i - 1]
        +
        gyro_roll_deg[i] * dt
    )

    estimated_pitch[i] = (
        estimated_pitch[i - 1]
        +
        gyro_pitch_deg[i] * dt
    )

    estimated_yaw[i] = (
        estimated_yaw[i - 1]
        +
        gyro_yaw_deg[i] * dt
    )


    # --------------------------------------------------------
    # GRAVITY CORRECTION
    # --------------------------------------------------------

    # Small complementary correction.
    #
    # Gravity is reliable for roll/pitch but contains
    # no heading information.

    alpha = 0.98

    estimated_roll[i] = (
        alpha *
        estimated_roll[i]
        +
        (1.0 - alpha) *
        roll_acc[i]
    )

    estimated_pitch[i] = (
        alpha *
        estimated_pitch[i]
        +
        (1.0 - alpha) *
        pitch_acc[i]
    )


    # Keep yaw within -180 to +180 degrees.

    estimated_yaw[i] = wrap_angle(
        estimated_yaw[i]
    )


# ============================================================
# CREATE OUTPUT
# ============================================================

results = pd.DataFrame({

    "TIME_MS": time_ms,

    "TIME_SECONDS": time_seconds,

    "GYRO_YAW_RAD_S": gyro_yaw,

    "GYRO_PITCH_RAD_S": gyro_pitch,

    "GYRO_ROLL_RAD_S": gyro_roll,

    "GYRO_YAW_DEG_S": gyro_yaw_deg,

    "GYRO_PITCH_DEG_S": gyro_pitch_deg,

    "GYRO_ROLL_DEG_S": gyro_roll_deg,

    "GRAVITY_X": gravity_x,

    "GRAVITY_Y": gravity_y,

    "GRAVITY_Z": gravity_z,

    "GRAVITY_ROLL_DEG": roll_acc,

    "GRAVITY_PITCH_DEG": pitch_acc,

    "ESTIMATED_ROLL_DEG": estimated_roll,

    "ESTIMATED_PITCH_DEG": estimated_pitch,

    "ESTIMATED_YAW_DEG": estimated_yaw
})


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "data/processed",
    exist_ok=True
)

results.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("ORIENTATION ESTIMATION")
print("======================")

print()

print(
    f"Initial roll  : "
    f"{estimated_roll[0]:.6f}°"
)

print(
    f"Initial pitch : "
    f"{estimated_pitch[0]:.6f}°"
)

print(
    f"Initial yaw   : "
    f"{estimated_yaw[0]:.6f}°"
)

print()

print("FINAL ORIENTATION:")

print(
    f"Roll  : "
    f"{estimated_roll[-1]:.6f}°"
)

print(
    f"Pitch : "
    f"{estimated_pitch[-1]:.6f}°"
)

print(
    f"Yaw   : "
    f"{estimated_yaw[-1]:.6f}°"
)

print()

print("ORIENTATION RANGE:")

print(
    f"Roll  : "
    f"{np.min(estimated_roll):.6f}° "
    f"to "
    f"{np.max(estimated_roll):.6f}°"
)

print(
    f"Pitch : "
    f"{np.min(estimated_pitch):.6f}° "
    f"to "
    f"{np.max(estimated_pitch):.6f}°"
)

print(
    f"Yaw   : "
    f"{np.min(estimated_yaw):.6f}° "
    f"to "
    f"{np.max(estimated_yaw):.6f}°"
)

print()

print("FILE SAVED:")
print(
    OUTPUT_FILE
)

print()

print(
    "SMARTPHONE IMU ORIENTATION "
    "ESTIMATION COMPLETE."
)