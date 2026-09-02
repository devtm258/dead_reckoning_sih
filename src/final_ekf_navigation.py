import pandas as pd
import numpy as np

from load_data import load_smartphone_data


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_PATH = "data/processed/final_ekf_navigation.csv"

# Gyroscope 3-axis calibration obtained earlier
GYRO_YAW_COEF = 0.029372
GYRO_PITCH_COEF = 0.964380
GYRO_ROLL_COEF = 0.425011
GYRO_INTERCEPT = 0.234927

# GPS speed conversion
KMH_TO_MS = 1000.0 / 3600.0

# Gravity
G = 9.80665

# GPS measurement noise
GPS_POSITION_STD = 5.0
GPS_SPEED_STD = 1.5

# Yaw measurement noise
GPS_YAW_STD_DEG = 15.0


# ============================================================
# LOAD DATA
# ============================================================

data = load_smartphone_data()

print("FINAL EXTENDED KALMAN FILTER NAVIGATION")
print("========================================")


# ============================================================
# COLUMN NAMES
# ============================================================

TIME_COL = "TIME SINCE START (ms)"

LAT_COL = "GPS LATITUDE (degrees)"
LON_COL = "GPS LONGITUDE (degrees)"
SPEED_COL = "GPS SPEED (Kmh)"
GPS_YAW_COL = "GPS ORIENTATION (Â°)"

GYRO_YAW_COL = "GYROSCOPE Yaw (rad/s)"
GYRO_PITCH_COL = "GYROSCOPE Pitch (rad/s)"
GYRO_ROLL_COL = "GYROSCOPE Roll (rad/s)"

GRAV_X_COL = "GRAVITY X (m/s²)"
GRAV_Y_COL = "GRAVITY Y (m/s²)"
GRAV_Z_COL = "GRAVITY Z (m/s²)"


# ============================================================
# EXTRACT DATA
# ============================================================

time_ms = pd.to_numeric(
    data[TIME_COL],
    errors="coerce"
).to_numpy()

lat = pd.to_numeric(
    data[LAT_COL],
    errors="coerce"
).to_numpy()

lon = pd.to_numeric(
    data[LON_COL],
    errors="coerce"
).to_numpy()

gps_speed = pd.to_numeric(
    data[SPEED_COL],
    errors="coerce"
).to_numpy() * KMH_TO_MS

gps_yaw = pd.to_numeric(
    data[GPS_YAW_COL],
    errors="coerce"
).to_numpy()

gyro_yaw = pd.to_numeric(
    data[GYRO_YAW_COL],
    errors="coerce"
).to_numpy()

gyro_pitch = pd.to_numeric(
    data[GYRO_PITCH_COL],
    errors="coerce"
).to_numpy()

gyro_roll = pd.to_numeric(
    data[GYRO_ROLL_COL],
    errors="coerce"
).to_numpy()

grav_x = pd.to_numeric(
    data[GRAV_X_COL],
    errors="coerce"
).to_numpy()

grav_y = pd.to_numeric(
    data[GRAV_Y_COL],
    errors="coerce"
).to_numpy()

grav_z = pd.to_numeric(
    data[GRAV_Z_COL],
    errors="coerce"
).to_numpy()


# ============================================================
# VALIDATE DATA
# ============================================================

valid = (
    np.isfinite(time_ms)
    & np.isfinite(lat)
    & np.isfinite(lon)
    & np.isfinite(gps_speed)
    & np.isfinite(gyro_yaw)
    & np.isfinite(gyro_pitch)
    & np.isfinite(gyro_roll)
    & np.isfinite(grav_x)
    & np.isfinite(grav_y)
    & np.isfinite(grav_z)
)

print(f"\nVALID SAMPLES: {valid.sum()}")


# ============================================================
# KEEP VALID DATA
# ============================================================

time_ms = time_ms[valid]
lat = lat[valid]
lon = lon[valid]
gps_speed = gps_speed[valid]
gps_yaw = gps_yaw[valid]

gyro_yaw = gyro_yaw[valid]
gyro_pitch = gyro_pitch[valid]
gyro_roll = gyro_roll[valid]

