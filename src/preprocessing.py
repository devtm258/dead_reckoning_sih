SMARTPHONE_COLUMNS = {
    "latitude": "GPS LATITUDE (degrees)",
    "longitude": "GPS LONGITUDE (degrees)",
    "altitude": "GPS ALTITUDE (m)",
    "speed": "GPS SPEED (Kmh)",
    "gps_accuracy": "GPS ACCURACY (m)",
    "gps_orientation": "GPS ORIENTATION (Â°)",
    "satellites": "GPS SATELLITES IN RANGE",
    "time_ms": "TIME SINCE START (ms)",
    "date": "DATE (YYYY-MO-DD HH-MI-SS_SSS)",

    "acc_x": "ACCELEROMETER X (m/s²)",
    "acc_y": "ACCELEROMETER Y (m/s²)",
    "acc_z": "ACCELEROMETER Z (m/s²)",

    "gravity_x": "GRAVITY X (m/s²)",
    "gravity_y": "GRAVITY Y (m/s²)",
    "gravity_z": "GRAVITY Z (m/s²)",

    "gyro_yaw": "GYROSCOPE Yaw (rad/s)",
    "gyro_pitch": "GYROSCOPE Pitch (rad/s)",
    "gyro_roll": "GYROSCOPE Roll (rad/s)",

    "mag_x": "MAGNETIC FIELD X (Î¼T)",
    "mag_y": "MAGNETIC FIELD Y (Î¼T)",
    "mag_z": "MAGNETIC FIELD Z (Î¼T)",

    "orientation_yaw": "ORIENTATION (Yaw) (Â°)",
    "orientation_pitch": "ORIENTATION (Pitch) (Â°)",
    "orientation_roll": "ORIENTATION (Roll ) (Â°)"
}


VBOX_COLUMNS = {
    "satellites": "No of GPS Satellites Available",
    "time_s": "Time Since Start of Day (seconds)",
    "latitude": "Latitude (degrees)",
    "longitude": "Longitude (degrees)",
    "speed": "Velocity (km/hr)",
    "heading": "Heading (degrees)",
    "height": "Height (km)",
    "vertical_velocity": "Vertical velocity (km/hr)",
    "sample_period": "Sample period (seconds)",
    "steering_angle": "Steering Angle (degrees)",
    "yaw_rate": "Yaw Rate (deg/sec)",
    "longitudinal_acceleration": "Indicated Longitudinal Acceleration (g)",
    "lateral_acceleration": "Indicated Lateral Acceleration (g)"
}


def clean_column_names(data):
    """
    Remove unnecessary spaces from column names.
    """

    data = data.copy()

    data.columns = data.columns.str.strip()

    return data