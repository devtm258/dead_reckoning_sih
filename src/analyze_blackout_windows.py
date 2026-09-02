import pandas as pd

FILE = "data/processed/dead_reckoning_blackout_windows.csv"

df = pd.read_csv(FILE)

print("\nBLACKOUT WINDOW DIAGNOSTIC")
print("==========================")

print(f"\nTOTAL WINDOWS: {len(df)}")

print("\nDRIFT STATISTICS")
print("================")

print(
    df["DRIFT_PERCENT"].describe()
)

cols = [
    "START_TIME_S",
    "END_TIME_S",
    "DURATION_S",
    "GPS_PATH_DISTANCE_M",
    "DR_PATH_DISTANCE_M",
    "GPS_DISPLACEMENT_M",
    "DR_DISPLACEMENT_M",
    "ENDPOINT_ERROR_M",
    "DRIFT_PERCENT",
    "PASS_UNDER_10_PERCENT"
]

print("\nWORST 20 WINDOWS")
print("================")

print(
    df
    .sort_values(
        "DRIFT_PERCENT",
        ascending=False
    )
    .head(20)[cols]
    .to_string(index=False)
)

print("\nBEST 20 WINDOWS")
print("================")

print(
    df
    .sort_values(
        "DRIFT_PERCENT",
        ascending=True
    )
    .head(20)[cols]
    .to_string(index=False)
)

print("\nWINDOWS OVER 100% DRIFT")
print("=======================")

over_100 = df[
    df["DRIFT_PERCENT"] > 100
]

print(
    f"Count: {len(over_100)}"
)

if len(over_100) > 0:

    print(
        over_100[cols]
        .sort_values(
            "DRIFT_PERCENT",
            ascending=False
        )
        .head(30)
        .to_string(index=False)
    )

print("\nLOW-DISTANCE WINDOWS")
print("====================")

low_distance = df[
    df["GPS_PATH_DISTANCE_M"] < 10
]

print(
    f"Count: {len(low_distance)}"
)

if len(low_distance) > 0:

    print(
        low_distance[cols]
        .sort_values(
            "GPS_PATH_DISTANCE_M"
        )
        .head(30)
        .to_string(index=False)
    )

print("\nSUMMARY")
print("=======")

drift = df["DRIFT_PERCENT"]

print(
    f"Mean drift   : {drift.mean():.3f}%"
)

print(
    f"Median drift : {drift.median():.3f}%"
)

print(
    f"P90 drift    : {drift.quantile(0.90):.3f}%"
)

print(
    f"Worst drift  : {drift.max():.3f}%"
)

under_10 = (
    drift < 10
).sum()

between_10_25 = (
    (drift >= 10)
    &
    (drift < 25)
).sum()

between_25_50 = (
    (drift >= 25)
    &
    (drift < 50)
).sum()

between_50_100 = (
    (drift >= 50)
    &
    (drift < 100)
).sum()

over_100_count = (
    drift >= 100
).sum()

print(
    f"Under 10%    : {under_10}"
)

print(
    f"10-25%       : {between_10_25}"
)

print(
    f"25-50%       : {between_25_50}"
)

print(
    f"50-100%      : {between_50_100}"
)

print(
    f">100%        : {over_100_count}"
)

print(
    "\nBLACKOUT DIAGNOSTIC COMPLETE."
)