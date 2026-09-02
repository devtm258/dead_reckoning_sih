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


# ============================================================
# SETTINGS
# ============================================================

WINDOW_DURATION_S = 60.0

STEP_S = 30.0

TOP_WINDOWS = 20


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(df, candidates):

    for name in candidates:

        if name in df.columns:
            return name

    lookup = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for name in candidates:

        key = (
            str(name)
            .strip()
            .lower()
        )

        if key in lookup:
            return lookup[key]

    def normalize(x):

        return (
            str(x)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
            .replace("Â", "")
            .replace("°", "")
        )

    normalized = {
        normalize(c): c
        for c in df.columns
    }

    for name in candidates:

        key = normalize(name)

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# LAT/LON -> LOCAL METRES
# ============================================================

def latlon_to_local(
    lat,
    lon,
    lat0,
    lon0
):

    earth_radius = 6371000.0

    lat0_rad = np.radians(
        lat0
    )

    east = (
        np.radians(
            lon - lon0
        )
        *
        earth_radius
        *
        np.cos(lat0_rad)
    )

    north = (
        np.radians(
            lat - lat0
        )
        *
        earth_radius
    )

    return east, north


# ============================================================
# HEADING DIFFERENCE
# ============================================================

def wrap_angle(angle):

    return (
        angle + 180.0
    ) % 360.0 - 180.0


# ============================================================
# FIND NEAREST INDEX
# ============================================================

