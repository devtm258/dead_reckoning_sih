import os
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# LOAD DATA
# ============================================================

data = load_smartphone_data()

print("\nFUSED HEADING OUTLIER ANALYSIS")
print("==============================")

TIME = "TIME SINCE START (ms)"

GYRO_YAW = "GYROSCOPE Yaw (rad/s)"
GYRO_PITCH = "GYROSCOPE Pitch (rad/s)"
GYRO_ROLL = "GYROSCOPE Roll (rad/s)"

GPS_HEADING = "GPS ORIENTATION (Â°)"
GPS_SPEED = "GPS SPEED (Kmh)"

GRAV_X = "GRAVITY X (m/s²)"
GRAV_Y = "GRAVITY Y (m/s²)"
GRAV_Z = "GRAVITY Z (m/s²)"

required = [
    TIME,
    GYRO_YAW,
    GYRO_PITCH,
    GYRO_ROLL,
    GPS_HEADING,
    GPS_SPEED,
    GRAV_X,
    GRAV_Y,
    GRAV_Z
]

for col in required:

    if col not in data.columns:
        raise ValueError(
            f"Missing column: {col}"
        )


df = data[required].copy()

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)

df = df.dropna().reset_index(
    drop=True
)

print(
    f"\nVALID SAMPLES: {len(df)}"
)


# ============================================================
# ARRAYS
# ============================================================

time = (
    df[TIME].to_numpy(float)
    / 1000.0
)

gyro_yaw = np.degrees(
    df[GYRO_YAW].to_numpy(float)
)

gyro_pitch = np.degrees(
    df[GYRO_PITCH].to_numpy(float)
)

gyro_roll = np.degrees(
    df[GYRO_ROLL].to_numpy(float)
)

gps_heading = df[
    GPS_HEADING
].to_numpy(float)

gps_speed = df[
    GPS_SPEED
].to_numpy(float)

gravity_x = df[
    GRAV_X
].to_numpy(float)

gravity_y = df[
    GRAV_Y
].to_numpy(float)

gravity_z = df[
    GRAV_Z
].to_numpy(float)


# ============================================================
# ANGLE FUNCTIONS
# ============================================================

def wrap_angle(angle):

    return (
        (angle + 180.0)
        % 360.0
    ) - 180.0


def circular_error(
    predicted,
    reference
):

    return wrap_angle(
        predicted -
        reference
    )


# ============================================================
# CALIBRATED GYROSCOPE
# ============================================================

yaw_rate = (

    0.029372 * gyro_yaw

    + 0.964380 * gyro_pitch

    + 0.425011 * gyro_roll

    + 0.234927
)


yaw_rate = np.clip(
    yaw_rate,
    -60.0,
    60.0
)


# ============================================================
# GPS VALIDITY
# ============================================================

gps_valid = (

    np.isfinite(gps_heading)

    &

    np.isfinite(gps_speed)

    &

    (gps_speed > 5.0)
)


print(
    f"GPS VALID SAMPLES: "
    f"{gps_valid.sum()}"
)


# ============================================================
# INITIAL GYRO HEADING
# ============================================================

gyro_heading = np.zeros(
    len(df)
)

for i in range(1, len(df)):

    dt = (
        time[i]
        -
        time[i - 1]
    )

    if (
        dt <= 0
        or dt > 1.0
    ):
        dt = 0.02

    gyro_heading[i] = (

        gyro_heading[i - 1]

        +

        yaw_rate[i] * dt
    )


gyro_heading = wrap_angle(
    gyro_heading
)


# ============================================================
# INITIAL FRAME
# ============================================================

SIGN = -1.0

OFFSET = 156.161716

gyro_heading = wrap_angle(

    SIGN * gyro_heading
    +
    OFFSET
)


# ============================================================
# TEST MULTIPLE GPS GAINS
# ============================================================

print(
    "\nGPS GAIN SEARCH"
)

print(
    "==============="
)


gain_results = []


