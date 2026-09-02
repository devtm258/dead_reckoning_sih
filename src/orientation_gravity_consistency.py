import os
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


OUTPUT_FILE = (
    "data/processed/orientation_gravity_consistency.csv"
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


def angle_error(a, b):

    return wrap_angle(a - b)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("ORIENTATION-GRAVITY CONSISTENCY ANALYSIS")
print("========================================")
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


print("COLUMNS FOUND:")
print()

print("Gravity X :", gx_col)
print("Gravity Y :", gy_col)
print("Gravity Z :", gz_col)
print("Yaw       :", yaw_col)
print("Pitch     :", pitch_col)
print("Roll      :", roll_col)

print()


# ============================================================
# EXTRACT
# ============================================================

gx = smartphone[gx_col].to_numpy(dtype=float)
gy = smartphone[gy_col].to_numpy(dtype=float)
gz = smartphone[gz_col].to_numpy(dtype=float)

yaw = smartphone[yaw_col].to_numpy(dtype=float)
pitch = smartphone[pitch_col].to_numpy(dtype=float)
roll = smartphone[roll_col].to_numpy(dtype=float)


# ============================================================
# VALID SAMPLES
# ============================================================

valid = (
    np.isfinite(gx)
    &
    np.isfinite(gy)
    &
    np.isfinite(gz)
    &
    np.isfinite(yaw)
    &
    np.isfinite(pitch)
    &
    np.isfinite(roll)
)

gx = gx[valid]
gy = gy[valid]
gz = gz[valid]

yaw = yaw[valid]
pitch = pitch[valid]
roll = roll[valid]


print(
    "VALID SAMPLES :",
    len(gx)
)

print()


# ============================================================
# NORMALIZE GRAVITY
# ============================================================

g_norm = np.sqrt(
    gx**2 +
    gy**2 +
    gz**2
)

gx_n = gx / g_norm
gy_n = gy / g_norm
gz_n = gz / g_norm


# ============================================================
# COMPUTE TILT FROM GRAVITY
# ============================================================

# Standard gravity-derived roll.
gravity_roll = np.degrees(
    np.arctan2(
        gy_n,
        gz_n
    )
)


# Standard gravity-derived pitch.
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
# PRINT BASIC COMPARISON
# ============================================================

print("RECORDED ORIENTATION")
print("=====================")

print(
    f"Yaw mean   : {np.mean(yaw):.6f}°"
)

print(
    f"Pitch mean : {np.mean(pitch):.6f}°"
)

print(
    f"Roll mean  : {np.mean(roll):.6f}°"
)

print()


print("GRAVITY-DERIVED ORIENTATION")
print("============================")

print(
    f"Pitch mean : "
    f"{np.mean(gravity_pitch):.6f}°"
)

print(
    f"Roll mean  : "
    f"{np.mean(gravity_roll):.6f}°"
)

print()


# ============================================================
# DIRECT ERRORS
# ============================================================

pitch_error = angle_error(
    gravity_pitch,
    pitch
)

roll_error = angle_error(
    gravity_roll,
    roll
)


print("DIRECT GRAVITY CONSISTENCY")
print("==========================")

print(
    f"Pitch MAE : "
    f"{np.mean(np.abs(pitch_error)):.6f}°"
)

print(
    f"Pitch median error : "
    f"{np.median(np.abs(pitch_error)):.6f}°"
)

print(
    f"Pitch maximum error : "
    f"{np.max(np.abs(pitch_error)):.6f}°"
)

print()

print(
    f"Roll MAE : "
    f"{np.mean(np.abs(roll_error)):.6f}°"
)

print(
    f"Roll median error : "
    f"{np.median(np.abs(roll_error)):.6f}°"
)

print(
    f"Roll maximum error : "
    f"{np.max(np.abs(roll_error)):.6f}°"
)

print()


# ============================================================
# TEST ROTATION/ANGLE TRANSFORMATIONS
# ============================================================

print("TESTING PITCH TRANSFORMATIONS")
print("==============================")
print()


pitch_candidates = {

    "PITCH":
        pitch,

    "-PITCH":
        -pitch,

    "PITCH + 90":
        wrap_angle(pitch + 90),

    "PITCH - 90":
        wrap_angle(pitch - 90),

    "PITCH + 180":
        wrap_angle(pitch + 180),

    "PITCH - 180":
        wrap_angle(pitch - 180),

    "90 - PITCH":
        90 - pitch,

    "-90 - PITCH":
        -90 - pitch,

    "90 + PITCH":
        90 + pitch,

    "-90 + PITCH":
        -90 + pitch
}


pitch_results = []


for name, candidate in pitch_candidates.items():

    error = angle_error(
        candidate,
        gravity_pitch
    )

    pitch_results.append({

        "TRANSFORMATION":
            name,

        "MAE_DEG":
            np.mean(np.abs(error)),

        "MEDIAN_ERROR_DEG":
            np.median(np.abs(error)),

        "STD_ERROR_DEG":
            np.std(error),

        "MAX_ERROR_DEG":
            np.max(np.abs(error))
    })


pitch_results_df = pd.DataFrame(
    pitch_results
).sort_values(
    "MAE_DEG"
)


print(
    pitch_results_df.to_string(
        index=False
    )
)

print()


# ============================================================
# ROLL TRANSFORMATIONS
# ============================================================

print("TESTING ROLL TRANSFORMATIONS")
print("============================")
print()


roll_candidates = {

    "ROLL":
        roll,

    "-ROLL":
        -roll,

    "ROLL + 90":
        wrap_angle(roll + 90),

    "ROLL - 90":
        wrap_angle(roll - 90),

    "ROLL + 180":
        wrap_angle(roll + 180),

    "ROLL - 180":
        wrap_angle(roll - 180),

    "90 - ROLL":
        90 - roll,

    "-90 - ROLL":
        -90 - roll,

    "90 + ROLL":
        90 + roll,

    "-90 + ROLL":
        -90 + roll
}


roll_results = []


for name, candidate in roll_candidates.items():

    error = angle_error(
        candidate,
        gravity_roll
    )

    roll_results.append({

        "TRANSFORMATION":
            name,

        "MAE_DEG":
            np.mean(np.abs(error)),

        "MEDIAN_ERROR_DEG":
            np.median(np.abs(error)),

        "STD_ERROR_DEG":
            np.std(error),

        "MAX_ERROR_DEG":
            np.max(np.abs(error))
    })


roll_results_df = pd.DataFrame(
    roll_results
).sort_values(
    "MAE_DEG"
)


print(
    roll_results_df.to_string(
        index=False
    )
)

print()


# ============================================================
# CORRELATIONS
# ============================================================

print("CORRELATION ANALYSIS")
print("====================")

pitch_correlation = np.corrcoef(
    gravity_pitch,
    pitch
)[0, 1]

roll_correlation = np.corrcoef(
    gravity_roll,
    roll
)[0, 1]


print(
    f"Gravity pitch vs recorded pitch : "
    f"{pitch_correlation:.6f}"
)

print(
    f"Gravity roll vs recorded roll   : "
    f"{roll_correlation:.6f}"
)

print()


# ============================================================
# SAMPLE-BY-SAMPLE OUTPUT
# ============================================================

sample_output = pd.DataFrame({

    "GRAVITY_X":
        gx,

    "GRAVITY_Y":
        gy,

    "GRAVITY_Z":
        gz,

    "RECORDED_YAW":
        yaw,

    "RECORDED_PITCH":
        pitch,

    "RECORDED_ROLL":
        roll,

    "GRAVITY_PITCH":
        gravity_pitch,

    "GRAVITY_ROLL":
        gravity_roll,

    "PITCH_ERROR":
        pitch_error,

    "ROLL_ERROR":
        roll_error
})


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "data/processed",
    exist_ok=True
)

sample_output.to_csv(
    OUTPUT_FILE,
    index=False
)


print("RESULTS SAVED:")
print(
    OUTPUT_FILE
)

print()

print(
    "ORIENTATION-GRAVITY CONSISTENCY ANALYSIS COMPLETE."
)