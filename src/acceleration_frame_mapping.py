import pandas as pd
import numpy as np

from load_data import load_smartphone_data


# ============================================================
# LOAD DATA
# ============================================================

data = load_smartphone_data()

print("ACCELERATION FRAME MAPPING CHECK")
print("================================")


# ============================================================
# FIND ACCELEROMETER COLUMNS
# ============================================================

ACC_X = "ACCELEROMETER X (m/s²)"
ACC_Y = "ACCELEROMETER Y (m/s²)"
ACC_Z = "ACCELEROMETER Z (m/s²)"


# ============================================================
# FIND POSSIBLE VBOX ACCELERATION COLUMNS
# ============================================================

print("\nSEARCHING FOR VBOX ACCELERATION COLUMNS...")
print("--------------------------------------------")

for col in data.columns:
    name = str(col).upper()

    if (
        "ACC" in name
        or "ACCELERATION" in name
        or "VBOX" in name
        or "LONGITUDINAL" in name
        or "LATERAL" in name
    ):
        print(col)


# ============================================================
# EXTRACT SMARTPHONE ACCELEROMETER
# ============================================================

acc = data[
    [ACC_X, ACC_Y, ACC_Z]
].apply(
    pd.to_numeric,
    errors="coerce"
)


# ============================================================
# VALID SAMPLES
# ============================================================

valid = np.isfinite(
    acc.to_numpy()
).all(axis=1)

acc = acc.loc[valid].reset_index(drop=True)


print("\nSMARTPHONE ACCELEROMETER")
print("========================")

print(
    f"Valid samples : {len(acc)}"
)

print(
    f"X mean : {acc[ACC_X].mean():.6f} m/s²"
)

print(
    f"Y mean : {acc[ACC_Y].mean():.6f} m/s²"
)

print(
    f"Z mean : {acc[ACC_Z].mean():.6f} m/s²"
)


# ============================================================
# ACCELEROMETER MAGNITUDE
# ============================================================

acc_magnitude = np.sqrt(
    acc[ACC_X] ** 2
    + acc[ACC_Y] ** 2
    + acc[ACC_Z] ** 2
)

print("\nACCELEROMETER MAGNITUDE")
print("=======================")

print(
    f"Mean : {acc_magnitude.mean():.6f} m/s²"
)

print(
    f"Std  : {acc_magnitude.std():.6f} m/s²"
)

print(
    f"Min  : {acc_magnitude.min():.6f} m/s²"
)

print(
    f"Max  : {acc_magnitude.max():.6f} m/s²"
)


# ============================================================
# CHECK FOR VBOX ACCELERATION REFERENCE
# ============================================================

possible_vbox = []

for col in data.columns:

    name = str(col).upper()

    if (
        "VBOX" in name
        and (
            "ACC" in name
            or "ACCELERATION" in name
        )
    ):
        possible_vbox.append(col)


print("\nVBOX ACCELERATION REFERENCE")
print("===========================")

if len(possible_vbox) == 0:

    print(
        "NO VBOX ACCELERATION COLUMN FOUND."
    )

    print(
        "\nRESULT:"
    )

    print(
        "Acceleration frame calibration "
        "cannot be performed from the current "
        "loaded columns."
    )

else:

    for col in possible_vbox:
        print(col)

    print(
        "\nUse these columns for the next "
        "calibration step."
    )


# ============================================================
# CHECK DATASET COLUMN COUNT
# ============================================================

print("\nDATASET COLUMNS")
print("===============")

for i, col in enumerate(data.columns):

    print(
        f"{i:02d} : {col}"
    )


# ============================================================
# SAVE CHECK
# ============================================================

output = pd.DataFrame({

    "ACC_X": acc[ACC_X],
    "ACC_Y": acc[ACC_Y],
    "ACC_Z": acc[ACC_Z],
    "ACC_MAGNITUDE": acc_magnitude

})

output_path = (
    "data/processed/"
    "acceleration_frame_mapping_check.csv"
)

output.to_csv(
    output_path,
    index=False
)


print("\nRESULTS SAVED:")
print(output_path)

print(
    "\nACCELERATION FRAME MAPPING CHECK COMPLETE."
)