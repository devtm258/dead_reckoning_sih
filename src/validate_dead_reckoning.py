import os
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# FILES
# ============================================================

DR_FILE = (
    "data/processed/"
    "dead_reckoning_no_gnss.csv"
)

VALIDATION_FILE = (
    "data/processed/"
    "dead_reckoning_validation.csv"
)

SUMMARY_FILE = (
    "data/processed/"
    "dead_reckoning_validation_summary.csv"
)

BLACKOUT_FILE = (
    "data/processed/"
    "dead_reckoning_blackout_windows.csv"
)


# ============================================================
# CONSTANTS
# ============================================================

EARTH_RADIUS_M = 6371000.0

BLACKOUT_DURATION_S = 60.0

BLACKOUT_STEP_S = 30.0

TARGET_DRIFT_PERCENT = 10.0


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(df, candidates):

    # Exact match
    for candidate in candidates:

        if candidate in df.columns:
            return candidate

    # Case-insensitive match
    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = (
            str(candidate)
            .strip()
            .lower()
        )

        if key in lookup:
            return lookup[key]

    # Normalized match
    def normalize(value):

        return (
            str(value)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
            .replace("Â", "")
            .replace("°", "")
        )

    normalized = {
        normalize(column): column
        for column in df.columns
    }

    for candidate in candidates:

        key = normalize(candidate)

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2.0) ** 2
        +
        np.cos(lat1)
        *
        np.cos(lat2)
        *
        np.sin(dlon / 2.0) ** 2
    )

    a = np.clip(
        a,
        0.0,
        1.0
    )

    c = (
        2.0
        *
        np.arctan2(
            np.sqrt(a),
            np.sqrt(1.0 - a)
        )
    )

    return EARTH_RADIUS_M * c


# ============================================================
# LAT/LON TO LOCAL EAST/NORTH
# ============================================================

def latlon_to_local(
    lat,
    lon,
    lat0,
    lon0
):

    lat0_rad = np.radians(lat0)

    east = (
        np.radians(
            lon - lon0
        )
        *
        EARTH_RADIUS_M
        *
        np.cos(lat0_rad)
    )

    north = (
        np.radians(
            lat - lat0
        )
        *
        EARTH_RADIUS_M
    )

    return east, north


# ============================================================
# ROTATE 2D POINTS
# ============================================================

def rotate_xy(
    x,
    y,
    angle_rad
):

    c = np.cos(angle_rad)
    s = np.sin(angle_rad)

    x_rot = (
        c * x
        -
        s * y
    )

    y_rot = (
        s * x
        +
        c * y
    )

    return x_rot, y_rot


# ============================================================
# ALIGN INITIAL HEADING
# ============================================================

def calculate_alignment(
    dr_x,
    dr_y,
    gps_x,
    gps_y
):

    n = len(dr_x)

    if n < 10:
        return 0.0

    initial_samples = min(
        n - 1,
        100
    )

    dr_dx = (
        dr_x[initial_samples]
        -
        dr_x[0]
    )

    dr_dy = (
        dr_y[initial_samples]
        -
        dr_y[0]
    )

    gps_dx = (
        gps_x[initial_samples]
        -
        gps_x[0]
    )

    gps_dy = (
        gps_y[initial_samples]
        -
        gps_y[0]
    )

    dr_distance = np.hypot(
        dr_dx,
        dr_dy
    )

    gps_distance = np.hypot(
        gps_dx,
        gps_dy
    )

    if (
        dr_distance < 0.5
        or
        gps_distance < 0.5
    ):

        return 0.0

    dr_angle = np.arctan2(
        dr_dy,
        dr_dx
    )

    gps_angle = np.arctan2(
        gps_dy,
        gps_dx
    )

    return gps_angle - dr_angle


# ============================================================
# INTERPOLATE
# ============================================================

def interpolate_gnss(
    target_time,
    source_time,
    source_values
):

    return np.interp(
        target_time,
        source_time,
        source_values
    )


# ============================================================
# FIND INDEX AT TIME
# ============================================================

