from preprocessing import SMARTPHONE_COLUMNS


SMARTPHONE_FEATURES = [
    SMARTPHONE_COLUMNS["acc_x"],
    SMARTPHONE_COLUMNS["acc_y"],
    SMARTPHONE_COLUMNS["acc_z"],

    SMARTPHONE_COLUMNS["gyro_yaw"],
    SMARTPHONE_COLUMNS["gyro_pitch"],
    SMARTPHONE_COLUMNS["gyro_roll"],

    SMARTPHONE_COLUMNS["mag_x"],
    SMARTPHONE_COLUMNS["mag_y"],
    SMARTPHONE_COLUMNS["mag_z"],

    SMARTPHONE_COLUMNS["gravity_x"],
    SMARTPHONE_COLUMNS["gravity_y"],
    SMARTPHONE_COLUMNS["gravity_z"],

    SMARTPHONE_COLUMNS["speed"],
    SMARTPHONE_COLUMNS["gps_accuracy"],
    SMARTPHONE_COLUMNS["gps_orientation"],
]


def get_smartphone_features(data):
    """
    Select the smartphone measurements used as navigation features.
    """

    return data[SMARTPHONE_FEATURES].copy()

if __name__ == "__main__":

    from load_data import load_smartphone_data

    smartphone = load_smartphone_data()

    features = get_smartphone_features(smartphone)

    print("ORIGINAL DATA SHAPE:")
    print(smartphone.shape)

    print("\nFEATURE DATA SHAPE:")
    print(features.shape)

    print("\nFEATURE COLUMNS:")
    print(features.columns.tolist())