for gain in [

    0.01,
    0.02,
    0.05,
    0.08,
    0.10,
    0.15,
    0.20,
    0.30,
    0.50,
    0.80,
    1.00

]:

    fused = np.zeros(
        len(df)
    )

    fused[0] = gyro_heading[0]

    for i in range(1, len(df)):

        dt = (
            time[i]
            -
            time[i - 1]
        )

        if (
            dt <= 0
            or dt > 1.0
        ):
            dt = 0.02

        predicted = wrap_angle(

            fused[i - 1]

            +

            yaw_rate[i] * dt
        )

        if gps_valid[i]:

            error = circular_error(

                gps_heading[i],
                predicted
            )

            predicted = wrap_angle(

                predicted
                +
                gain * error
            )

        fused[i] = predicted


    error = np.abs(
        circular_error(
            fused[gps_valid],
            gps_heading[gps_valid]
        )
    )

    gain_results.append({

        "GPS_GAIN": gain,

        "MAE_DEG":
            error.mean(),

        "MEDIAN_DEG":
            np.median(error),

        "RMSE_DEG":
            np.sqrt(
                np.mean(
                    error ** 2
                )
            ),

        "MAX_DEG":
            error.max(),

        "PCT_GT_10":
            100 * np.mean(
                error > 10
            ),

        "PCT_GT_20":
            100 * np.mean(
                error > 20
            ),

        "PCT_GT_45":
            100 * np.mean(
                error > 45
            ),

        "PCT_GT_90":
            100 * np.mean(
                error > 90
            )

    })


gain_df = pd.DataFrame(
    gain_results
)

gain_df = gain_df.sort_values(
    "MAE_DEG"
)


print(
    gain_df.to_string(
        index=False,
        float_format=lambda x:
        f"{x:.6f}"
    )
)


# ============================================================
# BEST GAIN
# ============================================================

best_gain = float(
    gain_df.iloc[0]["GPS_GAIN"]
)

print(
    "\nBEST GPS GAIN"
)

print(
    f"{best_gain:.3f}"
)


# ============================================================
# RUN BEST FUSION
# ============================================================

fused_heading = np.zeros(
    len(df)
)

fused_heading[0] = gyro_heading[0]


for i in range(1, len(df)):

    dt = (
        time[i]
        -
        time[i - 1]
    )

    if (
        dt <= 0
        or dt > 1.0
    ):
        dt = 0.02

    predicted = wrap_angle(

        fused_heading[i - 1]

        +

        yaw_rate[i] * dt
    )

    if gps_valid[i]:

        error = circular_error(

            gps_heading[i],
            predicted
        )

        predicted = wrap_angle(

            predicted
            +
            best_gain * error
        )

    fused_heading[i] = predicted


# ============================================================
# ERROR
# ============================================================

heading_error = np.abs(

    circular_error(
        fused_heading,
        gps_heading
    )
)


valid_error = heading_error[
    gps_valid
]


print(
    "\nBEST FUSED HEADING PERFORMANCE"
)

print(
    "=============================="
)

print(
    f"MAE    : "
    f"{valid_error.mean():.6f}°"
)

print(
    f"Median : "
    f"{np.median(valid_error):.6f}°"
)

print(
    f"RMSE   : "
    f"{np.sqrt(np.mean(valid_error ** 2)):.6f}°"
)

print(
    f"Maximum: "
    f"{valid_error.max():.6f}°"
)


# ============================================================
# ERROR THRESHOLDS
# ============================================================

print(
    "\nHEADING ERROR THRESHOLDS"
)

print(
    "========================"
)

for threshold in [
    5,
    10,
    20,
    30,
    45,
    60,
    90
]:

    percentage = (

        100 *
        np.mean(
            valid_error > threshold
        )

    )

    print(
        f"> {threshold:2d}° : "
        f"{percentage:.2f}%"
    )


# ============================================================
# WORST SAMPLES
# ============================================================

valid_indices = np.where(
    gps_valid
)[0]

