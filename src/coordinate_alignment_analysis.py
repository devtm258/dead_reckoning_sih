import pandas as pd
import numpy as np

from load_data import load_smartphone_data


# ============================================================
# LOAD DATA
# ============================================================

smartphone = load_smartphone_data()


# ============================================================
# DISPLAY AVAILABLE ORIENTATION COLUMNS
# ============================================================

print("SMARTPHONE ORIENTATION COLUMNS")
print("==============================")

orientation_columns = [
    column
    for column in smartphone.columns
    if "ORIENTATION" in column.upper()
]

for column in orientation_columns:
    print(column)


# ============================================================
# DISPLAY GRAVITY COLUMNS
# ============================================================

print("\n\nSMARTPHONE GRAVITY COLUMNS")
print("==========================")

gravity_columns = [
    column
    for column in smartphone.columns
    if "GRAVITY" in column.upper()
]

for column in gravity_columns:
    print(column)


# ============================================================
# DISPLAY FIRST 20 ORIENTATION VALUES
# ============================================================

print("\n\nFIRST 20 ORIENTATION VALUES")
print("===========================")

print(
    smartphone[
        orientation_columns
    ].head(20).to_string(index=False)
)


# ============================================================
# ORIENTATION SUMMARY
# ============================================================

print("\n\nORIENTATION SUMMARY")
print("===================")

print(
    smartphone[
        orientation_columns
    ].describe().to_string()
)


# ============================================================
# GRAVITY SUMMARY
# ============================================================

print("\n\nGRAVITY SUMMARY")
print("===============")

print(
    smartphone[
        gravity_columns
    ].describe().to_string()
)


# ============================================================
# GRAVITY MEAN
# ============================================================

print("\n\nGRAVITY MEANS")
print("=============")

for column in gravity_columns:
    print(
        f"{column}: "
        f"{smartphone[column].mean():.6f}"
    )


# ============================================================
# GRAVITY STANDARD DEVIATION
# ============================================================

print("\n\nGRAVITY STANDARD DEVIATIONS")
print("===========================")

for column in gravity_columns:
    print(
        f"{column}: "
        f"{smartphone[column].std():.6f}"
    )