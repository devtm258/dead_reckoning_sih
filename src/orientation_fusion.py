import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = (
    "data/processed/orientation_fusion.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()

print()
print("ORIENTATION SENSOR FUSION")
print("=========================")
print()


# ============================================================
# COLUMN NAMES
# ============================================================

time_col = "TIME SINCE START (ms)"

gyro_yaw_col = "GYROSCOPE Yaw (rad/s)"
gyro_pitch_col = "GYROSCOPE Pitch (rad/s)"
gyro_roll_col = "GYROSCOPE Roll (rad/s)"

gravity_x_col = "GRAVITY X (m/s²)"
gravity_y_col = "GRAVITY Y (m/s²)"
gravity_z_col = "GRAVITY Z (m/s²)"

mag_x_col = "MAGNETIC FIELD X (Î¼T)"
mag_y_col = "MAGNETIC FIELD Y (ÎμT)"
mag_z_col = "MAGNETIC FIELD Z (ÎμT)"


# ============================================================
# FIND MAGNETOMETER COLUMNS SAFELY
# ============================================================

def find_column(prefix):

    matches = [
        col
        for col in smartphone.columns
        if col.startswith(prefix)
    ]

    if len(matches) != 1:

        raise ValueError(
            f"Expected exactly one column starting with "
            f"'{prefix}', found: {matches}"
        )

    return matches[0]


mag_x_col = find_column("MAGNETIC FIELD X")
mag_y_col = find_column("MAGNETIC FIELD Y")
mag_z_col = find_column("MAGNETIC FIELD Z")


# ============================================================
# LOAD ARRAYS
# ============================================================

time_ms = smartphone[
    time_col
].to_numpy(dtype=float)


gyro = smartphone[
    [
        gyro_yaw_col,
        gyro_pitch_col,
        gyro_roll_col
    ]
].to_numpy(dtype=float)


gravity = smartphone[
    [
        gravity_x_col,
        gravity_y_col,
        gravity_z_col
    ]
].to_numpy(dtype=float)


mag = smartphone[
    [
        mag_x_col,
        mag_y_col,
        mag_z_col
    ]
].to_numpy(dtype=float)


# ============================================================
# VALID SAMPLES
# ============================================================

valid = (
    np.isfinite(time_ms)
    &
    np.all(np.isfinite(gyro), axis=1)
    &
    np.all(np.isfinite(gravity), axis=1)
    &
    np.all(np.isfinite(mag), axis=1)
)


time_ms = time_ms[valid]
gyro = gyro[valid]
gravity = gravity[valid]
mag = mag[valid]


print(
    "VALID SAMPLES:",
    len(time_ms)
)


# ============================================================
# NORMALIZE VECTOR
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


# ============================================================
# GRAVITY-BASED ROLL AND PITCH
# ============================================================

gravity_unit = normalize(
    gravity
)


roll_gravity = np.degrees(
    np.arctan2(
        gravity_unit[:, 1],
        gravity_unit[:, 2]
    )
)


pitch_gravity = np.degrees(
    np.arctan2(
        -gravity_unit[:, 0],
        np.sqrt(
            gravity_unit[:, 1] ** 2
            +
            gravity_unit[:, 2] ** 2
        )
    )
)


# ============================================================
# GYROSCOPE
# ============================================================

gyro_yaw_deg = np.degrees(
    gyro[:, 0]
)

gyro_pitch_deg = np.degrees(
    gyro[:, 1]
)

gyro_roll_deg = np.degrees(
    gyro[:, 2]
)


# ============================================================
# CALIBRATED VEHICLE YAW RATE
# ============================================================

vehicle_yaw_rate = (
    0.029372 * gyro_yaw_deg
    +
    0.964380 * gyro_pitch_deg
    +
    0.425011 * gyro_roll_deg
    +
    0.234927
)


# ============================================================
# INITIALIZE ORIENTATION
# ============================================================

fused_roll = np.zeros(
    len(time_ms)
)

fused_pitch = np.zeros(
    len(time_ms)
)

fused_yaw = np.zeros(
    len(time_ms)
)


fused_roll[0] = (
    roll_gravity[0]
)

fused_pitch[0] = (
    pitch_gravity[0]
)

fused_yaw[0] = 0.0


# ============================================================
# TIME
# ============================================================

time_seconds = (
    time_ms / 1000.0
)


# ============================================================
# GYROSCOPE YAW INTEGRATION
# ============================================================

for i in range(
    1,
    len(time_seconds)
):

    dt = (
        time_seconds[i]
        -
        time_seconds[i - 1]
    )

    if dt <= 0 or dt > 1.0:

        fused_yaw[i] = (
            fused_yaw[i - 1]
        )

        fused_roll[i] = (
            fused_roll[i - 1]
        )

        fused_pitch[i] = (
            fused_pitch[i - 1]
        )

        continue


    fused_yaw[i] = (
        fused_yaw[i - 1]
        +
        vehicle_yaw_rate[i] * dt
    )


    fused_yaw[i] = (
        (
            fused_yaw[i]
            +
            180.0
        )
        % 360.0
    ) - 180.0


    # Gravity provides stable roll/pitch.
    fused_roll[i] = (
        roll_gravity[i]
    )

    fused_pitch[i] = (
        pitch_gravity[i]
    )


# ============================================================
# CREATE OUTPUT DATAFRAME
# ============================================================

output = pd.DataFrame({

    "TIME_MS":
        time_ms,

    "GYRO_YAW_DEG_S":
        gyro_yaw_deg,

    "GYRO_PITCH_DEG_S":
        gyro_pitch_deg,

    "GYRO_ROLL_DEG_S":
        gyro_roll_deg,

    "CALIBRATED_YAW_RATE_DEG_S":
        vehicle_yaw_rate,

    "GRAVITY_ROLL_DEG":
        roll_gravity,

    "GRAVITY_PITCH_DEG":
        pitch_gravity,

    "FUSED_ROLL_DEG":
        fused_roll,

    "FUSED_PITCH_DEG":
        fused_pitch,

    "FUSED_YAW_DEG":
        fused_yaw
})


# ============================================================
# SAVE
# ============================================================

output.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print()
print(
    "ORIENTATION ESTIMATION"
)

print(
    "======================"
)

print(
    f"Initial roll  : "
    f"{fused_roll[0]:.6f}°"
)

print(
    f"Initial pitch : "
    f"{fused_pitch[0]:.6f}°"
)

print(
    f"Initial yaw   : "
    f"{fused_yaw[0]:.6f}°"
)


print()
print(
    "FINAL ORIENTATION"
)

print(
    "================="
)

print(
    f"Roll  : "
    f"{fused_roll[-1]:.6f}°"
)

print(
    f"Pitch : "
    f"{fused_pitch[-1]:.6f}°"
)

print(
    f"Yaw   : "
    f"{fused_yaw[-1]:.6f}°"
)


print()
print(
    "ORIENTATION RANGE"
)

print(
    "=================="
)

print(
    f"Roll  : "
    f"{fused_roll.min():.6f}° "
    f"to "
    f"{fused_roll.max():.6f}°"
)

print(
    f"Pitch : "
    f"{fused_pitch.min():.6f}° "
    f"to "
    f"{fused_pitch.max():.6f}°"
)

print(
    f"Yaw   : "
    f"{fused_yaw.min():.6f}° "
    f"to "
    f"{fused_yaw.max():.6f}°"
)


print()
print(
    "FILE SAVED:"
)

print(
    OUTPUT_FILE
)

print()
print(
    "ORIENTATION SENSOR FUSION COMPLETE."
)