grav_x = grav_x[valid]
grav_y = grav_y[valid]
grav_z = grav_z[valid]


N = len(time_ms)


# ============================================================
# GPS REFERENCE FRAME
#
# Local East/North coordinates relative to first GPS position.
# ============================================================

lat0 = lat[0]
lon0 = lon[0]

earth_radius = 6378137.0

lat_rad = np.radians(lat)
lon_rad = np.radians(lon)

lat0_rad = np.radians(lat0)
lon0_rad = np.radians(lon0)

gps_north = (
    (lat_rad - lat0_rad)
    * earth_radius
)

gps_east = (
    (lon_rad - lon0_rad)
    * earth_radius
    * np.cos(lat0_rad)
)


# ============================================================
# GRAVITY-BASED ROLL AND PITCH
# ============================================================

gravity_mag = np.sqrt(
    grav_x ** 2
    + grav_y ** 2
    + grav_z ** 2
)

gravity_mag = np.maximum(
    gravity_mag,
    1e-12
)

gx = grav_x / gravity_mag
gy = grav_y / gravity_mag
gz = grav_z / gravity_mag


gravity_roll = np.arctan2(
    gy,
    gz
)

gravity_pitch = np.arctan2(
    -gx,
    np.sqrt(
        gy ** 2
        + gz ** 2
    )
)


# ============================================================
# GYROSCOPE CALIBRATION
#
# Convert smartphone gyroscope values from rad/s to deg/s.
# Then apply previously identified 3-axis calibration model.
# ============================================================

gyro_yaw_deg = np.degrees(gyro_yaw)
gyro_pitch_deg = np.degrees(gyro_pitch)
gyro_roll_deg = np.degrees(gyro_roll)

calibrated_yaw_rate_deg = (
    GYRO_YAW_COEF * gyro_yaw_deg
    + GYRO_PITCH_COEF * gyro_pitch_deg
    + GYRO_ROLL_COEF * gyro_roll_deg
    + GYRO_INTERCEPT
)


# ============================================================
# CONVERT TO RAD/S
# ============================================================

calibrated_yaw_rate = np.radians(
    calibrated_yaw_rate_deg
)


# ============================================================
# ANGLE WRAPPING
# ============================================================

def wrap_angle(angle):

    return (
        (angle + np.pi)
        % (2.0 * np.pi)
    ) - np.pi


def circular_difference(a, b):

    return wrap_angle(
        a - b
    )


# ============================================================
# INITIAL YAW
# ============================================================

first_valid_gps_yaw = gps_yaw[
    np.isfinite(gps_yaw)
]

if len(first_valid_gps_yaw) > 0:

    initial_yaw = np.radians(
        first_valid_gps_yaw[0]
    )

else:

    initial_yaw = 0.0


# ============================================================
# STATE VECTOR
#
# x =
# [East,
#  North,
#  Velocity East,
#  Velocity North,
#  Yaw]
# ============================================================

state = np.array([
    gps_east[0],
    gps_north[0],
    0.0,
    0.0,
    initial_yaw
], dtype=float)


# ============================================================
# INITIAL COVARIANCE
# ============================================================

P = np.diag([
    GPS_POSITION_STD ** 2,
    GPS_POSITION_STD ** 2,
    GPS_SPEED_STD ** 2,
    GPS_SPEED_STD ** 2,
    np.radians(
        GPS_YAW_STD_DEG
    ) ** 2
])


# ============================================================
# PROCESS NOISE
# ============================================================

Q_base = np.diag([
    0.5,
    0.5,
    1.0,
    1.0,
    np.radians(2.0) ** 2
])


# ============================================================
# MEASUREMENT NOISE
# ============================================================

R_position = np.diag([
    GPS_POSITION_STD ** 2,
    GPS_POSITION_STD ** 2
])

R_speed = np.array([
    [GPS_SPEED_STD ** 2]
])

R_yaw = np.array([
    [np.radians(GPS_YAW_STD_DEG) ** 2]
])


# ============================================================
# STORAGE
# ============================================================

