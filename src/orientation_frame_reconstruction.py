import os
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


OUTPUT_FILE = (
    "data/processed/orientation_frame_reconstruction.csv"
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
        f"Column not found: {text}\n"
        f"Available columns:\n{list(df.columns)}"
    )


# ============================================================
# ANGLE UTILITIES
# ============================================================

def wrap_angle(angle):

    return (
        (angle + 180.0) % 360.0
    ) - 180.0


def circular_error(a, b):

    return wrap_angle(a - b)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("ORIENTATION FRAME RECONSTRUCTION")
print("================================")
print()

smartphone = load_smartphone_data()


# ============================================================
# FIND COLUMNS
# ============================================================

gx_col = find_column(
    smartphone,
    "GRAVITY X"
)

gy_col = find_column(
    smartphone,
    "GRAVITY Y"
)

gz_col = find_column(
    smartphone,
    "GRAVITY Z"
)

mx_col = find_column(
    smartphone,
    "MAGNETIC FIELD X"
)

my_col = find_column(
    smartphone,
    "MAGNETIC FIELD Y"
)

mz_col = find_column(
    smartphone,
    "MAGNETIC FIELD Z"
)

yaw_col = find_column(
    smartphone,
    "ORIENTATION (YAW)"
)

pitch_col = find_column(
    smartphone,
    "ORIENTATION (PITCH)"
)

roll_col = find_column(
    smartphone,
    "ORIENTATION (ROLL"
)

gps_col = find_column(
    smartphone,
    "GPS ORIENTATION"
)


print("COLUMNS FOUND:")
print()

print("Gravity X :", gx_col)
print("Gravity Y :", gy_col)
print("Gravity Z :", gz_col)

print("Magnetic X :", mx_col)
print("Magnetic Y :", my_col)
print("Magnetic Z :", mz_col)

print("Yaw :", yaw_col)
print("Pitch :", pitch_col)
print("Roll :", roll_col)

print("GPS orientation :", gps_col)

print()


# ============================================================
# EXTRACT DATA
# ============================================================

gx = smartphone[gx_col].to_numpy(dtype=float)
gy = smartphone[gy_col].to_numpy(dtype=float)
gz = smartphone[gz_col].to_numpy(dtype=float)

mx = smartphone[mx_col].to_numpy(dtype=float)
my = smartphone[my_col].to_numpy(dtype=float)
mz = smartphone[mz_col].to_numpy(dtype=float)

recorded_yaw = smartphone[yaw_col].to_numpy(dtype=float)
recorded_pitch = smartphone[pitch_col].to_numpy(dtype=float)
recorded_roll = smartphone[roll_col].to_numpy(dtype=float)

gps_heading = smartphone[gps_col].to_numpy(dtype=float)


# ============================================================
# VALID DATA
# ============================================================

valid = (
    np.isfinite(gx)
    &
    np.isfinite(gy)
    &
    np.isfinite(gz)
    &
    np.isfinite(mx)
    &
    np.isfinite(my)
    &
    np.isfinite(mz)
    &
    np.isfinite(recorded_yaw)
    &
    np.isfinite(recorded_pitch)
    &
    np.isfinite(recorded_roll)
    &
    np.isfinite(gps_heading)
)


gx = gx[valid]
gy = gy[valid]
gz = gz[valid]

mx = mx[valid]
my = my[valid]
mz = mz[valid]

recorded_yaw = recorded_yaw[valid]
recorded_pitch = recorded_pitch[valid]
recorded_roll = recorded_roll[valid]

gps_heading = gps_heading[valid]


print(
    "VALID SAMPLES :",
    len(gx)
)

print()


# ============================================================
# NORMALIZE GRAVITY
# ============================================================

g_mag = np.sqrt(
    gx**2 +
    gy**2 +
    gz**2
)

gx_n = gx / g_mag
gy_n = gy / g_mag
gz_n = gz / g_mag


# ============================================================
# COMPUTE GRAVITY-DERIVED TILT
# ============================================================

gravity_roll = np.degrees(
    np.arctan2(
        gy_n,
        gz_n
    )
)

gravity_pitch = np.degrees(
    np.arctan2(
        -gx_n,
        np.sqrt(
            gy_n**2 +
            gz_n**2
        )
    )
)


# ============================================================
# TILT COMPENSATE MAGNETOMETER
# ============================================================

# Rotate magnetic vector using the gravity-derived
# pitch and roll.

pitch_rad = np.radians(
    gravity_pitch
)

roll_rad = np.radians(
    gravity_roll
)


# Rotation around X
mx_r = mx

my_r = (
    my * np.cos(roll_rad)
    -
    mz * np.sin(roll_rad)
)

mz_r = (
    my * np.sin(roll_rad)
    +
    mz * np.cos(roll_rad)
)


# Rotation around Y
mx_h = (
    mx_r * np.cos(pitch_rad)
    +
    mz_r * np.sin(pitch_rad)
)

my_h = my_r


# ============================================================
# MAGNETIC HEADING CANDIDATES
# ============================================================

