import numpy as np
import pandas as pd

from load_data import load_smartphone_data


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = "data/processed/ekf_navigation.csv"

# Gyroscope calibration from previous analysis
GYRO_YAW_COEFF = 0.029372
GYRO_PITCH_COEFF = 0.964380
GYRO_ROLL_COEFF = 0.425011
GYRO_INTERCEPT = 0.234927

# GPS measurement noise
GPS_POSITION_STD = 3.0
GPS_SPEED_STD = 1.5

# Accelerometer noise
ACCELERATION_STD = 1.5

# Maximum accepted time step
MAX_DT = 1.0


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()

print()
print("CORRECTED EXTENDED KALMAN FILTER NAVIGATION")
print("============================================")
print()


# ============================================================
# COLUMN FINDER
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


# ============================================================
# COLUMN NAMES
# ============================================================

TIME_COL = "TIME SINCE START (ms)"

ACC_X_COL = "ACCELEROMETER X (m/s²)"
ACC_Y_COL = "ACCELEROMETER Y (m/s²)"
ACC_Z_COL = "ACCELEROMETER Z (m/s²)"

GRAV_X_COL = "GRAVITY X (m/s²)"
GRAV_Y_COL = "GRAVITY Y (m/s²)"
GRAV_Z_COL = "GRAVITY Z (m/s²)"

GYRO_YAW_COL = "GYROSCOPE Yaw (rad/s)"
GYRO_PITCH_COL = "GYROSCOPE Pitch (rad/s)"
GYRO_ROLL_COL = "GYROSCOPE Roll (rad/s)"

GPS_LAT_COL = "GPS LATITUDE (degrees)"
GPS_LON_COL = "GPS LONGITUDE (degrees)"
GPS_SPEED_COL = "GPS SPEED (Kmh)"


MAG_X_COL = find_column("MAGNETIC FIELD X")
MAG_Y_COL = find_column("MAGNETIC FIELD Y")
MAG_Z_COL = find_column("MAGNETIC FIELD Z")


# ============================================================
# EXTRACT DATA
# ============================================================

time_ms = smartphone[TIME_COL].to_numpy(dtype=float)

acc = smartphone[
    [
        ACC_X_COL,
        ACC_Y_COL,
        ACC_Z_COL
    ]
].to_numpy(dtype=float)

gravity = smartphone[
    [
        GRAV_X_COL,
        GRAV_Y_COL,
        GRAV_Z_COL
    ]
].to_numpy(dtype=float)

gyro = smartphone[
    [
        GYRO_YAW_COL,
        GYRO_PITCH_COL,
        GYRO_ROLL_COL
    ]
].to_numpy(dtype=float)

gps_lat = smartphone[
    GPS_LAT_COL
].to_numpy(dtype=float)

gps_lon = smartphone[
    GPS_LON_COL
].to_numpy(dtype=float)

gps_speed_kmh = smartphone[
    GPS_SPEED_COL
].to_numpy(dtype=float)


# ============================================================
# VALID DATA
# ============================================================

valid = (
    np.isfinite(time_ms)
    &
    np.all(np.isfinite(acc), axis=1)
    &
    np.all(np.isfinite(gravity), axis=1)
    &
    np.all(np.isfinite(gyro), axis=1)
    &
    np.isfinite(gps_lat)
    &
    np.isfinite(gps_lon)
    &
    np.isfinite(gps_speed_kmh)
)

time_ms = time_ms[valid]
acc = acc[valid]
gravity = gravity[valid]
gyro = gyro[valid]
gps_lat = gps_lat[valid]
gps_lon = gps_lon[valid]
gps_speed_kmh = gps_speed_kmh[valid]


print("VALID SAMPLES:", len(time_ms))


# ============================================================
# TIME
# ============================================================

time_s = time_ms / 1000.0


# ============================================================
# GPS → LOCAL EAST/NORTH FRAME
# ============================================================

earth_radius = 6378137.0

lat0 = np.radians(gps_lat[0])
lon0 = np.radians(gps_lon[0])

lat = np.radians(gps_lat)
lon = np.radians(gps_lon)

gps_east = (
    earth_radius
    * np.cos(lat0)
    * (lon - lon0)
)

gps_north = (
    earth_radius
    * (lat - lat0)
)


gps_speed = (
    gps_speed_kmh / 3.6
)


# ============================================================
# GRAVITY-REMOVED LINEAR ACCELERATION
# ============================================================

# Smartphone accelerometer contains gravity.
#
# Gravity sensor gives the gravity vector in the same
# smartphone coordinate frame.
#
# Therefore:
#
# linear acceleration = accelerometer - gravity
#
# This is performed before any navigation-frame rotation.

linear_acc = (
    acc - gravity
)


# ============================================================
# GYROSCOPE CALIBRATION
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


yaw_rate_deg = (
    GYRO_YAW_COEFF * gyro_yaw_deg
    +
    GYRO_PITCH_COEFF * gyro_pitch_deg
    +
    GYRO_ROLL_COEFF * gyro_roll_deg
    +
    GYRO_INTERCEPT
)