ekf_east = np.zeros(N)
ekf_north = np.zeros(N)
ekf_velocity_east = np.zeros(N)
ekf_velocity_north = np.zeros(N)
ekf_speed = np.zeros(N)
ekf_yaw = np.zeros(N)

roll_output = np.zeros(N)
pitch_output = np.zeros(N)

position_error = np.zeros(N)
speed_error = np.zeros(N)


# ============================================================
# EKF
# ============================================================

for k in range(N):

    if k == 0:

        dt = 0.01

    else:

        dt = (
            time_ms[k]
            - time_ms[k - 1]
        ) / 1000.0

        if (
            not np.isfinite(dt)
            or dt <= 0.0
            or dt > 1.0
        ):
            dt = 0.01

    # --------------------------------------------------------
    # CURRENT GRAVITY ORIENTATION
    # --------------------------------------------------------

    roll = gravity_roll[k]
    pitch = gravity_pitch[k]

    roll_output[k] = np.degrees(roll)
    pitch_output[k] = np.degrees(pitch)

    # --------------------------------------------------------
    # PREDICT YAW
    # --------------------------------------------------------

    yaw = state[4]

    yaw_new = wrap_angle(
        yaw
        + calibrated_yaw_rate[k] * dt
    )

    # --------------------------------------------------------
    # GPS SPEED
    # --------------------------------------------------------

    speed = gps_speed[k]

    # --------------------------------------------------------
    # VEHICLE VELOCITY FROM YAW + GPS SPEED
    # --------------------------------------------------------

    velocity_east = (
        speed
        * np.sin(yaw_new)
    )

    velocity_north = (
        speed
        * np.cos(yaw_new)
    )

    # --------------------------------------------------------
    # STATE PREDICTION
    # --------------------------------------------------------

    predicted_east = (
        state[0]
        + velocity_east * dt
    )

    predicted_north = (
        state[1]
        + velocity_north * dt
    )

    predicted_velocity_east = velocity_east
    predicted_velocity_north = velocity_north

    state_pred = np.array([
        predicted_east,
        predicted_north,
        predicted_velocity_east,
        predicted_velocity_north,
        yaw_new
    ])

    # --------------------------------------------------------
    # STATE TRANSITION MATRIX
    # --------------------------------------------------------

    F = np.eye(5)

    F[0, 2] = dt
    F[1, 3] = dt

    # --------------------------------------------------------
    # COVARIANCE PREDICTION
    # --------------------------------------------------------

    P = (
        F @ P @ F.T
        + Q_base * max(dt, 0.01)
    )

    state = state_pred

    # --------------------------------------------------------
    # GPS POSITION UPDATE
    # --------------------------------------------------------

    if (
        np.isfinite(gps_east[k])
        and np.isfinite(gps_north[k])
    ):

        z = np.array([
            gps_east[k],
            gps_north[k]
        ])

        H = np.zeros(
            (2, 5)
        )

        H[0, 0] = 1.0
        H[1, 1] = 1.0

        innovation = (
            z
            - H @ state
        )

        S = (
            H @ P @ H.T
            + R_position
        )

        K = (
            P @ H.T
            @ np.linalg.inv(S)
        )

        state = (
            state
            + K @ innovation
        )

        P = (
            np.eye(5)
            - K @ H
        ) @ P

    # --------------------------------------------------------
    # GPS SPEED UPDATE
    # --------------------------------------------------------

    if np.isfinite(gps_speed[k]):

        predicted_speed = np.sqrt(
            state[2] ** 2
            + state[3] ** 2
        )

        z_speed = np.array([
            gps_speed[k]
        ])

        H_speed = np.zeros(
            (1, 5)
        )

        velocity_norm = max(
            predicted_speed,
            1e-6
        )

        H_speed[0, 2] = (
            state[2]
            / velocity_norm
        )

        H_speed[0, 3] = (
            state[3]
            / velocity_norm
        )

        innovation = (
            z_speed
            - np.array([
                predicted_speed
            ])
        )

        S = (
            H_speed @ P
            @ H_speed.T
            + R_speed
        )

        K = (
            P @ H_speed.T
            @ np.linalg.inv(S)
        )

        state = (
            state
            + (
                K
                @ innovation
            )
        )

        P = (
            np.eye(5)
            - K @ H_speed
        ) @ P

    # --------------------------------------------------------
    # GPS YAW UPDATE
    #
    # Only use GPS orientation when speed is sufficient.
    # --------------------------------------------------------

    if (
        np.isfinite(gps_yaw[k])
        and gps_speed[k] > 2.0
    ):

        gps_yaw_rad = np.radians(
            gps_yaw[k]
        )

        yaw_error = circular_difference(
            gps_yaw_rad,
            state[4]
        )

        H_yaw = np.zeros(
            (1, 5)
        )

        H_yaw[0, 4] = 1.0

        S = (
            H_yaw @ P
            @ H_yaw.T
            + R_yaw
        )

        K = (
            P @ H_yaw.T
            @ np.linalg.inv(S)
        )

        state = (
            state
            + (
                K[:, 0]
                * yaw_error
            )
        )

        state[4] = wrap_angle(
            state[4]
        )

        P = (
            np.eye(5)
            - K @ H_yaw
        ) @ P

    # --------------------------------------------------------
    # SAVE STATE
    # --------------------------------------------------------

    ekf_east[k] = state[0]
    ekf_north[k] = state[1]

    ekf_velocity_east[k] = state[2]
    ekf_velocity_north[k] = state[3]

    ekf_speed[k] = np.sqrt(
        state[2] ** 2
        + state[3] ** 2
    )

    ekf_yaw[k] = np.degrees(
        wrap_angle(
            state[4]
        )
    )

    # --------------------------------------------------------
    # ERRORS
    # --------------------------------------------------------

    position_error[k] = np.sqrt(
        (
            ekf_east[k]
            - gps_east[k]
        ) ** 2
        +
        (
            ekf_north[k]
            - gps_north[k]
        ) ** 2
    )

    speed_error[k] = abs(
        ekf_speed[k]
        - gps_speed[k]
    )


