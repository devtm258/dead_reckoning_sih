import pandas as pd

from preprocessing import clean_column_names, SMARTPHONE_COLUMNS, VBOX_COLUMNS


SMARTPHONE_PATH = r"data\raw\Synchronised V abd S datasets\Synchronised V abd S datasets\Categorised IOVNB Dataset\S (Driver A)\S1\S-S1.csv"

VBOX_PATH = r"data\raw\Synchronised V abd S datasets\Synchronised V abd S datasets\Categorised IOVNB Dataset\S (Driver A)\S1\V-S1.csv"


def load_smartphone_data():
    data = pd.read_csv(
        SMARTPHONE_PATH,
        encoding="cp1252"
    )

    data = clean_column_names(data)

    return data


def load_vbox_data():
    data = pd.read_csv(
        VBOX_PATH,
        encoding="cp1252"
    )

    data = clean_column_names(data)

    return data


if __name__ == "__main__":

    smartphone = load_smartphone_data()
    vbox = load_vbox_data()

    print("Smartphone data:", smartphone.shape)
    print("VBOX data:", vbox.shape)

    print("\nSMARTPHONE ACCELEROMETER X COLUMN:")
    print(SMARTPHONE_COLUMNS["acc_x"])

    print("\nSMARTPHONE GPS LATITUDE COLUMN:")
    print(SMARTPHONE_COLUMNS["latitude"])

    print("\nVBOX LATITUDE COLUMN:")
    print(VBOX_COLUMNS["latitude"])

    print("\nVBOX YAW RATE COLUMN:")
    print(VBOX_COLUMNS["yaw_rate"])