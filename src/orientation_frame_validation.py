import os
import itertools
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = (
    "data/processed/orientation_frame_validation.csv"
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
        f"Column containing '{text}' not found.\n"
        f"Available columns:\n{list(df.columns)}"
    )


# ============================================================
# ANGLE FUNCTIONS
# ============================================================

def wrap_angle(angle):

    return (
        (angle + 180.0) % 360.0
    ) - 180.0


def angular_difference(a, b):

    return wrap_angle(a - b)


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(predicted, reference):

    error = angular_difference(
        predicted,
        reference
    )

    absolute_error = np.abs(error)

    return {
        "MAE_DEG":
            np.mean(absolute_error),

        "MEDIAN_ERROR_DEG":
            np.median(absolute_error),

        "STD_ERROR_DEG":
            np.std(error),

        "MAX_ERROR_DEG":
            np.max(absolute_error)
    }


# ============================================================
# LOAD DATA
# ============================================================

print()
print("SMARTPHONE ORIENTATION FRAME VALIDATION")
print("=======================================")
print()

smartphone = load_smartphone_data()


# ============================================================
# FIND COLUMNS
# ============================================================

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

orientation_pitch_column = find_column(
    smartphone,
    "ORIENTATION (PITCH)"
)

orientation_roll_column = find_column(
    smartphone,
    "ORIENTATION (ROLL"
)


print("COLUMNS FOUND:")
print()

print(
    "Gravity X :",
    gravity_x_column
)

print(
    "Gravity Y :",
    gravity_y_column
)

print(
    "Gravity Z :",
    gravity_z_column
)

print(
    "Pitch     :",
    orientation_pitch_column
)

print(
    "Roll      :",
    orientation_roll_column
)

print()


# ============================================================
# EXTRACT DATA
# ============================================================

gx = smartphone[
    gravity_x_column
].to_numpy(dtype=float)

gy = smartphone[
    gravity_y_column
].to_numpy(dtype=float)

gz = smartphone[
    gravity_z_column
].to_numpy(dtype=float)

reference_pitch = smartphone[
    orientation_pitch_column
].to_numpy(dtype=float)

reference_roll = smartphone[
    orientation_roll_column
].to_numpy(dtype=float)


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
    np.isfinite(reference_pitch)
    &
    np.isfinite(reference_roll)
)


gx = gx[valid]
gy = gy[valid]
gz = gz[valid]

reference_pitch = (
    reference_pitch[valid]
)

reference_roll = (
    reference_roll[valid]
)


print(
    "VALID SAMPLES :",
    len(gx)
)

print()


# ============================================================
# NORMALIZE GRAVITY
# ============================================================

gravity_magnitude = np.sqrt(
    gx**2 +
    gy**2 +
    gz**2
)


nx = gx / gravity_magnitude
ny = gy / gravity_magnitude
nz = gz / gravity_magnitude


# ============================================================
# TEST ALL GRAVITY AXIS COMBINATIONS
# ============================================================

print("TESTING GRAVITY FRAME CONVENTIONS...")
print()


results = []


# Every gravity axis can independently have
# either positive or negative sign.

signs = [-1, 1]


# ------------------------------------------------------------
# PITCH / ROLL FORMULATIONS
# ------------------------------------------------------------

for sx, sy, sz in itertools.product(
    signs,
    signs,
    signs
):

    x = sx * nx
    y = sy * ny
    z = sz * nz


    # --------------------------------------------------------
    # CONVENTION A
    # --------------------------------------------------------

    pitch_a = np.degrees(
        np.arctan2(
            -x,
            np.sqrt(
                y**2 +
                z**2
            )
        )
    )

    roll_a = np.degrees(
        np.arctan2(
            y,
            z
        )
    )


    pitch_metrics_a = (
        calculate_metrics(
            pitch_a,
            reference_pitch
        )
    )

    roll_metrics_a = (
        calculate_metrics(
            roll_a,
            reference_roll
        )
    )


    results.append({

        "SIGN_X": sx,
        "SIGN_Y": sy,
        "SIGN_Z": sz,

        "FORMULA": "STANDARD",

        "PITCH_MAE_DEG":
            pitch_metrics_a["MAE_DEG"],

        "PITCH_MEDIAN_DEG":
            pitch_metrics_a[
                "MEDIAN_ERROR_DEG"
            ],

        "PITCH_STD_DEG":
            pitch_metrics_a[
                "STD_ERROR_DEG"
            ],

        "PITCH_MAX_DEG":
            pitch_metrics_a[
                "MAX_ERROR_DEG"
            ],

        "ROLL_MAE_DEG":
            roll_metrics_a["MAE_DEG"],

        "ROLL_MEDIAN_DEG":
            roll_metrics_a[
                "MEDIAN_ERROR_DEG"
            ],

        "ROLL_STD_DEG":
            roll_metrics_a[
                "STD_ERROR_DEG"
            ],

        "ROLL_MAX_DEG":
            roll_metrics_a[
                "MAX_ERROR_DEG"
            ],

        "TOTAL_MAE":
            (
                pitch_metrics_a["MAE_DEG"]
                +
                roll_metrics_a["MAE_DEG"]
            )
    })


# ============================================================
# ALTERNATIVE FRAME FORMULATIONS
# ============================================================

alternative_results = []