def nearest_index(
    time_array,
    target_time
):

    return int(
        np.argmin(
            np.abs(
                time_array
                -
                target_time
            )
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\nDEAD RECKONING VALIDATION"
    )

    print(
        "========================="
    )

    # ========================================================
    # CHECK DR FILE
    # ========================================================

    if not os.path.exists(
        DR_FILE
    ):

        raise FileNotFoundError(

            "\nDead-reckoning output not found:\n"
            f"{DR_FILE}\n\n"

            "Run first:\n"

            "D:\\Anaconda\\envs\\smartphone_nav\\python.exe "
            "src\\dead_reckoning_no_gnss.py"
        )

    # ========================================================
    # LOAD DR
    # ========================================================

    dr = pd.read_csv(
        DR_FILE
    )

    required_dr = [
        "TIME_S",
        "DR_EAST_M",
        "DR_NORTH_M"
    ]

    missing_dr = [
        column
        for column in required_dr
        if column not in dr.columns
    ]

    if missing_dr:

        raise ValueError(
            "Dead-reckoning output is missing columns: "
            +
            ", ".join(missing_dr)
        )

    # ========================================================
    # LOAD SMARTPHONE DATA
    # ========================================================

    smartphone = (
        load_smartphone_data()
    )

    # ========================================================
    # FIND GNSS COLUMNS
    # ========================================================

    time_col = find_column(
        smartphone,
        [
            "TIME SINCE START (ms)"
        ]
    )

    lat_col = find_column(
        smartphone,
        [
            "GPS LATITUDE (degrees)",
            "GPS Latitude (degrees)",
            "GPS LATITUDE",
            "GPS LAT"
        ]
    )

    lon_col = find_column(
        smartphone,
        [
            "GPS LONGITUDE (degrees)",
            "GPS Longitude (degrees)",
            "GPS LONGITUDE",
            "GPS LON"
        ]
    )

    missing_gnss = []

    if time_col is None:
        missing_gnss.append(
            "TIME SINCE START (ms)"
        )

    if lat_col is None:
        missing_gnss.append(
            "GPS LATITUDE"
        )

    if lon_col is None:
        missing_gnss.append(
            "GPS LONGITUDE"
        )

    if missing_gnss:

        raise ValueError(
            "Missing GNSS validation columns: "
            +
            ", ".join(missing_gnss)
        )

    # ========================================================
    # EXTRACT GNSS
    # ========================================================

    gnss = smartphone[
        [
            time_col,
            lat_col,
            lon_col
        ]
    ].copy()

    gnss.columns = [
        "TIME_S",
        "LAT",
        "LON"
    ]

    for column in gnss.columns:

        gnss[column] = pd.to_numeric(
            gnss[column],
            errors="coerce"
        )

    gnss = (

        gnss

        .replace(
            [
                np.inf,
                -np.inf
            ],
            np.nan
        )

        .dropna()

        .sort_values(
            "TIME_S"
        )

        .drop_duplicates(
            subset=[
                "TIME_S"
            ]
        )

        .reset_index(
            drop=True
        )
    )

    if len(gnss) < 2:

        raise RuntimeError(
            "Not enough valid GNSS samples."
        )

    # ========================================================
    # CLEAN DR
    # ========================================================

    dr = (

        dr

        .replace(
            [
                np.inf,
                -np.inf
            ],
            np.nan
        )

        .dropna(
            subset=[
                "TIME_S",
                "DR_EAST_M",
                "DR_NORTH_M"
            ]
        )

        .sort_values(
            "TIME_S"
        )

        .drop_duplicates(
            subset=[
                "TIME_S"
            ]
        )

        .reset_index(
            drop=True
        )
    )

    # ========================================================
    # ARRAYS
    # ========================================================

    dr_time = (
        dr[
            "TIME_S"
        ]
        .to_numpy(float)
    )

    dr_east = (
        dr[
            "DR_EAST_M"
        ]
        .to_numpy(float)
    )

    dr_north = (
        dr[
            "DR_NORTH_M"
        ]
        .to_numpy(float)
    )

    gps_time = (
        gnss[
            "TIME_S"
        ]
        .to_numpy(float)
        /
        1000.0
    )

    gps_lat = (
        gnss[
            "LAT"
        ]
        .to_numpy(float)
    )

    gps_lon = (
        gnss[
            "LON"
        ]
        .to_numpy(float)
    )

    # ========================================================
    # COMMON TIME RANGE
    # ========================================================

    start_time = max(
        dr_time[0],
        gps_time[0]
    )

    end_time = min(
        dr_time[-1],
        gps_time[-1]
    )

    common = (
        (dr_time >= start_time)
        &
        (dr_time <= end_time)
    )

    if common.sum() < 10:

        raise RuntimeError(
            "Insufficient overlapping DR/GNSS time."
        )

    dr_time = dr_time[
        common
    ]

    dr_east = dr_east[
        common
    ]

    dr_north = dr_north[
        common
    ]

    # ========================================================
    # GNSS LOCAL COORDINATES
    # ========================================================

    gps_east_raw, gps_north_raw = (
        latlon_to_local(

            gps_lat,

            gps_lon,

            gps_lat[0],

            gps_lon[0]
        )
    )

    # ========================================================
    # INTERPOLATE GNSS TO DR TIME
    # ========================================================

    gps_east = interpolate_gnss(
        dr_time,
        gps_time,
        gps_east_raw
    )

    gps_north = interpolate_gnss(
        dr_time,
        gps_time,
        gps_north_raw
    )

    # ========================================================
    # ORIGIN NORMALIZATION
    # ========================================================

    dr_east = (
        dr_east
        -
        dr_east[0]
    )

    dr_north = (
        dr_north
        -
        dr_north[0]
    )

    gps_east = (
        gps_east
        -
        gps_east[0]
    )

    gps_north = (
        gps_north
        -
        gps_north[0]
    )

    # ========================================================
    # VALIDATION-ONLY INITIAL ROTATION
    # ========================================================

    alignment_angle = calculate_alignment(

        dr_east,
        dr_north,

        gps_east,
        gps_north
    )

    aligned_east, aligned_north = rotate_xy(

        dr_east,
        dr_north,

        alignment_angle
    )

    # ========================================================
    # POSITION ERROR
    # ========================================================

    position_error = np.sqrt(

        (
            aligned_east
            -
            gps_east
        ) ** 2

        +

        (
            aligned_north
            -
            gps_north
        ) ** 2
    )

    # ========================================================
    # CUMULATIVE DISTANCE
    # ========================================================

    gps_step_distance = np.sqrt(

        np.diff(
            gps_east
        ) ** 2

        +

        np.diff(
            gps_north
        ) ** 2
    )

    dr_step_distance = np.sqrt(

        np.diff(
            aligned_east
        ) ** 2

        +

        np.diff(
            aligned_north
        ) ** 2
    )

    gps_distance_cumulative = np.concatenate([

        [0.0],

        np.cumsum(
            gps_step_distance
        )
    ])

    dr_distance_cumulative = np.concatenate([

        [0.0],

        np.cumsum(
            dr_step_distance
        )
    ])

    total_gps_distance = (
        gps_distance_cumulative[-1]
    )

    total_dr_distance = (
        dr_distance_cumulative[-1]
    )

    # ========================================================
    # ERROR METRICS
    # ========================================================

    mean_error = np.mean(
        position_error
    )

    median_error = np.median(
        position_error
    )

    p90_error = np.percentile(
        position_error,
        90
    )

    p95_error = np.percentile(
        position_error,
        95
    )

    p99_error = np.percentile(
        position_error,
        99
    )

    max_error = np.max(
        position_error
    )

    final_error = position_error[-1]

    # ========================================================
    # DRIFT
    # ========================================================

    mean_drift_percent = (

        mean_error
        /
        max(
            total_gps_distance,
            1e-9
        )
        *
        100.0
    )

    final_drift_percent = (

        final_error
        /
        max(
            total_gps_distance,
            1e-9
        )
        *
        100.0
    )

    max_drift_percent = (

        max_error
        /
        max(
            total_gps_distance,
            1e-9
        )
        *
        100.0
    )

    meets_10_percent = (
        final_drift_percent
        <
        TARGET_DRIFT_PERCENT
    )

    # ========================================================
    # 60-SECOND BLACKOUT TEST
    #
    # IMPORTANT:
    #
    # Each window is independently anchored at its own
    # starting position.
    #
    # We measure:
    #
    #   DR displacement over 60 s
    #   GNSS displacement over 60 s
    #
    # and compare the ENDPOINT displacement error against
    # the GNSS distance travelled during that same window.
    #
    # This is a true local blackout-drift measurement.
    # ========================================================

    print(
        "\nBUILDING 60-SECOND BLACKOUT WINDOWS..."
    )

    blackout_rows = []

    window_start = dr_time[0]

    while (

        window_start
        +
        BLACKOUT_DURATION_S
        <=
        dr_time[-1]
    ):

        window_end = (
            window_start
            +
            BLACKOUT_DURATION_S
        )

        start_idx = nearest_index(
            dr_time,
            window_start
        )

        end_idx = nearest_index(
            dr_time,
            window_end
        )

        actual_start = dr_time[start_idx]
        actual_end = dr_time[end_idx]

        actual_duration = (
            actual_end
            -
            actual_start
        )

        if actual_duration < 55.0:

            window_start += BLACKOUT_STEP_S

            continue

        # ----------------------------------------------------
        # DR displacement
        # ----------------------------------------------------

        dr_dx = (
            aligned_east[end_idx]
            -
            aligned_east[start_idx]
        )

        dr_dy = (
            aligned_north[end_idx]
            -
            aligned_north[start_idx]
        )

        dr_displacement = np.hypot(
            dr_dx,
            dr_dy
        )

        # ----------------------------------------------------
        # GNSS displacement
        # ----------------------------------------------------

        gps_dx = (
            gps_east[end_idx]
            -
            gps_east[start_idx]
        )

        gps_dy = (
            gps_north[end_idx]
            -
            gps_north[start_idx]
        )

        gps_displacement = np.hypot(
            gps_dx,
            gps_dy
        )

        # ----------------------------------------------------
        # GNSS path distance inside the window
        # ----------------------------------------------------

        gps_path_distance = np.sum(

            np.sqrt(

                np.diff(
                    gps_east[
                        start_idx:end_idx + 1
                    ]
                ) ** 2

                +

                np.diff(
                    gps_north[
                        start_idx:end_idx + 1
                    ]
                ) ** 2
            )
        )

        # ----------------------------------------------------
        # DR path distance
        # ----------------------------------------------------

        dr_path_distance = np.sum(

            np.sqrt(

                np.diff(
                    aligned_east[
                        start_idx:end_idx + 1
                    ]
                ) ** 2

                +

                np.diff(
                    aligned_north[
                        start_idx:end_idx + 1
                    ]
                ) ** 2
            )
        )

        # ----------------------------------------------------
        # Endpoint error
        # ----------------------------------------------------

        endpoint_error = np.hypot(

            (
                aligned_east[end_idx]
                -
                aligned_east[start_idx]
            )
            -
            (
                gps_east[end_idx]
                -
                gps_east[start_idx]
            ),

            (
                aligned_north[end_idx]
                -
                aligned_north[start_idx]
            )
            -
            (
                gps_north[end_idx]
                -
                gps_north[start_idx]
            )
        )

        # ----------------------------------------------------
        # Drift relative to actual GNSS distance
        # ----------------------------------------------------

        drift_percent = (

            endpoint_error
            /
            max(
                gps_path_distance,
                1e-9
            )
            *
            100.0
        )

        blackout_rows.append({

            "START_TIME_S":
                actual_start,

            "END_TIME_S":
                actual_end,

            "DURATION_S":
                actual_duration,

            "GPS_PATH_DISTANCE_M":
                gps_path_distance,

            "DR_PATH_DISTANCE_M":
                dr_path_distance,

            "GPS_DISPLACEMENT_M":
                gps_displacement,

            "DR_DISPLACEMENT_M":
                dr_displacement,

            "ENDPOINT_ERROR_M":
                endpoint_error,

            "DRIFT_PERCENT":
                drift_percent,

            "PASS_UNDER_10_PERCENT":
                drift_percent
                <
                TARGET_DRIFT_PERCENT
        })

        window_start += BLACKOUT_STEP_S

    blackout_df = pd.DataFrame(
        blackout_rows
    )

    # ========================================================
    # BLACKOUT STATISTICS
    # ========================================================

    if len(blackout_df):

        blackout_pass_count = int(

            blackout_df[
                "PASS_UNDER_10_PERCENT"
            ]
            .sum()
        )

        blackout_mean = float(

            blackout_df[
                "DRIFT_PERCENT"
            ]
            .mean()
        )

        blackout_median = float(

            blackout_df[
                "DRIFT_PERCENT"
            ]
            .median()
        )

        blackout_p90 = float(

            blackout_df[
                "DRIFT_PERCENT"
            ]
            .quantile(
                0.90
            )
        )

        blackout_worst = float(

            blackout_df[
                "DRIFT_PERCENT"
            ]
            .max()
        )

    else:

        blackout_pass_count = 0

        blackout_mean = np.nan

        blackout_median = np.nan

        blackout_p90 = np.nan

        blackout_worst = np.nan

    # ========================================================
    # SAMPLE VALIDATION FILE
    # ========================================================

    validation = pd.DataFrame({

        "TIME_S":
            dr_time,

        "DR_EAST_M":
            aligned_east,

        "DR_NORTH_M":
            aligned_north,

        "GNSS_EAST_M":
            gps_east,

        "GNSS_NORTH_M":
            gps_north,

        "POSITION_ERROR_M":
            position_error,

        "GNSS_CUMULATIVE_DISTANCE_M":
            gps_distance_cumulative,

        "DR_CUMULATIVE_DISTANCE_M":
            dr_distance_cumulative,

        "DRIFT_PERCENT":
            (
                position_error
                /
                np.maximum(
                    gps_distance_cumulative,
                    1e-9
                )
                *
                100.0
            )
    })

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = pd.DataFrame([{

        "DR_SAMPLES":
            len(dr),

        "GNSS_SAMPLES":
            len(gnss),

        "GPS_DISTANCE_M":
            total_gps_distance,

        "DR_DISTANCE_M":
            total_dr_distance,

        "MEAN_POSITION_ERROR_M":
            mean_error,

        "MEDIAN_POSITION_ERROR_M":
            median_error,

        "P90_ERROR_M":
            p90_error,

        "P95_ERROR_M":
            p95_error,

        "P99_ERROR_M":
            p99_error,

        "MAX_POSITION_ERROR_M":
            max_error,

        "FINAL_POSITION_ERROR_M":
            final_error,

        "MEAN_DRIFT_PERCENT":
            mean_drift_percent,

        "FINAL_DRIFT_PERCENT":
            final_drift_percent,

        "MAX_DRIFT_PERCENT":
            max_drift_percent,

        "INITIAL_ALIGNMENT_DEG":
            np.degrees(
                alignment_angle
            ),

        "MEETS_10_PERCENT_TARGET":
            meets_10_percent,

        "BLACKOUT_WINDOWS":
            len(blackout_df),

        "BLACKOUT_WINDOWS_UNDER_10_PERCENT":
            blackout_pass_count,

        "BLACKOUT_MEAN_DRIFT_PERCENT":
            blackout_mean,

        "BLACKOUT_MEDIAN_DRIFT_PERCENT":
            blackout_median,

        "BLACKOUT_P90_DRIFT_PERCENT":
            blackout_p90,

        "BLACKOUT_WORST_DRIFT_PERCENT":
            blackout_worst

    }])

    # ========================================================
    # SAVE
    # ========================================================

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    validation.to_csv(
        VALIDATION_FILE,
        index=False
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    blackout_df.to_csv(
        BLACKOUT_FILE,
        index=False
    )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print(
        "\nVALIDATION RESULTS"
    )

    print(
        "=================="
    )

    print(
        f"DR samples       : "
        f"{len(dr)}"
    )

    print(
        f"GNSS samples     : "
        f"{len(gnss)}"
    )

    print(
        f"GNSS distance    : "
        f"{total_gps_distance:.3f} m"
    )

    print(
        f"DR distance      : "
        f"{total_dr_distance:.3f} m"
    )

    print(
        f"Mean error       : "
        f"{mean_error:.3f} m"
    )

    print(
        f"Median error     : "
        f"{median_error:.3f} m"
    )

    print(
        f"P90 error        : "
        f"{p90_error:.3f} m"
    )

    print(
        f"P95 error        : "
        f"{p95_error:.3f} m"
    )

    print(
        f"P99 error        : "
        f"{p99_error:.3f} m"
    )

    print(
        f"Maximum error    : "
        f"{max_error:.3f} m"
    )

    print(
        f"Final error      : "
        f"{final_error:.3f} m"
    )

    print(
        f"Mean drift       : "
        f"{mean_drift_percent:.3f}%"
    )

    print(
        f"Final drift      : "
        f"{final_drift_percent:.3f}%"
    )

    print(
        f"Initial alignment: "
        f"{np.degrees(alignment_angle):.3f}°"
    )

    print(
        "\n10% DRIFT TARGET"
    )

    print(
        "================"
    )

    if meets_10_percent:

        print(
            "PASS"
        )

    else:

        print(
            "FAIL"
        )

    # ========================================================
    # BLACKOUT REPORT
    # ========================================================

    print(
        "\n60-SECOND BLACKOUT TEST"
    )

    print(
        "======================="
    )

    print(
        f"Windows tested : "
        f"{len(blackout_df)}"
    )

    if len(blackout_df):

        print(
            f"Windows <10%   : "
            f"{blackout_pass_count}"
        )

        print(
            f"Mean drift     : "
            f"{blackout_mean:.3f}%"
        )

        print(
            f"Median drift   : "
            f"{blackout_median:.3f}%"
        )

        print(
            f"P90 drift      : "
            f"{blackout_p90:.3f}%"
        )

        print(
            f"Worst drift    : "
            f"{blackout_worst:.3f}%"
        )

    # ========================================================
    # FILES
    # ========================================================

    print(
        "\nFILES SAVED:"
    )

    print(
        VALIDATION_FILE
    )

    print(
        SUMMARY_FILE
    )

    print(
        BLACKOUT_FILE
    )

    print(
        "\nDEAD RECKONING VALIDATION COMPLETE."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()