yaw_rate_rad = np.radians(
    yaw_rate_deg
)


# ============================================================
# INITIAL STATE
#
# [east_position,
#  north_position,
#  east_velocity,
#  north_velocity,
#  yaw]
# ============================================================

state = np.array([
    gps_east[0],
    gps_north[0],
    gps_speed[0],
    0.0,
    0.0
], dtype=float)


# ============================================================
# INITIAL COVARIANCE
# ============================================================

P = np.diag([
    9.0,
    9.0,
    4.0,
    4.0,
    np.radians(15.0) ** 2
])


# ============================================================
# STORAGE
# ============================================================

n = len(time_s)

ekf_east = np.zeros(n)
ekf_north = np.zeros(n)

ekf_velocity_east = np.zeros(n)
ekf_velocity_north = np.zeros(n)

ekf_speed = np.zeros(n)

ekf_yaw = np.zeros(n)


# ============================================================
# ANGLE WRAPPING
# ============================================================

def wrap_angle(angle):

    return (
        (angle + np.pi)
        % (2.0 * np.pi)
    ) - np.pi


# ============================================================
# INITIAL OUTPUT
# ============================================================

ekf_east[0] = state[0]
ekf_north[0] = state[1]

ekf_velocity_east[0] = state[2]
ekf_velocity_north[0] = state[3]

ekf_speed[0] = np.hypot(
    state[2],
    state[3]
)

ekf_yaw[0] = state[4]


# ============================================================
# EKF
# ============================================================

for i in range(1, n):

    dt = (
        time_s[i]
        -
        time_s[i - 1]
    )

    if dt <= 0 or dt > MAX_DT:

        ekf_east[i] = state[0]
        ekf_north[i] = state[1]

        ekf_velocity_east[i] = state[2]
        ekf_velocity_north[i] = state[3]

        ekf_speed[i] = np.hypot(
            state[2],
            state[3]
        )

        ekf_yaw[i] = state[4]

        continue


    # ========================================================
    # PREDICT YAW
    # ========================================================

    yaw = state[4]

    yaw_pred = wrap_angle(
        yaw
        +
        yaw_rate_rad[i] * dt
    )


    # ========================================================
    # PHONE-FRAME LINEAR ACCELERATION
    # ========================================================

    ax_phone = linear_acc[i, 0]
    ay_phone = linear_acc[i, 1]


    # ========================================================
    # NAVIGATION FRAME ROTATION
    # ========================================================
    #
    # IMPORTANT:
    # This assumes the smartphone horizontal X/Y frame
    # corresponds approximately to the navigation heading
    # represented by the EKF yaw.
    #
    # The GPS corrections prevent unbounded drift.
    #

    c = np.cos(yaw_pred)
    s = np.sin(yaw_pred)

    ax_nav = (
        c * ax_phone
        -
        s * ay_phone
    )

    ay_nav = (
        s * ax_phone
        +
        c * ay_phone
    )


    # ========================================================
    # PREDICT POSITION
    # ========================================================

    east = state[0]
    north = state[1]

    velocity_east = state[2]
    velocity_north = state[3]


    east_pred = (
        east
        +
        velocity_east * dt
        +
        0.5 * ax_nav * dt ** 2
    )

    north_pred = (
        north
        +
        velocity_north * dt
        +
        0.5 * ay_nav * dt ** 2
    )


    # ========================================================
    # PREDICT VELOCITY
    # ========================================================

    velocity_east_pred = (
        velocity_east
        +
        ax_nav * dt
    )

    velocity_north_pred = (
        velocity_north
        +
        ay_nav * dt
    )


    predicted_state = np.array([
        east_pred,
        north_pred,
        velocity_east_pred,
        velocity_north_pred,
        yaw_pred
    ])


    # ========================================================
    # STATE TRANSITION MATRIX
    # ========================================================

    F = np.array([
        [1.0, 0.0, dt,  0.0, 0.0],
        [0.0, 1.0, 0.0, dt,  0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0]
    ])


    # ========================================================
    # PROCESS NOISE
    # ========================================================

    acceleration_variance = (
        ACCELERATION_STD ** 2
    )

    position_variance = (
        0.25
        *
        acceleration_variance
        *
        dt ** 4
    )

    velocity_variance = (
        acceleration_variance
        *
        dt ** 2
    )

    yaw_variance = (
        np.radians(1.0) ** 2
    )


    Q = np.diag([
        position_variance,
        position_variance,
        velocity_variance,
        velocity_variance,
        yaw_variance
    ])


    # ========================================================
    # COVARIANCE PREDICTION
    # ========================================================

    P = (
        F
        @ P
        @ F.T
        +
        Q
    )


    # ========================================================
    # GPS POSITION + SPEED MEASUREMENT
    # ========================================================

    measurement = np.array([
        gps_east[i],
        gps_north[i],
        gps_speed[i]
    ])


    # EKF predicted measurement
    predicted_measurement = np.array([
        predicted_state[0],
        predicted_state[1],
        np.hypot(
            predicted_state[2],
            predicted_state[3]
        )
    ])


    # ========================================================
    # MEASUREMENT MATRIX
    # ========================================================

    predicted_speed = max(
        np.hypot(
            predicted_state[2],
            predicted_state[3]
        ),
        1e-6
    )

    H = np.array([

        [
            1.0,
            0.0,
            0.0,
            0.0,
            0.0
        ],

        [
            0.0,
            1.0,
            0.0,
            0.0,
            0.0
        ],

        [
            0.0,
            0.0,
            predicted_state[2] / predicted_speed,
            predicted_state[3] / predicted_speed,
            0.0
        ]
    ])


    # ========================================================
    # MEASUREMENT NOISE
    # ========================================================

    R = np.diag([
        GPS_POSITION_STD ** 2,
        GPS_POSITION_STD ** 2,
        GPS_SPEED_STD ** 2
    ])


    # ========================================================
    # INNOVATION
    # ========================================================

    innovation = (
        measurement
        -
        predicted_measurement
    )


    # ========================================================
    # INNOVATION COVARIANCE
    # ========================================================

    S = (
        H
        @ P
        @ H.T
        +
        R
    )


    # ========================================================
    # KALMAN GAIN
    # ========================================================

    K = (
        P
        @ H.T
        @ np.linalg.inv(S)
    )


    # ========================================================
    # STATE UPDATE
    # ========================================================

    state = (
        predicted_state
        +
        K @ innovation
    )


    state[4] = wrap_angle(
        state[4]
    )


    # ========================================================
    # COVARIANCE UPDATE
    # ========================================================

    identity = np.eye(5)

    P = (
        identity
        -
        K @ H
    ) @ P


    # Numerical symmetry
    P = (
        P + P.T
    ) / 2.0


    # ========================================================
    # STORE
    # ========================================================

    ekf_east[i] = state[0]
    ekf_north[i] = state[1]

    ekf_velocity_east[i] = state[2]
    ekf_velocity_north[i] = state[3]

    ekf_speed[i] = np.hypot(
        state[2],
        state[3]
    )

    ekf_yaw[i] = state[4]