# ============================================================
# RESULTS
# ============================================================

print("\nEKF RESULTS")
print("===========")

print(
    f"Final EKF East  : "
    f"{ekf_east[-1]:.3f} m"
)

print(
    f"Final EKF North : "
    f"{ekf_north[-1]:.3f} m"
)

print(
    f"Final EKF Yaw   : "
    f"{ekf_yaw[-1]:.3f}°"
)

print(
    f"Final EKF Speed : "
    f"{ekf_speed[-1]:.3f} m/s"
)


# ============================================================
# POSITION ERROR
# ============================================================

print("\nPOSITION ERROR")
print("==============")

print(
    f"Mean                : "
    f"{np.mean(position_error):.3f} m"
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
    f"{np.max(position_error):.3f} m"
)


# ============================================================
# SPEED ERROR
# ============================================================

print("\nSPEED ERROR")
print("===========")

print(
    f"Mean                : "
    f"{np.mean(speed_error):.3f} m/s"
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
    f"{np.max(speed_error):.3f} m/s"
)


# ============================================================
# SAVE OUTPUT
# ============================================================

output = pd.DataFrame({

    "TIME_MS": time_ms,

    "GPS_EAST_M": gps_east,
    "GPS_NORTH_M": gps_north,

    "EKF_EAST_M": ekf_east,
    "EKF_NORTH_M": ekf_north,

    "GPS_SPEED_MS": gps_speed,
    "EKF_SPEED_MS": ekf_speed,

    "GPS_YAW_DEG": gps_yaw,
    "EKF_YAW_DEG": ekf_yaw,

    "GRAVITY_ROLL_DEG": roll_output,
    "GRAVITY_PITCH_DEG": pitch_output,

    "CALIBRATED_GYRO_YAW_RATE_DEG_S":
        calibrated_yaw_rate_deg,

    "POSITION_ERROR_M":
        position_error,

    "SPEED_ERROR_MS":
        speed_error
})


output.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nOUTPUT SAVED:")
print(OUTPUT_PATH)

print(
    "\nFINAL EXTENDED KALMAN FILTER "
    "NAVIGATION COMPLETE."
)