for sx, sy, sz in itertools.product(
    signs,
    signs,
    signs
):

    x = sx * nx
    y = sy * ny
    z = sz * nz


    # --------------------------------------------------------
    # FORMULA 1
    # --------------------------------------------------------

    pitch = np.degrees(
        np.arctan2(
            x,
            np.sqrt(
                y**2 +
                z**2
            )
        )
    )

    roll = np.degrees(
        np.arctan2(
            y,
            z
        )
    )


    pitch_m = calculate_metrics(
        pitch,
        reference_pitch
    )

    roll_m = calculate_metrics(
        roll,
        reference_roll
    )


    alternative_results.append({

        "SIGN_X": sx,
        "SIGN_Y": sy,
        "SIGN_Z": sz,

        "FORMULA":
            "PITCH=atan2(X,sqrt(Y²+Z²)), "
            "ROLL=atan2(Y,Z)",

        "PITCH_MAE_DEG":
            pitch_m["MAE_DEG"],

        "ROLL_MAE_DEG":
            roll_m["MAE_DEG"],

        "TOTAL_MAE":
            (
                pitch_m["MAE_DEG"]
                +
                roll_m["MAE_DEG"]
            )
    })


    # --------------------------------------------------------
    # FORMULA 2
    # --------------------------------------------------------

    pitch = np.degrees(
        np.arctan2(
            -x,
            z
        )
    )

    roll = np.degrees(
        np.arctan2(
            y,
            np.sqrt(
                x**2 +
                z**2
            )
        )
    )


    pitch_m = calculate_metrics(
        pitch,
        reference_pitch
    )

    roll_m = calculate_metrics(
        roll,
        reference_roll
    )


    alternative_results.append({

        "SIGN_X": sx,
        "SIGN_Y": sy,
        "SIGN_Z": sz,

        "FORMULA":
            "PITCH=atan2(-X,Z), "
            "ROLL=atan2(Y,sqrt(X²+Z²))",

        "PITCH_MAE_DEG":
            pitch_m["MAE_DEG"],

        "ROLL_MAE_DEG":
            roll_m["MAE_DEG"],

        "TOTAL_MAE":
            (
                pitch_m["MAE_DEG"]
                +
                roll_m["MAE_DEG"]
            )
    })


    # --------------------------------------------------------
    # FORMULA 3
    # --------------------------------------------------------

    pitch = np.degrees(
        np.arctan2(
            x,
            z
        )
    )

    roll = np.degrees(
        np.arctan2(
            -y,
            np.sqrt(
                x**2 +
                z**2
            )
        )
    )


    pitch_m = calculate_metrics(
        pitch,
        reference_pitch
    )

    roll_m = calculate_metrics(
        roll,
        reference_roll
    )


    alternative_results.append({

        "SIGN_X": sx,
        "SIGN_Y": sy,
        "SIGN_Z": sz,

        "FORMULA":
            "PITCH=atan2(X,Z), "
            "ROLL=atan2(-Y,sqrt(X²+Z²))",

        "PITCH_MAE_DEG":
            pitch_m["MAE_DEG"],

        "ROLL_MAE_DEG":
            roll_m["MAE_DEG"],

        "TOTAL_MAE":
            (
                pitch_m["MAE_DEG"]
                +
                roll_m["MAE_DEG"]
            )
    })


# ============================================================
# COMBINE RESULTS
# ============================================================

all_results = pd.DataFrame(
    results +
    alternative_results
)


# ============================================================
# SORT
# ============================================================

all_results = all_results.sort_values(
    "TOTAL_MAE",
    ascending=True
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("BEST FRAME CONVENTIONS")
print("======================")
print()

print(
    all_results.head(20).to_string(
        index=False
    )
)

print()


# ============================================================
# BEST RESULT
# ============================================================

best = all_results.iloc[0]


print("BEST FRAME")
print("==========")
print()

print(
    "Sign X :",
    best["SIGN_X"]
)

print(
    "Sign Y :",
    best["SIGN_Y"]
)

print(
    "Sign Z :",
    best["SIGN_Z"]
)

print(
    "Formula :",
    best["FORMULA"]
)

print(
    f"Pitch MAE : "
    f"{best['PITCH_MAE_DEG']:.6f}°"
)

print(
    f"Roll MAE  : "
    f"{best['ROLL_MAE_DEG']:.6f}°"
)

print(
    f"Total MAE : "
    f"{best['TOTAL_MAE']:.6f}°"
)

print()


# ============================================================
# REFERENCE ORIENTATION STATISTICS
# ============================================================

print("REFERENCE ORIENTATION")
print("=====================")
print()

print(
    f"Pitch mean : "
    f"{np.mean(reference_pitch):.6f}°"
)

print(
    f"Pitch std  : "
    f"{np.std(reference_pitch):.6f}°"
)

print(
    f"Roll mean  : "
    f"{np.mean(reference_roll):.6f}°"
)

print(
    f"Roll std   : "
    f"{np.std(reference_roll):.6f}°"
)

print()


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "data/processed",
    exist_ok=True
)

all_results.to_csv(
    OUTPUT_FILE,
    index=False
)


print("RESULTS SAVED:")
print(
    OUTPUT_FILE
)

print()

print(
    "ORIENTATION FRAME VALIDATION COMPLETE."
)