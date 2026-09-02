import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from load_data import load_smartphone_data


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()

ekf_path = "data/processed/final_ekf_navigation.csv"

ekf = pd.read_csv(ekf_path)


# ============================================================
# GPS TRAJECTORY
# ============================================================

lat = pd.to_numeric(
    smartphone["GPS LATITUDE (degrees)"],
    errors="coerce"
).to_numpy()

lon = pd.to_numeric(
    smartphone["GPS LONGITUDE (degrees)"],
    errors="coerce"
).to_numpy()


valid_gps = (
    np.isfinite(lat)
    & np.isfinite(lon)
)


lat = lat[valid_gps]
lon = lon[valid_gps]


# ============================================================
# CONVERT GPS TO LOCAL EAST/NORTH
# ============================================================

earth_radius = 6378137.0

lat0 = np.radians(lat[0])
lon0 = np.radians(lon[0])

lat_rad = np.radians(lat)
lon_rad = np.radians(lon)

gps_north = (
    (lat_rad - lat0)
    * earth_radius
)

gps_east = (
    (lon_rad - lon0)
    * earth_radius
    * np.cos(lat0)
)


# ============================================================
# EKF DATA
# ============================================================

ekf_east = ekf["EKF_EAST_M"].to_numpy()
ekf_north = ekf["EKF_NORTH_M"].to_numpy()

position_error = ekf[
    "POSITION_ERROR_M"
].to_numpy()


# ============================================================
# TRAJECTORY COMPARISON
# ============================================================

plt.figure(figsize=(10, 8))

plt.plot(
    gps_east,
    gps_north,
    label="GPS Trajectory"
)

plt.plot(
    ekf_east,
    ekf_north,
    label="EKF Trajectory"
)

plt.xlabel("East (m)")
plt.ylabel("North (m)")

plt.title(
    "GPS vs Extended Kalman Filter Trajectory"
)

plt.legend()
plt.grid(True)

plt.axis("equal")

plt.tight_layout()

plt.show()


# ============================================================
# POSITION ERROR
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    position_error
)

plt.xlabel("Sample")
plt.ylabel("Position Error (m)")

plt.title(
    "Extended Kalman Filter Position Error"
)

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# ERROR STATISTICS
# ============================================================

print("\nEKF TRAJECTORY VALIDATION")
print("=========================")

print(
    f"Mean position error   : "
    f"{np.mean(position_error):.3f} m"
)

print(
    f"Median position error : "
    f"{np.median(position_error):.3f} m"
)

print(
    f"95th percentile       : "
    f"{np.percentile(position_error, 95):.3f} m"
)

print(
    f"Maximum position error: "
    f"{np.max(position_error):.3f} m"
)


# ============================================================
# WORST 20 SAMPLES
# ============================================================

worst_indices = np.argsort(
    position_error
)[-20:][::-1]


print("\nWORST 20 POSITION ERRORS")
print("========================")

print(
    ekf.iloc[
        worst_indices
    ][
        [
            "TIME_MS",
            "GPS_EAST_M",
            "GPS_NORTH_M",
            "EKF_EAST_M",
            "EKF_NORTH_M",
            "GPS_SPEED_MS",
            "EKF_SPEED_MS",
            "POSITION_ERROR_M"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# SAVE WORST SAMPLES
# ============================================================

worst_output = ekf.iloc[
    worst_indices
]

worst_output.to_csv(
    "data/processed/ekf_worst_position_errors.csv",
    index=False
)


print(
    "\nWorst-error samples saved to:"
)

print(
    "data/processed/ekf_worst_position_errors.csv"
)


print(
    "\nEKF TRAJECTORY VALIDATION COMPLETE."
)