import os
import pickle
import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# GNSS-FREE DEAD RECKONING ENGINE
# ============================================================
#
# Runtime inputs:
#   Accelerometer
#   Gravity
#   Gyroscope
#   Magnetometer
#
# NEVER USED AT RUNTIME:
#   GPS latitude
#   GPS longitude
#   GPS speed
#   GPS orientation
#   VBOX
#
# The trained velocity model estimates forward vehicle speed.
# Heading is estimated from inertial sensors only.
# ============================================================


# ============================================================
# FILES
# ============================================================

MODEL_FILE = (
    "data/processed/"
    "dr_velocity_model.pkl"
)

OUTPUT_FILE = (
    "data/processed/"
    "dead_reckoning_no_gnss.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

WINDOW = 20

MAX_SPEED_MS = 35.0

MIN_SPEED_MS = 0.0

# Exponential smoothing for model velocity.
SPEED_ALPHA = 0.25

# Gyroscope integration is the primary heading propagation.
# Magnetometer correction is deliberately slow because vehicle
# magnetic disturbances can be significant.

HEADING_CORRECTION_GAIN = 0.03

# Reject obviously unstable magnetometer readings.
MAG_MIN_UT = 10.0
MAG_MAX_UT = 100.0

# Limit single-step heading changes caused by numerical or
# sensor anomalies.

MAX_HEADING_RATE_RAD_S = np.radians(180.0)

# Normal smartphone sampling is expected around 10 Hz.
# This protects the integration from bad timestamps.

MAX_DT_S = 1.0
DEFAULT_DT_S = 0.1


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(df, candidates):

    # Exact match
    for name in candidates:

        if name in df.columns:
            return name

    # Case-insensitive match
    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in candidates:

        key = (
            str(name)
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

    for name in candidates:

        key = normalize(name)

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# EXACT 53-FEATURE FUNCTION
# ============================================================
#
# Must match the current velocity model.
#
# 45 raw sensor statistics
# + 4 linear acceleration magnitude statistics
# + 4 gyroscope magnitude statistics
# = 53
# ============================================================

def make_features(accel, gyro, gravity):

    features = []

    # --------------------------------------------------------
    # Raw sensor statistics
    # 3 arrays x 3 axes x 5 statistics = 45
    # --------------------------------------------------------

    for arr in (
        accel,
        gyro,
        gravity
    ):

        for axis in range(3):

            v = arr[:, axis]

            features.extend([

                np.mean(v),

                np.std(v),

                np.min(v),

                np.max(v),

                np.mean(
                    np.abs(v)
                )

            ])

    # --------------------------------------------------------
    # Linear acceleration
    # --------------------------------------------------------

    linear = (
        accel
        -
        gravity
    )

    linear_mag = np.linalg.norm(
        linear,
        axis=1
    )

    # --------------------------------------------------------
    # Gyroscope magnitude
    # --------------------------------------------------------

    gyro_mag = np.linalg.norm(
        gyro,
        axis=1
    )

    # --------------------------------------------------------
    # Linear acceleration magnitude
    # 5 initially
    # --------------------------------------------------------

    features.extend([

        np.mean(
            linear_mag
        ),

        np.std(
            linear_mag
        ),

        np.min(
            linear_mag
        ),

        np.max(
            linear_mag
        ),

        np.mean(
            np.abs(
                linear_mag
            )
        )

    ])

    # --------------------------------------------------------
    # Gyroscope magnitude
    # 5 initially
    # --------------------------------------------------------

    features.extend([

        np.mean(
            gyro_mag
        ),

        np.std(
            gyro_mag
        ),

        np.min(
            gyro_mag
        ),

        np.max(
            gyro_mag
        ),

        np.mean(
            np.abs(
                gyro_mag
            )
        )

    ])

    # 45 + 5 + 5 = 55
    #
    # Remove two redundant minimum-magnitude features to
    # preserve the exact 53-feature model interface.

    features = [

        value

        for index, value
        in enumerate(features)

        if index not in (
            47,
            52
        )

    ]

    result = np.asarray(
        features,
        dtype=np.float32
    )

    if len(result) != 53:

        raise ValueError(
            f"Feature generation error: "
            f"expected 53, got {len(result)}"
        )

    return result


# ============================================================
# ANGLE WRAPPING
# ============================================================

def wrap_angle_rad(angle):

    return (
        angle + np.pi
    ) % (
        2.0 * np.pi
    ) - np.pi


def wrap_angle_deg(angle):

    return (
        angle + 180.0
    ) % 360.0 - 180.0


# ============================================================
# MAGNETOMETER HEADING
# ============================================================
#
# We use the horizontal magnetometer components.
#
# This is an auxiliary absolute heading reference.
# It is NOT GPS.
#
# Because magnetic interference is possible inside vehicles,
# the magnetometer is only used for slow correction.
# ============================================================

def magnetometer_heading(
    mx,
    my
):

    return np.arctan2(
        my,
        mx
    )


# ============================================================
# ROBUST CIRCULAR MEDIAN
# ============================================================

def circular_mean(angles):

    if len(angles) == 0:
        return 0.0

    s = np.mean(
        np.sin(angles)
    )

    c = np.mean(
        np.cos(angles)
    )

    return np.arctan2(
        s,
        c
    )


# ============================================================
# HEADING ESTIMATION
# ============================================================

def estimate_heading(
    time,
    gyro_yaw,
    gravity,
    magnetic
):

    n = len(time)

    yaw = np.zeros(
        n,
        dtype=float
    )

    # --------------------------------------------------------
    # Initial inertial heading.
    #
    # Absolute zero is arbitrary. The validation stage can
    # perform a one-time frame alignment because the vehicle's
    # local coordinate frame is not known beforehand.
    # --------------------------------------------------------

    mag_heading = np.full(
        n,
        np.nan,
        dtype=float
    )

    # --------------------------------------------------------
    # Prepare magnetometer heading.
    # --------------------------------------------------------

    for i in range(n):

        mx = magnetic[i, 0]
        my = magnetic[i, 1]
        mz = magnetic[i, 2]

        magnitude = np.sqrt(
            mx * mx
            +
            my * my
            +
            mz * mz
        )

        if (

            np.isfinite(magnitude)

            and

            MAG_MIN_UT
            <=
            magnitude
            <=
            MAG_MAX_UT

        ):

            mag_heading[i] = (
                magnetometer_heading(
                    mx,
                    my
                )
            )

    # --------------------------------------------------------
    # Initialize from the first valid magnetometer heading.
    # If unavailable, start at zero.
    # --------------------------------------------------------

    valid_mag = np.where(
        np.isfinite(
            mag_heading
        )
    )[0]

    if len(valid_mag):

        first = valid_mag[0]

        yaw[0] = mag_heading[first]

    else:

        yaw[0] = 0.0

    # --------------------------------------------------------
    # Gyroscope propagation + slow magnetometer correction.
    # --------------------------------------------------------

    for i in range(1, n):

        dt = (
            time[i]
            -
            time[i - 1]
        )

        if (

            not np.isfinite(dt)

            or
            dt <= 0.0

            or
            dt > MAX_DT_S

        ):

            dt = DEFAULT_DT_S

        gyro_rate = gyro_yaw[i]

        if not np.isfinite(gyro_rate):

            gyro_rate = 0.0

        gyro_rate = np.clip(

            gyro_rate,

            -MAX_HEADING_RATE_RAD_S,

            MAX_HEADING_RATE_RAD_S

        )

        # ----------------------------------------------------
        # Inertial propagation
        # ----------------------------------------------------

        predicted_yaw = (

            yaw[i - 1]
            +
            gyro_rate * dt

        )

        predicted_yaw = wrap_angle_rad(
            predicted_yaw
        )

        # ----------------------------------------------------
        # Slow magnetic correction
        # ----------------------------------------------------

        if np.isfinite(
            mag_heading[i]
        ):

            innovation = wrap_angle_rad(

                mag_heading[i]
                -
                predicted_yaw

            )

            predicted_yaw = (

                predicted_yaw

                +

                HEADING_CORRECTION_GAIN
                *
                innovation

            )

        yaw[i] = wrap_angle_rad(
            predicted_yaw
        )

    # --------------------------------------------------------
    # Unwrap for smooth output.
    # --------------------------------------------------------

    yaw = np.unwrap(
        yaw
    )

    return yaw


# ============================================================
# SPEED SMOOTHING
# ============================================================

def smooth_speed(
    speed,
    alpha
):

    result = np.zeros_like(
        speed,
        dtype=float
    )

    if len(speed) == 0:
        return result

    result[0] = speed[0]

    for i in range(
        1,
        len(speed)
    ):

        result[i] = (

            alpha
            *
            speed[i]

            +

            (1.0 - alpha)
            *
            result[i - 1]

        )

    return result


# ============================================================
# REMOVE SHORT IMPOSSIBLE SPEED SPIKES
# ============================================================

def limit_speed_acceleration(
    speed,
    time
):

    result = np.asarray(
        speed,
        dtype=float
    ).copy()

    if len(result) < 2:
        return result

    # Conservative physical rate limit.
    #
    # This is not intended to create a vehicle model. It simply
    # prevents one-frame model spikes from adding unrealistic
    # displacement.

    MAX_ACCEL_MS2 = 6.0

    for i in range(
        1,
        len(result)
    ):

        dt = (
            time[i]
            -
            time[i - 1]
        )

        if (

            not np.isfinite(dt)

            or
            dt <= 0.0

            or
            dt > MAX_DT_S

        ):

            dt = DEFAULT_DT_S

        max_delta = (
            MAX_ACCEL_MS2
            *
            dt
        )

        lower = max(
            MIN_SPEED_MS,
            result[i - 1]
            -
            max_delta
        )

        upper = min(
            MAX_SPEED_MS,
            result[i - 1]
            +
            max_delta
        )

        result[i] = np.clip(
            result[i],
            lower,
            upper
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\nGNSS-FREE DEAD RECKONING ENGINE"
    )

    print(
        "==============================="
    )

    # ========================================================
    # LOAD MODEL
    # ========================================================

    if not os.path.exists(
        MODEL_FILE
    ):

        raise FileNotFoundError(

            "\nVelocity model not found:\n"

            f"{MODEL_FILE}\n\n"

            "Run:\n"

            "D:\\Anaconda\\envs\\smartphone_nav\\python.exe "
            "src\\train_velocity_model.py"

        )

    with open(
        MODEL_FILE,
        "rb"
    ) as f:

        bundle = pickle.load(
            f
        )

    model = bundle[
        "model"
    ]

    model_window = bundle.get(
        "window",
        WINDOW
    )

    feature_count = bundle.get(
        "feature_count",
        None
    )

    print(
        f"\nMODEL WINDOW     : "
        f"{model_window}"
    )

    print(
        f"FEATURE COUNT    : "
        f"{feature_count}"
    )

    if model_window != WINDOW:

        raise ValueError(

            f"Model window is "
            f"{model_window}, "

            f"but runtime expects "
            f"{WINDOW}."

        )

    # ========================================================
    # LOAD SMARTPHONE DATA ONLY
    # ========================================================

    print(
        "\nLoading smartphone data..."
    )

    data = load_smartphone_data()

    # ========================================================
    # FIND SENSOR COLUMNS
    # ========================================================

    time_col = find_column(
        data,
        [
            "TIME SINCE START (ms)"
        ]
    )

    ax_col = find_column(
        data,
        [
            "ACCELEROMETER X (m/s²)"
        ]
    )

    ay_col = find_column(
        data,
        [
            "ACCELEROMETER Y (m/s²)"
        ]
    )

    az_col = find_column(
        data,
        [
            "ACCELEROMETER Z (m/s²)"
        ]
    )

    gyro_yaw_col = find_column(
        data,
        [
            "GYROSCOPE Yaw (rad/s)"
        ]
    )

    gyro_pitch_col = find_column(
        data,
        [
            "GYROSCOPE Pitch (rad/s)"
        ]
    )

    gyro_roll_col = find_column(
        data,
        [
            "GYROSCOPE Roll (rad/s)"
        ]
    )

    gravity_x_col = find_column(
        data,
        [
            "GRAVITY X (m/s²)"
        ]
    )

    gravity_y_col = find_column(
        data,
        [
            "GRAVITY Y (m/s²)"
        ]
    )

    gravity_z_col = find_column(
        data,
        [
            "GRAVITY Z (m/s²)"
        ]
    )

    magnetic_x_col = find_column(
        data,
        [
            "MAGNETIC FIELD X (Î¼T)",
            "MAGNETIC FIELD X (μT)"
        ]
    )

    magnetic_y_col = find_column(
        data,
        [
            "MAGNETIC FIELD Y (Î¼T)",
            "MAGNETIC FIELD Y (μT)"
        ]
    )

    magnetic_z_col = find_column(
        data,
        [
            "MAGNETIC FIELD Z (Î¼T)",
            "MAGNETIC FIELD Z (μT)"
        ]
    )

    # ========================================================
    # IMPORTANT:
    #
    # GPS ORIENTATION IS INTENTIONALLY NOT SEARCHED.
    # ========================================================

    required = {

        "TIME":
            time_col,

        "ACCELEROMETER X":
            ax_col,

        "ACCELEROMETER Y":
            ay_col,

        "ACCELEROMETER Z":
            az_col,

        "GYROSCOPE YAW":
            gyro_yaw_col,

        "GYROSCOPE PITCH":
            gyro_pitch_col,

        "GYROSCOPE ROLL":
            gyro_roll_col,

        "GRAVITY X":
            gravity_x_col,

        "GRAVITY Y":
            gravity_y_col,

        "GRAVITY Z":
            gravity_z_col,

        "MAGNETIC FIELD X":
            magnetic_x_col,

        "MAGNETIC FIELD Y":
            magnetic_y_col,

        "MAGNETIC FIELD Z":
            magnetic_z_col

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

        for column in data.columns:

            print(
                column
            )

        raise ValueError(

            "\nMissing required sensor columns:\n"

            +
            "\n".join(
                missing
            )

        )

    # ========================================================
    # WORKING DATA
    # ========================================================

    work = data[

        [

            time_col,

            ax_col,
            ay_col,
            az_col,

            gyro_yaw_col,
            gyro_pitch_col,
            gyro_roll_col,

            gravity_x_col,
            gravity_y_col,
            gravity_z_col,

            magnetic_x_col,
            magnetic_y_col,
            magnetic_z_col

        ]

    ].copy()

    work.columns = [

        "time",

        "ax",
        "ay",
        "az",

        "gyro_yaw",
        "gyro_pitch",
        "gyro_roll",

        "gravity_x",
        "gravity_y",
        "gravity_z",

        "mag_x",
        "mag_y",
        "mag_z"

    ]

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    for column in work.columns:

        work[column] = pd.to_numeric(

            work[column],

            errors="coerce"

        )

    # ========================================================
    # CLEAN
    # ========================================================

    work = (

        work

        .replace(
            [
                np.inf,
                -np.inf
            ],
            np.nan
        )

        .dropna()

        .reset_index(
            drop=True
        )

    )

    if len(work) < WINDOW:

        raise ValueError(
            "Not enough valid smartphone samples."
        )

    # ========================================================
    # ARRAYS
    # ========================================================

    time = (

        work[
            "time"
        ]
        .to_numpy(float)

        /
        1000.0

    )

    accel = work[

        [
            "ax",
            "ay",
            "az"
        ]

    ].to_numpy(
        float
    )

    gyro = work[

        [
            "gyro_yaw",
            "gyro_pitch",
            "gyro_roll"
        ]

    ].to_numpy(
        float
    )

    gravity = work[

        [
            "gravity_x",
            "gravity_y",
            "gravity_z"
        ]

    ].to_numpy(
        float
    )

    magnetic = work[

        [
            "mag_x",
            "mag_y",
            "mag_z"
        ]

    ].to_numpy(
        float
    )

    n = len(work)

    print(
        f"\nSAMPLES: {n}"
    )

    # ========================================================
    # EXPLICIT GNSS / VBOX SAFETY
    # ========================================================

    print(
        "GNSS INPUTS TO ENGINE: 0"
    )

    print(
        "VBOX INPUTS TO ENGINE: 0"
    )

    print(
        "GPS ORIENTATION INPUT: 0"
    )

    # ========================================================
    # FEATURE COMPATIBILITY
    # ========================================================

    test_features = make_features(

        accel[
            :WINDOW
        ],

        gyro[
            :WINDOW
        ],

        gravity[
            :WINDOW
        ]

    )

    runtime_feature_count = len(
        test_features
    )

    print(
        f"RUNTIME FEATURE COUNT: "
        f"{runtime_feature_count}"
    )

    if feature_count is not None:

        if runtime_feature_count != feature_count:

            raise ValueError(

                "\nFEATURE MISMATCH!\n"

                f"Model expects: "
                f"{feature_count}\n"

                f"Runtime creates: "
                f"{runtime_feature_count}"

            )

    # ========================================================
    # HEADING
    # ========================================================

    print(
        "\nBUILDING GNSS-FREE HEADING..."
    )

    yaw_rad = estimate_heading(

        time,

        gyro[
            :,
            0
        ],

        gravity,

        magnetic

    )

    yaw_deg = np.degrees(
        yaw_rad
    )

    yaw_deg = np.array([

        wrap_angle_deg(
            value
        )

        for value
        in yaw_deg

    ])

    # ========================================================
    # VELOCITY FEATURES
    # ========================================================

    print(
        "\nBUILDING VELOCITY FEATURES..."
    )

    feature_rows = []

    feature_indices = []

    for i in range(

        WINDOW - 1,

        n

    ):

        start = (

            i
            -
            WINDOW
            +
            1

        )

        features = make_features(

            accel[
                start:i + 1
            ],

            gyro[
                start:i + 1
            ],

            gravity[
                start:i + 1
            ]

        )

        feature_rows.append(
            features
        )

        feature_indices.append(
            i
        )

    X = np.asarray(

        feature_rows,

        dtype=np.float32

    )

    feature_indices = np.asarray(

        feature_indices,

        dtype=int

    )

    print(
        f"FEATURE WINDOWS: "
        f"{len(X)}"
    )

    # ========================================================
    # PREDICT VELOCITY
    # ========================================================

    print(
        "\nPREDICTING VELOCITY..."
    )

    predicted_speed = model.predict(
        X
    )

    predicted_speed = np.asarray(

        predicted_speed,

        dtype=float

    )

    # ========================================================
    # RAW SPEED LIMIT
    # ========================================================

    predicted_speed = np.clip(

        predicted_speed,

        MIN_SPEED_MS,

        MAX_SPEED_MS

    )

    # ========================================================
    # INITIALIZE FULL SPEED ARRAY
    # ========================================================

    estimated_speed = np.zeros(

        n,

        dtype=float

    )

    estimated_speed[
        feature_indices
    ] = predicted_speed

    if len(predicted_speed):

        estimated_speed[
            :WINDOW - 1
        ] = predicted_speed[0]

    # ========================================================
    # TEMPORAL SPEED SMOOTHING
    # ========================================================

    estimated_speed = smooth_speed(

        estimated_speed,

        SPEED_ALPHA

    )

    # ========================================================
    # PHYSICAL SPEED-RATE LIMIT
    # ========================================================

    estimated_speed = limit_speed_acceleration(

        estimated_speed,

        time

    )

    estimated_speed = np.clip(

        estimated_speed,

        MIN_SPEED_MS,

        MAX_SPEED_MS

    )

    # ========================================================
    # SPEED RESULTS
    # ========================================================

    print(
        "\nGNSS-FREE SPEED RESULTS"
    )

    print(
        "======================="
    )

    print(
        f"Mean speed   : "
        f"{np.mean(estimated_speed):.3f} m/s"
    )

    print(
        f"Median speed : "
        f"{np.median(estimated_speed):.3f} m/s"
    )

    print(
        f"Maximum speed: "
        f"{np.max(estimated_speed):.3f} m/s"
    )

    # ========================================================
    # DEAD-RECKONING VELOCITY
    # ========================================================

    velocity_east = (

        estimated_speed
        *
        np.cos(
            yaw_rad
        )

    )

    velocity_north = (

        estimated_speed
        *
        np.sin(
            yaw_rad
        )

    )

    # ========================================================
    # POSITION PROPAGATION
    # ========================================================

    east = np.zeros(

        n,

        dtype=float

    )

    north = np.zeros(

        n,

        dtype=float

    )

    for i in range(

        1,

        n

    ):

        dt = (

            time[i]
            -
            time[i - 1]

        )

        if (

            not np.isfinite(dt)

            or

            dt <= 0.0

            or

            dt > MAX_DT_S

        ):

            dt = DEFAULT_DT_S

        # ----------------------------------------------------
        # Trapezoidal integration
        # ----------------------------------------------------

        east[i] = (

            east[i - 1]

            +

            0.5
            *
            (
                velocity_east[i]
                +
                velocity_east[i - 1]
            )
            *
            dt

        )

        north[i] = (

            north[i - 1]

            +

            0.5
            *
            (
                velocity_north[i]
                +
                velocity_north[i - 1]
            )
            *
            dt

        )

    # ========================================================
    # DISTANCE
    # ========================================================

    distance_step = np.hypot(

        np.diff(
            east
        ),

        np.diff(
            north
        )

    )

    cumulative_distance = np.concatenate([

        [0.0],

        np.cumsum(
            distance_step
        )

    ])

    # ========================================================
    # OUTPUT
    # ========================================================

    result = pd.DataFrame({

        "TIME_S":
            time,

        "DR_YAW_DEG":
            yaw_deg,

        "DR_SPEED_MS":
            estimated_speed,

        "DR_SPEED_KMH":
            estimated_speed * 3.6,

        "DR_VELOCITY_EAST_MS":
            velocity_east,

        "DR_VELOCITY_NORTH_MS":
            velocity_north,

        "DR_EAST_M":
            east,

        "DR_NORTH_M":
            north,

        "DR_DISTANCE_M":
            cumulative_distance

    })

    # ========================================================
    # SAVE
    # ========================================================

    os.makedirs(

        "data/processed",

        exist_ok=True

    )

    result.to_csv(

        OUTPUT_FILE,

        index=False

    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print(
        "\nGNSS-FREE DEAD RECKONING COMPLETE"
    )

    print(
        "=================================="
    )

    print(
        f"SAMPLES PROCESSED      : "
        f"{n}"
    )

    print(
        "GNSS INPUTS TO ENGINE  : 0"
    )

    print(
        "VBOX INPUTS TO ENGINE  : 0"
    )

    print(
        "GPS ORIENTATION INPUT  : 0"
    )

    print(
        f"FINAL DR SPEED         : "
        f"{estimated_speed[-1]:.3f} m/s"
    )

    print(
        f"TOTAL DR DISTANCE      : "
        f"{cumulative_distance[-1]:.3f} m"
    )

    print(
        "\nOUTPUT:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()