worst_order = valid_indices[
    np.argsort(
        heading_error[
            valid_indices
        ]
    )[::-1]
][:50]


worst = pd.DataFrame({

    "TIME_S":
        time[worst_order],

    "GPS_SPEED_KMH":
        gps_speed[worst_order],

    "GPS_HEADING_DEG":
        gps_heading[worst_order],

    "GYRO_YAW_DEG_S":
        gyro_yaw[worst_order],

    "GYRO_PITCH_DEG_S":
        gyro_pitch[worst_order],

    "GYRO_ROLL_DEG_S":
        gyro_roll[worst_order],

    "YAW_RATE_DEG_S":
        yaw_rate[worst_order],

    "GYRO_HEADING_DEG":
        gyro_heading[worst_order],

    "FUSED_HEADING_DEG":
        fused_heading[worst_order],

    "HEADING_ERROR_DEG":
        heading_error[worst_order]

})


print(
    "\nWORST 50 FUSED HEADING ERRORS"
)

print(
    "============================="
)

print(
    worst.to_string(
        index=False,
        float_format=lambda x:
        f"{x:.6f}"
    )
)


# ============================================================
# ERROR BY SPEED
# ============================================================

print(
    "\nERROR BY GPS SPEED"
)

print(
    "=================="
)


speed_bins = [
    0,
    5,
    10,
    15,
    20,
    30,
    1000
]

speed_labels = [
    "0-5",
    "5-10",
    "10-15",
    "15-20",
    "20-30",
    "30+"
]


speed_range = pd.cut(

    gps_speed,

    bins=speed_bins,

    labels=speed_labels,

    include_lowest=True
)


speed_table = pd.DataFrame({

    "SPEED_RANGE":
        speed_range[gps_valid],

    "ERROR":
        valid_error

})


speed_summary = (
    speed_table
    .groupby(
        "SPEED_RANGE",
        observed=True
    )
    ["ERROR"]
    .agg([
        "count",
        "mean",
        "median",
        "max"
    ])
)


print(
    speed_summary.to_string(
        float_format=lambda x:
        f"{x:.6f}"
    )
)


# ============================================================
# SAVE SAMPLE RESULTS
# ============================================================

output = pd.DataFrame({

    "TIME_S":
        time,

    "GPS_SPEED_KMH":
        gps_speed,

    "GPS_HEADING_DEG":
        gps_heading,

    "GYRO_YAW_DEG_S":
        gyro_yaw,

    "GYRO_PITCH_DEG_S":
        gyro_pitch,

    "GYRO_ROLL_DEG_S":
        gyro_roll,

    "CALIBRATED_YAW_RATE_DEG_S":
        yaw_rate,

    "GYRO_HEADING_DEG":
        gyro_heading,

    "FUSED_HEADING_DEG":
        fused_heading,

    "HEADING_ERROR_DEG":
        heading_error,

    "GPS_VALID":
        gps_valid

})


os.makedirs(
    "data/processed",
    exist_ok=True
)


sample_path = (
    "data/processed/"
    "fused_heading_outlier_analysis.csv"
)


output.to_csv(
    sample_path,
    index=False
)


# ============================================================
# SAVE GAIN SEARCH
# ============================================================

gain_path = (
    "data/processed/"
    "fused_heading_gain_search.csv"
)


gain_df.to_csv(
    gain_path,
    index=False
)


# ============================================================
# SAVE WORST SAMPLES
# ============================================================

worst_path = (
    "data/processed/"
    "fused_heading_worst_50.csv"
)


worst.to_csv(
    worst_path,
    index=False
)


# ============================================================
# SAVE SPEED ANALYSIS
# ============================================================

speed_path = (
    "data/processed/"
    "fused_heading_speed_analysis.csv"
)


speed_summary.to_csv(
    speed_path
)


print(
    "\nFILES SAVED:"
)

print(sample_path)
print(gain_path)
print(worst_path)
print(speed_path)

print(
    "\nFUSED HEADING OUTLIER ANALYSIS COMPLETE."
)