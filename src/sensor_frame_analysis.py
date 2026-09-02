import pandas as pd
import numpy as np

from load_data import load_smartphone_data


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()


# ============================================================
# EXTRACT ACCELEROMETER
# ============================================================

acc_x = smartphone["ACCELEROMETER X (m/s²)"]
acc_y = smartphone["ACCELEROMETER Y (m/s²)"]
acc_z = smartphone["ACCELEROMETER Z (m/s²)"]


# ============================================================
# EXTRACT GRAVITY
# ============================================================

grav_x = smartphone["GRAVITY X (m/s²)"]
grav_y = smartphone["GRAVITY Y (m/s²)"]
grav_z = smartphone["GRAVITY Z (m/s²)"]


# ============================================================
# EXTRACT ORIENTATION
# ============================================================

yaw = smartphone["ORIENTATION (Yaw) (Â°)"]
pitch = smartphone["ORIENTATION (Pitch) (Â°)"]
roll = smartphone["ORIENTATION (Roll ) (Â°)"]

gps_orientation = smartphone["GPS ORIENTATION (Â°)"]


# ============================================================
# MAGNETOMETER
# ============================================================

mag_x = smartphone["MAGNETIC FIELD X (Î¼T)"]
mag_y = smartphone["MAGNETIC FIELD Y (Î¼T)"]
mag_z = smartphone["MAGNETIC FIELD Z (Î¼T)"]


# ============================================================
# GRAVITY MAGNITUDE
# ============================================================

gravity_magnitude = np.sqrt(
    grav_x**2 +
    grav_y**2 +
    grav_z**2
)


# ============================================================
# NORMALIZED GRAVITY
# ============================================================

gx = grav_x / gravity_magnitude
gy = grav_y / gravity_magnitude
gz = grav_z / gravity_magnitude


# ============================================================
# PRINT GRAVITY AXIS STATISTICS
# ============================================================

print("SENSOR FRAME ANALYSIS")
print("=====================")

print("\nGRAVITY AXIS STATISTICS")

print(
    f"Gravity X mean : {grav_x.mean():.6f}"
)

print(
    f"Gravity Y mean : {grav_y.mean():.6f}"
)

print(
    f"Gravity Z mean : {grav_z.mean():.6f}"
)

print(
    f"Gravity X std  : {grav_x.std():.6f}"
)

print(
    f"Gravity Y std  : {grav_y.std():.6f}"
)

print(
    f"Gravity Z std  : {grav_z.std():.6f}"
)


# ============================================================
# GRAVITY DOMINANCE
# ============================================================

print("\n\nNORMALIZED GRAVITY")

print(
    f"X mean : {gx.mean():.6f}"
)

print(
    f"Y mean : {gy.mean():.6f}"
)

print(
    f"Z mean : {gz.mean():.6f}"
)


# ============================================================
# ORIENTATION STATISTICS
# ============================================================

print("\n\nORIENTATION")

print(
    f"Yaw mean   : {yaw.mean():.6f}°"
)

print(
    f"Pitch mean : {pitch.mean():.6f}°"
)

print(
    f"Roll mean  : {roll.mean():.6f}°"
)

print(
    f"GPS orientation mean : "
    f"{gps_orientation.mean():.6f}°"
)


# ============================================================
# CORRELATION MATRIX
# ============================================================

analysis = pd.DataFrame({

    "ACC_X": acc_x,
    "ACC_Y": acc_y,
    "ACC_Z": acc_z,

    "GRAV_X": grav_x,
    "GRAV_Y": grav_y,
    "GRAV_Z": grav_z,

    "MAG_X": mag_x,
    "MAG_Y": mag_y,
    "MAG_Z": mag_z,

    "YAW": yaw,
    "PITCH": pitch,
    "ROLL": roll,

    "GPS_ORIENTATION":
        gps_orientation
})


print("\n\nCORRELATION MATRIX")

print(
    analysis.corr().round(4).to_string()
)


# ============================================================
# MAGNETOMETER AXIS CORRELATION WITH ORIENTATION
# ============================================================

print("\n\nMAGNETOMETER VS ORIENTATION")

print(
    analysis[
        [
            "MAG_X",
            "MAG_Y",
            "MAG_Z",
            "YAW",
            "PITCH",
            "ROLL"
        ]
    ]
    .corr()
    .round(4)
    .to_string()
)


# ============================================================
# FIRST 20 SAMPLES
# ============================================================

print("\n\nFIRST 20 SENSOR FRAME SAMPLES")

print(
    analysis[
        [
            "GRAV_X",
            "GRAV_Y",
            "GRAV_Z",
            "MAG_X",
            "MAG_Y",
            "MAG_Z",
            "YAW",
            "PITCH",
            "ROLL"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# LAST 20 SAMPLES
# ============================================================

print("\n\nLAST 20 SENSOR FRAME SAMPLES")

print(
    analysis[
        [
            "GRAV_X",
            "GRAV_Y",
            "GRAV_Z",
            "MAG_X",
            "MAG_Y",
            "MAG_Z",
            "YAW",
            "PITCH",
            "ROLL"
        ]
    ]
    .tail(20)
    .to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

analysis.to_csv(
    "data/processed/sensor_frame_analysis.csv",
    index=False
)

print("\n\nAnalysis saved to:")

print(
    "data/processed/sensor_frame_analysis.csv"
)