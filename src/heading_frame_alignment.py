import os
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


OUTPUT_FILE = (
    "data/processed/heading_frame_alignment.csv"
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
        f"Could not find column containing: {text}"
    )


# ============================================================
# ANGLE FUNCTIONS
# ============================================================

def wrap_angle(angle):

    return (
        (angle + 180.0) % 360.0
    ) - 180.0


def circular_error(a, b):

    return wrap_angle(a - b)


# ============================================================
# LOAD
# ============================================================

print()
print("HEADING FRAME ALIGNMENT ANALYSIS")
print("================================")
print()

smartphone = load_smartphone_data()


# ============================================================
# COLUMNS
# ============================================================

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

gps_col = find_column(
    smartphone,
    "GPS ORIENTATION"
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

print("MAG X :", mx_col)
print("MAG Y :", my_col)
print("MAG Z :", mz_col)
print("GPS  :", gps_col)
print("YAW  :", yaw_col)
print("PITCH:", pitch_col)
print("ROLL :", roll_col)

print()


# ============================================================
# DATA
# ============================================================

mx = smartphone[mx_col].to_numpy(dtype=float)
my = smartphone[my_col].to_numpy(dtype=float)
mz = smartphone[mz_col].to_numpy(dtype=float)

gps = smartphone[gps_col].to_numpy(dtype=float)
yaw = smartphone[yaw_col].to_numpy(dtype=float)
pitch = smartphone[pitch_col].to_numpy(dtype=float)
roll = smartphone[roll_col].to_numpy(dtype=float)


valid = (
    np.isfinite(mx)
    &
    np.isfinite(my)
    &
    np.isfinite(mz)
    &
    np.isfinite(gps)
    &
    np.isfinite(yaw)
    &
    np.isfinite(pitch)
    &
    np.isfinite(roll)
)


mx = mx[valid]
my = my[valid]
mz = mz[valid]

gps = gps[valid]
yaw = yaw[valid]
pitch = pitch[valid]
roll = roll[valid]


print(
    "VALID SAMPLES :",
    len(mx)
)

print()


# ============================================================
# HARD-IRON CORRECTION
# ============================================================

bias_x = (
    np.min(mx) +
    np.max(mx)
) / 2.0

bias_y = (
    np.min(my) +
    np.max(my)
) / 2.0

bias_z = (
    np.min(mz) +
    np.max(mz)
) / 2.0


mx_c = mx - bias_x
my_c = my - bias_y
mz_c = mz - bias_z


print("HARD-IRON BIASES")
print("=================")

print(
    f"X : {bias_x:.6f} µT"
)

print(
    f"Y : {bias_y:.6f} µT"
)

print(
    f"Z : {bias_z:.6f} µT"
)

print()


# ============================================================
# HORIZONTAL MAGNETIC HEADING
# ============================================================

raw_heading = np.degrees(
    np.arctan2(
        my,
        mx
    )
) % 360.0


corrected_heading = np.degrees(
    np.arctan2(
        my_c,
        mx_c
    )
) % 360.0


# ============================================================
# CONSTANT OFFSET SEARCH
# ============================================================

print("SEARCHING CONSTANT HEADING OFFSET")
print("=================================")
print()


offset_results = []


for offset in np.arange(
    -180.0,
    180.001,
    0.5
):

    candidate = (
        corrected_heading +
        offset
    ) % 360.0

    error = circular_error(
        candidate,
        gps
    )

    offset_results.append({

        "OFFSET_DEG":
            offset,

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


offset_df = pd.DataFrame(
    offset_results
).sort_values(
    "MAE_DEG"
)


print(
    offset_df.head(10).to_string(
        index=False
    )
)

print()


# ============================================================
# BEST OFFSET
# ============================================================

best_offset = (
    offset_df.iloc[0]["OFFSET_DEG"]
)

best_offset_heading = (
    corrected_heading +
    best_offset
) % 360.0


print("BEST CONSTANT OFFSET")
print("====================")

print(
    f"Offset : {best_offset:.6f}°"
)

print()


# ============================================================
# TEST SIGN + OFFSET
# ============================================================

print("SIGN + OFFSET SEARCH")
print("====================")
print()


sign_offset_results = []


for sign in [1, -1]:

    for offset in np.arange(
        -180.0,
        180.001,
        0.5
    ):

        candidate = (
            sign *
            corrected_heading +
            offset
        ) % 360.0

        error = circular_error(
            candidate,
            gps
        )

        sign_offset_results.append({

            "SIGN":
                sign,

            "OFFSET_DEG":
                offset,

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


sign_offset_df = pd.DataFrame(
    sign_offset_results
).sort_values(
    "MAE_DEG"
)


print(
    sign_offset_df.head(10).to_string(
        index=False
    )
)

print()


best_sign = (
    sign_offset_df.iloc[0]["SIGN"]
)

best_sign_offset = (
    sign_offset_df.iloc[0]["OFFSET_DEG"]
)


best_aligned_heading = (
    best_sign *
    corrected_heading +
    best_sign_offset
) % 360.0


# ============================================================
# RECORDED YAW ALIGNMENT
# ============================================================

print("RECORDED YAW ALIGNMENT")
print("======================")
print()


yaw_results = []


for sign in [1, -1]:

    for offset in np.arange(
        -180.0,
        180.001,
        0.5
    ):

        candidate = (
            sign *
            yaw +
            offset
        ) % 360.0

        error = circular_error(
            candidate,
            gps
        )

        yaw_results.append({

            "SIGN":
                sign,

            "OFFSET_DEG":
                offset,

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
    yaw_results_df.head(10).to_string(
        index=False
    )
)

print()


# ============================================================
# BEST RECORDED YAW TRANSFORMATION
# ============================================================

best_yaw_sign = (
    yaw_results_df.iloc[0]["SIGN"]
)

best_yaw_offset = (
    yaw_results_df.iloc[0]["OFFSET_DEG"]
)

best_yaw_heading = (
    best_yaw_sign *
    yaw +
    best_yaw_offset
) % 360.0


# ============================================================
# FINAL COMPARISON
# ============================================================

print("FINAL HEADING FRAME COMPARISON")
print("==============================")
print()


physical_error = circular_error(
    corrected_heading,
    gps
)

aligned_error = circular_error(
    best_aligned_heading,
    gps
)

recorded_yaw_error = circular_error(
    yaw,
    gps
)

transformed_yaw_error = circular_error(
    best_yaw_heading,
    gps
)


comparison = pd.DataFrame({

    "MODEL": [

        "Hard-Iron Magnetometer",

        "Aligned Magnetometer",

        "Recorded Smartphone Yaw",

        "Aligned Smartphone Yaw"
    ],

    "MAE_DEG": [

        np.mean(
            np.abs(physical_error)
        ),

        np.mean(
            np.abs(aligned_error)
        ),

        np.mean(
            np.abs(recorded_yaw_error)
        ),

        np.mean(
            np.abs(transformed_yaw_error)
        )
    ],

    "MEDIAN_ERROR_DEG": [

        np.median(
            np.abs(physical_error)
        ),

        np.median(
            np.abs(aligned_error)
        ),

        np.median(
            np.abs(recorded_yaw_error)
        ),

        np.median(
            np.abs(transformed_yaw_error)
        )
    ],

    "STD_ERROR_DEG": [

        np.std(
            physical_error
        ),

        np.std(
            aligned_error
        ),

        np.std(
            recorded_yaw_error
        ),

        np.std(
            transformed_yaw_error
        )
    ],

    "MAX_ERROR_DEG": [

        np.max(
            np.abs(physical_error)
        ),

        np.max(
            np.abs(aligned_error)
        ),

        np.max(
            np.abs(recorded_yaw_error)
        ),

        np.max(
            np.abs(transformed_yaw_error)
        )
    ]
})


print(
    comparison.to_string(
        index=False
    )
)

print()


# ============================================================
# SAMPLE OUTPUT
# ============================================================

results = pd.DataFrame({

    "MAG_X":
        mx,

    "MAG_Y":
        my,

    "MAG_Z":
        mz,

    "CORRECTED_MAG_X":
        mx_c,

    "CORRECTED_MAG_Y":
        my_c,

    "CORRECTED_MAG_Z":
        mz_c,

    "GPS_HEADING":
        gps,

    "RAW_MAG_HEADING":
        raw_heading,

    "CORRECTED_MAG_HEADING":
        corrected_heading,

    "ALIGNED_MAG_HEADING":
        best_aligned_heading,

    "RECORDED_YAW":
        yaw,

    "ALIGNED_RECORDED_YAW":
        best_yaw_heading,

    "PITCH":
        pitch,

    "ROLL":
        roll
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


offset_df.to_csv(
    "data/processed/"
    "heading_constant_offset_search.csv",
    index=False
)


sign_offset_df.to_csv(
    "data/processed/"
    "heading_sign_offset_search.csv",
    index=False
)


yaw_results_df.to_csv(
    "data/processed/"
    "recorded_yaw_sign_offset_search.csv",
    index=False
)


comparison.to_csv(
    "data/processed/"
    "heading_frame_comparison.csv",
    index=False
)


print("FILES SAVED:")
print(
    OUTPUT_FILE
)

print(
    "data/processed/"
    "heading_constant_offset_search.csv"
)

print(
    "data/processed/"
    "heading_sign_offset_search.csv"
)

print(
    "data/processed/"
    "recorded_yaw_sign_offset_search.csv"
)

print(
    "data/processed/"
    "heading_frame_comparison.csv"
)

print()

print(
    "HEADING FRAME ALIGNMENT COMPLETE."
)