heading_candidates = {

    "atan2(MY_H, MX_H)":
        np.degrees(
            np.arctan2(
                my_h,
                mx_h
            )
        ),

    "atan2(-MY_H, MX_H)":
        np.degrees(
            np.arctan2(
                -my_h,
                mx_h
            )
        ),

    "atan2(MX_H, MY_H)":
        np.degrees(
            np.arctan2(
                mx_h,
                my_h
            )
        ),

    "atan2(-MX_H, MY_H)":
        np.degrees(
            np.arctan2(
                -mx_h,
                my_h
            )
        )
}


# ============================================================
# HEADING TEST
# ============================================================

heading_results = []


for name, heading in heading_candidates.items():

    heading = heading % 360.0

    error = circular_error(
        heading,
        gps_heading
    )

    heading_results.append({

        "FORMULA":
            name,

        "MAE_DEG":
            np.mean(
                np.abs(error)
            ),

        "MEDIAN_ERROR_DEG":
            np.median(
                np.abs(error)
            ),

        "STD_ERROR_DEG":
            np.std(error),

        "MAX_ERROR_DEG":
            np.max(
                np.abs(error)
            )
    })


heading_results_df = pd.DataFrame(
    heading_results
).sort_values(
    "MAE_DEG"
)


print("TILT-COMPENSATED HEADING TEST")
print("==============================")
print()

print(
    heading_results_df.to_string(
        index=False
    )
)

print()


# ============================================================
# BEST HEADING
# ============================================================

best_formula = (
    heading_results_df.iloc[0]["FORMULA"]
)


best_heading = (
    heading_candidates[best_formula]
    % 360.0
)


print("BEST HEADING")
print("============")

print(
    "Formula :",
    best_formula
)

print()


# ============================================================
# COMPARE RECORDED YAW
# ============================================================

yaw_error = circular_error(
    best_heading,
    recorded_yaw
)

gps_error = circular_error(
    best_heading,
    gps_heading
)


print("RECORDED YAW VS RECONSTRUCTED HEADING")
print("======================================")
print()

print(
    f"MAE against recorded yaw : "
    f"{np.mean(np.abs(yaw_error)):.6f}°"
)

print(
    f"Median error : "
    f"{np.median(np.abs(yaw_error)):.6f}°"
)

print(
    f"MAE against GPS heading : "
    f"{np.mean(np.abs(gps_error)):.6f}°"
)

print(
    f"Median GPS error : "
    f"{np.median(np.abs(gps_error)):.6f}°"
)

print()


# ============================================================
# TEST RECORDED ORIENTATION TRANSFORMATIONS
# ============================================================

print("RECORDED YAW TRANSFORMATION TEST")
print("=================================")
print()


yaw_transformations = {

    "YAW":
        recorded_yaw,

    "-YAW":
        -recorded_yaw,

    "YAW + 90":
        wrap_angle(
            recorded_yaw + 90
        ),

    "YAW - 90":
        wrap_angle(
            recorded_yaw - 90
        ),

    "YAW + 180":
        wrap_angle(
            recorded_yaw + 180
        ),

    "YAW - 180":
        wrap_angle(
            recorded_yaw - 180
        )
}


yaw_results = []


for name, candidate in yaw_transformations.items():

    error = circular_error(
        candidate,
        best_heading
    )

    yaw_results.append({

        "TRANSFORMATION":
            name,

        "MAE_DEG":
            np.mean(
                np.abs(error)
            ),

        "MEDIAN_ERROR_DEG":
            np.median(
                np.abs(error)
            ),

        "STD_ERROR_DEG":
            np.std(error),

        "MAX_ERROR_DEG":
            np.max(
                np.abs(error)
            )
    })


yaw_results_df = pd.DataFrame(
    yaw_results
).sort_values(
    "MAE_DEG"
)


print(
    yaw_results_df.to_string(
        index=False
    )
)

print()


# ============================================================
# RECONSTRUCTED ORIENTATION DATA
# ============================================================

results = pd.DataFrame({

    "GRAVITY_X":
        gx,

    "GRAVITY_Y":
        gy,

    "GRAVITY_Z":
        gz,

    "MAGNETIC_X":
        mx,

    "MAGNETIC_Y":
        my,

    "MAGNETIC_Z":
        mz,

    "GRAVITY_PITCH":
        gravity_pitch,

    "GRAVITY_ROLL":
        gravity_roll,

    "HORIZONTAL_MAG_X":
        mx_h,

    "HORIZONTAL_MAG_Y":
        my_h,

    "RECONSTRUCTED_HEADING":
        best_heading,

    "RECORDED_YAW":
        recorded_yaw,

    "RECORDED_PITCH":
        recorded_pitch,

    "RECORDED_ROLL":
        recorded_roll,

    "GPS_HEADING":
        gps_heading,

    "HEADING_ERROR":
        gps_error
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


print("RESULTS SAVED:")
print(
    OUTPUT_FILE
)

print()

print(
    "ORIENTATION FRAME RECONSTRUCTION COMPLETE."
)