def nearest_index(
    time,
    target
):

    return int(
        np.argmin(
            np.abs(
                time - target
            )
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\nDEAD RECKONING ERROR DIAGNOSTIC"
    )

    print(
        "==============================="
    )

    # ========================================================
    # CHECK FILE
    # ========================================================

    if not os.path.exists(
        DR_FILE
    ):

        raise FileNotFoundError(
            f"\nMissing:\n{DR_FILE}"
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
        "DR_NORTH_M",

        "DR_SPEED_MS",
        "DR_YAW_DEG"
    ]

    missing = [

        c
        for c in required_dr
        if c not in dr.columns
    ]

    if missing:

        raise ValueError(
            "Missing DR columns: "
            +
            ", ".join(missing)
        )

    # ========================================================
    # LOAD SMARTPHONE / GNSS DATA
    # ========================================================

    smartphone = (
        load_smartphone_data()
    )

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

    gps_speed_col = find_column(

        smartphone,

        [
            "GPS SPEED (Kmh)",
            "GPS SPEED (kmh)",
            "GPS SPEED"
        ]
    )

    gps_heading_col = find_column(

        smartphone,

        [
            "GPS ORIENTATION (Â°)",
            "GPS ORIENTATION (°)"
        ]
    )

    required = {

        "TIME":
            time_col,

        "LATITUDE":
            lat_col,

        "LONGITUDE":
            lon_col,

        "GPS SPEED":
            gps_speed_col,

        "GPS HEADING":
            gps_heading_col
    }

    missing = [

        name
        for name, column
        in required.items()
        if column is None
    ]

    if missing:

        print(
            "\nAVAILABLE COLUMNS:"
        )

        for column in smartphone.columns:

            print(
                column
            )

        raise ValueError(
            "Missing columns: "
            +
            ", ".join(missing)
        )

    # ========================================================
    # BUILD GNSS DATAFRAME
    # ========================================================

    gps = smartphone[
        [
            time_col,
            lat_col,
            lon_col,
            gps_speed_col,
            gps_heading_col
        ]
    ].copy()

    gps.columns = [

        "TIME_S",
        "LAT",
        "LON",
        "GPS_SPEED_KMH",
        "GPS_HEADING_DEG"
    ]

    for column in gps.columns:

        gps[column] = pd.to_numeric(
            gps[column],
            errors="coerce"
        )

    gps = (

        gps

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

    # ========================================================
    # DR DATA
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
                "DR_NORTH_M",
                "DR_SPEED_MS",
                "DR_YAW_DEG"
            ]
        )

        .sort_values(
            "TIME_S"
        )

        .reset_index(
            drop=True
        )
    )

    # ========================================================
    # ARRAYS
    # ========================================================

    dr_time = dr[
        "TIME_S"
    ].to_numpy(float)

    dr_east = dr[
        "DR_EAST_M"
    ].to_numpy(float)

    dr_north = dr[
        "DR_NORTH_M"
    ].to_numpy(float)

    dr_speed = dr[
        "DR_SPEED_MS"
    ].to_numpy(float)

    dr_yaw = dr[
        "DR_YAW_DEG"
    ].to_numpy(float)

    gps_time = (
        gps[
            "TIME_S"
        ]
        .to_numpy(float)
        /
        1000.0
    )

    gps_lat = gps[
        "LAT"
    ].to_numpy(float)

    gps_lon = gps[
        "LON"
    ].to_numpy(float)

    gps_speed = gps[
        "GPS_SPEED_KMH"
    ].to_numpy(float)

    gps_heading = gps[
        "GPS_HEADING_DEG"
    ].to_numpy(float)

    # ========================================================
    # GNSS LOCAL POSITION
    # ========================================================

    gps_east, gps_north = (
        latlon_to_local(

            gps_lat,
            gps_lon,

            gps_lat[0],
            gps_lon[0]
        )
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

    valid = (

        (dr_time >= start_time)
        &
        (dr_time <= end_time)
    )

    dr_time = dr_time[valid]
    dr_east = dr_east[valid]
    dr_north = dr_north[valid]
    dr_speed = dr_speed[valid]
    dr_yaw = dr_yaw[valid]

    # ========================================================
    # INTERPOLATE GNSS
    # ========================================================

    gps_east_i = np.interp(

        dr_time,
        gps_time,
        gps_east
    )

    gps_north_i = np.interp(

        dr_time,
        gps_time,
        gps_north
    )

    gps_speed_i = np.interp(

        dr_time,
        gps_time,
        gps_speed
    )

    # Heading interpolation is dangerous around 0/360,
    # so interpolate using unit vectors.

    heading_rad = np.radians(
        gps_heading
    )

    heading_x = np.cos(
        heading_rad
    )

    heading_y = np.sin(
        heading_rad
    )

    heading_x_i = np.interp(

        dr_time,
        gps_time,
        heading_x
    )

    heading_y_i = np.interp(

        dr_time,
        gps_time,
        heading_y
    )

    gps_heading_i = np.degrees(

        np.arctan2(
            heading_y_i,
            heading_x_i
        )
    )

    gps_heading_i = (
        gps_heading_i
        %
        360.0
    )

    # ========================================================
    # BUILD WINDOWS
    # ========================================================

    rows = []

    window_start = dr_time[0]

    while (

        window_start
        +
        WINDOW_DURATION_S
        <=
        dr_time[-1]
    ):

        window_end = (
            window_start
            +
            WINDOW_DURATION_S
        )

        i0 = nearest_index(
            dr_time,
            window_start
        )

        i1 = nearest_index(
            dr_time,
            window_end
        )

        duration = (
            dr_time[i1]
            -
            dr_time[i0]
        )

        if duration < 55.0:

            window_start += STEP_S

            continue

        # ====================================================
        # DR DISPLACEMENT
        # ====================================================

        dr_dx = (
            dr_east[i1]
            -
            dr_east[i0]
        )

        dr_dy = (
            dr_north[i1]
            -
            dr_north[i0]
        )

        dr_displacement = np.hypot(
            dr_dx,
            dr_dy
        )

        # ====================================================
        # GNSS DISPLACEMENT
        # ====================================================

        gps_dx = (
            gps_east_i[i1]
            -
            gps_east_i[i0]
        )

        gps_dy = (
            gps_north_i[i1]
            -
            gps_north_i[i0]
        )

        gps_displacement = np.hypot(
            gps_dx,
            gps_dy
        )

        # ====================================================
        # GNSS PATH DISTANCE
        # ====================================================

        gps_path = np.sum(

            np.hypot(

                np.diff(
                    gps_east_i[
                        i0:i1 + 1
                    ]
                ),

                np.diff(
                    gps_north_i[
                        i0:i1 + 1
                    ]
                )
            )
        )

        # ====================================================
        # DR PATH DISTANCE
        # ====================================================

        dr_path = np.sum(

            np.hypot(

                np.diff(
                    dr_east[
                        i0:i1 + 1
                    ]
                ),

                np.diff(
                    dr_north[
                        i0:i1 + 1
                    ]
                )
            )
        )

        # ====================================================
        # ENDPOINT ERROR
        # ====================================================

        endpoint_error = np.hypot(

            dr_dx - gps_dx,

            dr_dy - gps_dy
        )

        # ====================================================
        # SPEED ANALYSIS
        # ====================================================

        dr_mean_speed = np.mean(

            dr_speed[
                i0:i1 + 1
            ]
        )

        gps_mean_speed = np.mean(

            gps_speed_i[
                i0:i1 + 1
            ]
            /
            3.6
        )

        speed_error = (

            dr_mean_speed
            -
            gps_mean_speed
        )

        speed_error_abs = abs(
            speed_error
        )

        # ====================================================
        # HEADING ANALYSIS
        # ====================================================

        dr_heading_start = dr_yaw[i0]

        dr_heading_end = dr_yaw[i1]

        gps_heading_start = (
            gps_heading_i[i0]
        )

        gps_heading_end = (
            gps_heading_i[i1]
        )

        heading_error_start = abs(

            wrap_angle(

                dr_heading_start
                -
                gps_heading_start
            )
        )

        heading_error_end = abs(

            wrap_angle(

                dr_heading_end
                -
                gps_heading_end
            )
        )

        heading_change_dr = abs(

            wrap_angle(

                dr_heading_end
                -
                dr_heading_start
            )
        )

        heading_change_gps = abs(

            wrap_angle(

                gps_heading_end
                -
                gps_heading_start
            )
        )

        heading_change_difference = abs(

            heading_change_dr
            -
            heading_change_gps
        )

        # ====================================================
        # GNSS MOVEMENT QUALITY
        # ====================================================

        gps_mean_speed_kmh = np.mean(

            gps_speed_i[
                i0:i1 + 1
            ]
        )

        rows.append({

            "START_TIME_S":
                dr_time[i0],

            "END_TIME_S":
                dr_time[i1],

            "DURATION_S":
                duration,

            "GPS_PATH_M":
                gps_path,

            "DR_PATH_M":
                dr_path,

            "GPS_DISPLACEMENT_M":
                gps_displacement,

            "DR_DISPLACEMENT_M":
                dr_displacement,

            "ENDPOINT_ERROR_M":
                endpoint_error,

            "DRIFT_PERCENT":
                (
                    endpoint_error
                    /
                    max(
                        gps_path,
                        1e-9
                    )
                    *
                    100.0
                ),

            "DR_MEAN_SPEED_MS":
                dr_mean_speed,

            "GPS_MEAN_SPEED_MS":
                gps_mean_speed,

            "SPEED_ERROR_MS":
                speed_error,

            "SPEED_ERROR_ABS_MS":
                speed_error_abs,

            "DR_HEADING_START_DEG":
                dr_heading_start,

            "GPS_HEADING_START_DEG":
                gps_heading_start,

            "HEADING_ERROR_START_DEG":
                heading_error_start,

            "DR_HEADING_END_DEG":
                dr_heading_end,

            "GPS_HEADING_END_DEG":
                gps_heading_end,

            "HEADING_ERROR_END_DEG":
                heading_error_end,

            "DR_HEADING_CHANGE_DEG":
                heading_change_dr,

            "GPS_HEADING_CHANGE_DEG":
                heading_change_gps,

            "HEADING_CHANGE_DIFFERENCE_DEG":
                heading_change_difference,

            "GPS_MEAN_SPEED_KMH":
                gps_mean_speed_kmh
        })

        window_start += STEP_S

    result = pd.DataFrame(
        rows
    )

    # ========================================================
    # REPORT
    # ========================================================

    print(
        f"\nWINDOWS ANALYSED: "
        f"{len(result)}"
    )

    print(
        "\nWORST WINDOWS BY DRIFT"
    )

    print(
        "======================"
    )

    display_columns = [

        "START_TIME_S",
        "END_TIME_S",

        "GPS_PATH_M",
        "DR_PATH_M",

        "GPS_DISPLACEMENT_M",
        "DR_DISPLACEMENT_M",

        "ENDPOINT_ERROR_M",
        "DRIFT_PERCENT",

        "DR_MEAN_SPEED_MS",
        "GPS_MEAN_SPEED_MS",
        "SPEED_ERROR_MS",

        "HEADING_ERROR_START_DEG",
        "HEADING_ERROR_END_DEG",

        "HEADING_CHANGE_DIFFERENCE_DEG"
    ]

    print(

        result

        .sort_values(
            "DRIFT_PERCENT",
            ascending=False
        )

        .head(
            TOP_WINDOWS
        )

        [display_columns]

        .to_string(
            index=False
        )
    )

    # ========================================================
    # WORST SPEED WINDOWS
    # ========================================================

    print(
        "\nWORST WINDOWS BY SPEED ERROR"
    )

    print(
        "============================="
    )

    print(

        result

        .sort_values(
            "SPEED_ERROR_ABS_MS",
            ascending=False
        )

        .head(
            TOP_WINDOWS
        )

        [
            [
                "START_TIME_S",
                "END_TIME_S",
                "GPS_PATH_M",
                "DR_MEAN_SPEED_MS",
                "GPS_MEAN_SPEED_MS",
                "SPEED_ERROR_MS",
                "DRIFT_PERCENT"
            ]
        ]

        .to_string(
            index=False
        )
    )

    # ========================================================
    # WORST HEADING WINDOWS
    # ========================================================

    print(
        "\nWORST WINDOWS BY HEADING ERROR"
    )

    print(
        "==============================="
    )

    result["MAX_HEADING_ERROR_DEG"] = result[
        [
            "HEADING_ERROR_START_DEG",
            "HEADING_ERROR_END_DEG"
        ]
    ].max(
        axis=1
    )

    print(

        result

        .sort_values(
            "MAX_HEADING_ERROR_DEG",
            ascending=False
        )

        .head(
            TOP_WINDOWS
        )

        [
            [
                "START_TIME_S",
                "END_TIME_S",
                "MAX_HEADING_ERROR_DEG",
                "HEADING_CHANGE_DIFFERENCE_DEG",
                "SPEED_ERROR_MS",
                "DRIFT_PERCENT"
            ]
        ]

        .to_string(
            index=False
        )
    )

    # ========================================================
    # SAVE
    # ========================================================

    output = (
        "data/processed/"
        "dr_error_diagnostic.csv"
    )

    result.to_csv(
        output,
        index=False
    )

    print(
        "\nFILE SAVED:"
    )

    print(
        output
    )

    print(
        "\nDR ERROR DIAGNOSTIC COMPLETE."
    )


if __name__ == "__main__":

    main()