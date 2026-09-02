import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from load_data import load_smartphone_data


# ============================================================
# CONFIGURATION
# ============================================================

EKF_PATH = "data/processed/final_ekf_navigation.csv"

OUTPUT_PATH = (
    "data/processed/"
    "final_navigation_validation.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()
ekf = pd.read_csv(EKF_PATH)

print("FINAL NAVIGATION VALIDATION")
print("===========================")


# ============================================================
# GPS DATA
# ============================================================

lat = pd.to_numeric(
    smartphone["GPS LATITUDE (degrees)"],
    errors="coerce"
).to_numpy()

lon = pd.to_numeric(
    smartphone["GPS LONGITUDE (degrees)"],
    errors="coerce"
).to_numpy()

gps_speed = pd.to_numeric(
    smartphone["GPS SPEED (Kmh)"],
    errors="coerce"
).to_numpy()

gps_yaw = pd.to_numeric(
    smartphone["GPS ORIENTATION (Â°)"],
    errors="coerce"
).to_numpy()


# ============================================================
# VALID GPS SAMPLES
# ============================================================

valid = (
    np.isfinite(lat)
    & np.isfinite(lon)
    & np.isfinite(gps_speed)
)

lat = lat[valid]
lon = lon[valid]
gps_speed = gps_speed[valid]
gps_yaw = gps_yaw[valid]


# ============================================================
# LOCAL GPS COORDINATES
# ============================================================

R = 6378137.0

lat0 = np.radians(lat[0])
lon0 = np.radians(lon[0])

lat_rad = np.radians(lat)
lon_rad = np.radians(lon)

gps_north = (
    (lat_rad - lat0)
    * R
)

gps_east = (
    (lon_rad - lon0)
    * R
    * np.cos(lat0)
)


# ============================================================
# EKF VALUES
# ============================================================

ekf_east = ekf[
    "EKF_EAST_M"
].to_numpy()

ekf_north = ekf[
    "EKF_NORTH_M"
].to_numpy()

ekf_speed = ekf[
    "EKF_SPEED_MS"
].to_numpy()

position_error = ekf[
    "POSITION_ERROR_M"
].to_numpy()

speed_error = ekf[
    "SPEED_ERROR_MS"
].to_numpy()

ekf_yaw = ekf[
    "EKF_YAW_DEG"
].to_numpy()


# ============================================================
# LENGTH ALIGNMENT
# ============================================================

N = min(
    len(gps_east),
    len(ekf_east)
)

gps_east = gps_east[:N]
gps_north = gps_north[:N]

gps_speed = gps_speed[:N]
gps_yaw = gps_yaw[:N]

ekf_east = ekf_east[:N]
ekf_north = ekf_north[:N]

ekf_speed = ekf_speed[:N]
ekf_yaw = ekf_yaw[:N]

position_error = position_error[:N]
speed_error = speed_error[:N]


# ============================================================
# GPS SPEED CONVERSION
# ============================================================

gps_speed_ms = (
    gps_speed
    * 1000.0
    / 3600.0
)


# ============================================================
# GPS SPEED BASELINE ERROR
# ============================================================

gps_speed_error = np.zeros(N)

# GPS compared with itself is zero.
# This is intentionally retained as the reference.


# ============================================================
# TRAJECTORY DISTANCE
# ============================================================

gps_step_distance = np.sqrt(
    np.diff(gps_east) ** 2
    +
    np.diff(gps_north) ** 2
)

ekf_step_distance = np.sqrt(
    np.diff(ekf_east) ** 2
    +
    np.diff(ekf_north) ** 2
)

gps_total_distance = np.sum(
    gps_step_distance
)

ekf_total_distance = np.sum(
    ekf_step_distance
)


# ============================================================
# TRAJECTORY FINAL DISPLACEMENT
# ============================================================

gps_final_displacement = np.sqrt(
    gps_east[-1] ** 2
    +
    gps_north[-1] ** 2
)

ekf_final_displacement = np.sqrt(
    ekf_east[-1] ** 2
    +
    ekf_north[-1] ** 2
)


# ============================================================
# YAW ERROR
# ============================================================

def circular_difference(a, b):

    return (
        (
            a - b + 180.0
        )
        % 360.0
    ) - 180.0


yaw_valid = (
    np.isfinite(gps_yaw)
    & np.isfinite(ekf_yaw)
)

yaw_error = np.abs(
    circular_difference(
        ekf_yaw[yaw_valid],
        gps_yaw[yaw_valid]
    )
)


# ============================================================
# POSITION ERROR STATISTICS
# ============================================================

position_mean = np.mean(
    position_error
)

position_median = np.median(
    position_error
)

position_95 = np.percentile(
    position_error,
    95
)

position_max = np.max(
    position_error
)


# ============================================================
# SPEED ERROR STATISTICS
# ============================================================

speed_mean = np.mean(
    speed_error
)

speed_median = np.median(
    speed_error
)

speed_95 = np.percentile(
    speed_error,
    95
)

speed_max = np.max(
    speed_error
)


# ============================================================
# YAW ERROR STATISTICS
# ============================================================

if len(yaw_error) > 0:

    yaw_mean = np.mean(
        yaw_error
    )

    yaw_median = np.median(
        yaw_error
    )

    yaw_95 = np.percentile(
        yaw_error,
        95
    )

    yaw_max = np.max(
        yaw_error
    )

else:

    yaw_mean = np.nan
    yaw_median = np.nan
    yaw_95 = np.nan
    yaw_max = np.nan


# ============================================================
# PRINT RESULTS
# ============================================================

print("\nDATASET")
print("=======")

print(
    f"Samples : {N}"
)


print("\nTRAJECTORY")
print("==========")

print(
    f"GPS total distance : "
    f"{gps_total_distance:.3f} m"
)

print(
    f"EKF total distance : "
    f"{ekf_total_distance:.3f} m"
)

print(
    f"GPS final displacement : "
    f"{gps_final_displacement:.3f} m"
)

print(
    f"EKF final displacement : "
    f"{ekf_final_displacement:.3f} m"
)


print("\nPOSITION PERFORMANCE")
print("====================")

print(
    f"Mean error       : "
    f"{position_mean:.3f} m"
)

print(
    f"Median error     : "
    f"{position_median:.3f} m"
)

print(
    f"95th percentile  : "
    f"{position_95:.3f} m"
)

print(
    f"Maximum error    : "
    f"{position_max:.3f} m"
)


print("\nSPEED PERFORMANCE")
print("=================")

print(
    f"Mean error       : "
    f"{speed_mean:.3f} m/s"
)

print(
    f"Median error     : "
    f"{speed_median:.3f} m/s"
)

print(
    f"95th percentile  : "
    f"{speed_95:.3f} m/s"
)

print(
    f"Maximum error    : "
    f"{speed_max:.3f} m/s"
)


print("\nYAW PERFORMANCE")
print("================")

print(
    f"Mean error       : "
    f"{yaw_mean:.3f}°"
)

print(
    f"Median error     : "
    f"{yaw_median:.3f}°"
)

print(
    f"95th percentile  : "
    f"{yaw_95:.3f}°"
)

print(
    f"Maximum error    : "
    f"{yaw_max:.3f}°"
)


# ============================================================
# ERROR THRESHOLDS
# ============================================================

print("\nPOSITION ERROR THRESHOLDS")
print("=========================")

for threshold in [1, 2, 5, 10, 20, 50]:

    percentage = (
        np.mean(
            position_error > threshold
        )
        * 100.0
    )

    print(
        f"> {threshold:2d} m : "
        f"{percentage:.2f}%"
    )


print("\nSPEED ERROR THRESHOLDS")
print("======================")

for threshold in [0.5, 1, 2, 5, 10]:

    percentage = (
        np.mean(
            speed_error > threshold
        )
        * 100.0
    )

    print(
        f"> {threshold:4.1f} m/s : "
        f"{percentage:.2f}%"
    )


# ============================================================
# WORST POSITION ERRORS
# ============================================================

worst_indices = np.argsort(
    position_error
)[-20:][::-1]


print("\nWORST 20 POSITION ERRORS")
print("========================")

worst = pd.DataFrame({

    "GPS_EAST_M":
        gps_east[worst_indices],

    "GPS_NORTH_M":
        gps_north[worst_indices],

    "EKF_EAST_M":
        ekf_east[worst_indices],

    "EKF_NORTH_M":
        ekf_north[worst_indices],

    "GPS_SPEED_MS":
        gps_speed_ms[worst_indices],

    "EKF_SPEED_MS":
        ekf_speed[worst_indices],

    "EKF_YAW_DEG":
        ekf_yaw[worst_indices],

    "POSITION_ERROR_M":
        position_error[worst_indices],

    "SPEED_ERROR_MS":
        speed_error[worst_indices]
})

print(
    worst.to_string(
        index=False
    )
)


# ============================================================
# SAVE FINAL VALIDATION DATA
# ============================================================

validation = pd.DataFrame({

    "GPS_EAST_M":
        gps_east,

    "GPS_NORTH_M":
        gps_north,

    "EKF_EAST_M":
        ekf_east,

    "EKF_NORTH_M":
        ekf_north,

    "GPS_SPEED_MS":
        gps_speed_ms,

    "EKF_SPEED_MS":
        ekf_speed,

    "GPS_YAW_DEG":
        gps_yaw,

    "EKF_YAW_DEG":
        ekf_yaw,

    "POSITION_ERROR_M":
        position_error,

    "SPEED_ERROR_MS":
        speed_error
})


validation.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# PLOT 1 — TRAJECTORY
# ============================================================

plt.figure(
    figsize=(10, 8)
)

plt.plot(
    gps_east,
    gps_north,
    label="GPS"
)

plt.plot(
    ekf_east,
    ekf_north,
    label="EKF"
)

plt.xlabel(
    "East (m)"
)

plt.ylabel(
    "North (m)"
)

plt.title(
    "Final GPS vs EKF Navigation"
)

plt.legend()

plt.grid(True)

plt.axis(
    "equal"
)

plt.tight_layout()

plt.show()


# ============================================================
# PLOT 2 — POSITION ERROR
# ============================================================

plt.figure(
    figsize=(10, 5)
)

plt.plot(
    position_error
)

plt.axhline(
    5.0,
    linestyle="--",
    label="5 m"
)

plt.axhline(
    10.0,
    linestyle="--",
    label="10 m"
)

plt.xlabel(
    "Sample"
)

plt.ylabel(
    "Position Error (m)"
)

plt.title(
    "Final EKF Position Error"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# PLOT 3 — SPEED ERROR
# ============================================================

plt.figure(
    figsize=(10, 5)
)

plt.plot(
    speed_error
)

plt.xlabel(
    "Sample"
)

plt.ylabel(
    "Speed Error (m/s)"
)

plt.title(
    "Final EKF Speed Error"
)

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# PLOT 4 — YAW
# ============================================================

plt.figure(
    figsize=(10, 5)
)

plt.plot(
    ekf_yaw,
    label="EKF Yaw"
)

valid_yaw_plot = np.isfinite(
    gps_yaw
)

plt.plot(
    np.where(
        valid_yaw_plot
    )[0],
    gps_yaw[
        valid_yaw_plot
    ],
    label="GPS Orientation"
)

plt.xlabel(
    "Sample"
)

plt.ylabel(
    "Yaw (degrees)"
)

plt.title(
    "EKF vs GPS Orientation"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# COMPLETE
# ============================================================

print("\nFINAL VALIDATION SAVED:")
print(OUTPUT_PATH)

print(
    "\nFINAL NAVIGATION VALIDATION COMPLETE."
)