# ============================================================
# ERROR ANALYSIS
# ============================================================

position_error = np.sqrt(
    (
        ekf_east
        -
        gps_east
    ) ** 2
    +
    (
        ekf_north
        -
        gps_north
    ) ** 2
)


speed_error = np.abs(
    ekf_speed
    -
    gps_speed
)


# ============================================================
# OUTPUT DATAFRAME
# ============================================================

output = pd.DataFrame({

    "TIME_MS":
        time_ms,

    "GPS_EAST_M":
        gps_east,

    "GPS_NORTH_M":
        gps_north,

    "GPS_SPEED_MS":
        gps_speed,

    "GYRO_YAW_RATE_DEG_S":
        yaw_rate_deg,

    "LINEAR_ACCEL_X_MS2":
        linear_acc[:, 0],

    "LINEAR_ACCEL_Y_MS2":
        linear_acc[:, 1],

    "EKF_EAST_M":
        ekf_east,

    "EKF_NORTH_M":
        ekf_north,

    "EKF_VELOCITY_EAST_MS":
        ekf_velocity_east,

    "EKF_VELOCITY_NORTH_MS":
        ekf_velocity_north,

    "EKF_SPEED_MS":
        ekf_speed,

    "EKF_YAW_DEG":
        np.degrees(ekf_yaw),

    "POSITION_ERROR_M":
        position_error,

    "SPEED_ERROR_MS":
        speed_error
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
print("EKF RESULTS")
print("===========")

print(
    f"Final EKF East       : "
    f"{ekf_east[-1]:.3f} m"
)

print(
    f"Final EKF North      : "
    f"{ekf_north[-1]:.3f} m"
)

print(
    f"Final EKF Yaw        : "
    f"{np.degrees(ekf_yaw[-1]):.3f}°"
)

print(
    f"Final EKF Speed      : "
    f"{ekf_speed[-1]:.3f} m/s"
)


print()
print("POSITION ERROR")
print("==============")

print(
    f"Mean                : "
    f"{position_error.mean():.3f} m"
)

print(
    f"Median              : "
    f"{np.median(position_error):.3f} m"
)

print(
    f"95th percentile     : "
    f"{np.percentile(position_error, 95):.3f} m"
)

print(
    f"Maximum             : "
    f"{position_error.max():.3f} m"
)


print()
print("SPEED ERROR")
print("===========")

print(
    f"Mean                : "
    f"{speed_error.mean():.3f} m/s"
)

print(
    f"Median              : "
    f"{np.median(speed_error):.3f} m/s"
)

print(
    f"95th percentile     : "
    f"{np.percentile(speed_error, 95):.3f} m/s"
)

print(
    f"Maximum             : "
    f"{speed_error.max():.3f} m/s"
)


print()
print("OUTPUT SAVED:")
print(OUTPUT_FILE)

print()
print(
    "CORRECTED EXTENDED KALMAN FILTER "
    "NAVIGATION COMPLETE."
)