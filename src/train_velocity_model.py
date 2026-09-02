import os
import pickle

import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from load_data import load_smartphone_data, load_vbox_data


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_FILE = (
    "data/processed/"
    "dr_velocity_model.pkl"
)

PARAMETERS_FILE = (
    "data/processed/"
    "dr_velocity_model_parameters.csv"
)

WINDOW = 20


# ============================================================
# FEATURE ENGINEERING
#
# EXACTLY 53 FEATURES
#
# 45 raw sensor statistics
# 4 linear acceleration magnitude statistics
# 4 gyroscope magnitude statistics
#
# TOTAL = 53
# ============================================================

def make_features(accel, gyro, gravity):

    features = []

    # --------------------------------------------------------
    # RAW SENSOR STATISTICS
    # --------------------------------------------------------

    for arr in (
        accel,
        gyro,
        gravity
    ):

        for axis in range(3):

            v = arr[:, axis]

            features.extend([

                np.mean(v),

                np.std(v),

                np.min(v),

                np.max(v),

                np.mean(
                    np.abs(v)
                )

            ])

    # --------------------------------------------------------
    # LINEAR ACCELERATION
    # --------------------------------------------------------

    linear = (
        accel
        -
        gravity
    )

    linear_mag = np.linalg.norm(
        linear,
        axis=1
    )

    # --------------------------------------------------------
    # GYROSCOPE MAGNITUDE
    # --------------------------------------------------------

    gyro_mag = np.linalg.norm(
        gyro,
        axis=1
    )

    # --------------------------------------------------------
    # LINEAR ACCELERATION MAGNITUDE
    # --------------------------------------------------------

    features.extend([

        np.mean(
            linear_mag
        ),

        np.std(
            linear_mag
        ),

        np.min(
            linear_mag
        ),

        np.max(
            linear_mag
        )

    ])

    # --------------------------------------------------------
    # GYROSCOPE MAGNITUDE
    # --------------------------------------------------------

    features.extend([

        np.mean(
            gyro_mag
        ),

        np.std(
            gyro_mag
        ),

        np.min(
            gyro_mag
        ),

        np.max(
            gyro_mag
        )

    ])

    result = np.asarray(
        features,
        dtype=np.float32
    )

    if len(result) != 53:

        raise ValueError(
            f"Feature generation error: "
            f"expected 53, got {len(result)}"
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\nTRAINING OFFLINE VELOCITY MODEL"
    )

    print(
        "================================"
    )

    print(
        "DATASET: IOVNB - DRIVER A"
    )

    # ========================================================
    # LOAD DATA
    # ========================================================

    smartphone = (
        load_smartphone_data()
    )

    vbox = (
        load_vbox_data()
    )

    print(
        f"\nSMARTPHONE SAMPLES: "
        f"{len(smartphone)}"
    )

    print(
        f"VBOX SAMPLES      : "
        f"{len(vbox)}"
    )

    if len(smartphone) != len(vbox):

        raise ValueError(
            "Smartphone and VBOX datasets "
            "have different sample counts."
        )

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    smartphone_columns = [

        "ACCELEROMETER X (m/s²)",
        "ACCELEROMETER Y (m/s²)",
        "ACCELEROMETER Z (m/s²)",

        "GRAVITY X (m/s²)",
        "GRAVITY Y (m/s²)",
        "GRAVITY Z (m/s²)",

        "GYROSCOPE Yaw (rad/s)",
        "GYROSCOPE Pitch (rad/s)",
        "GYROSCOPE Roll (rad/s)"

    ]

    vbox_columns = [

        "Velocity (km/hr)",

        "Indicated Vehicle Speed (km/hr)",

        "Wheel Speed Front Left (rad/sec)",
        "Wheel Speed Front Right (rad/sec)",

        "Wheel Speed Rear Left (rad/sec)",
        "Wheel Speed Rear Right (rad/sec)"

    ]

    # ========================================================
    # CHECK COLUMNS
    # ========================================================

    missing_smartphone = [

        c
        for c in smartphone_columns
        if c not in smartphone.columns

    ]

    if missing_smartphone:

        raise ValueError(
            "\nMissing smartphone columns:\n"
            +
            "\n".join(
                missing_smartphone
            )
        )

    missing_vbox = [

        c
        for c in vbox_columns
        if c not in vbox.columns

    ]

    if missing_vbox:

        raise ValueError(
            "\nMissing VBOX columns:\n"
            +
            "\n".join(
                missing_vbox
            )
        )

    # ========================================================
    # SMARTPHONE SENSOR ARRAYS
    # ========================================================

    accel = smartphone[

        [
            "ACCELEROMETER X (m/s²)",
            "ACCELEROMETER Y (m/s²)",
            "ACCELEROMETER Z (m/s²)"
        ]

    ].apply(
        pd.to_numeric,
        errors="coerce"
    ).to_numpy(
        dtype=float
    )

    gravity = smartphone[

        [
            "GRAVITY X (m/s²)",
            "GRAVITY Y (m/s²)",
            "GRAVITY Z (m/s²)"
        ]

    ].apply(
        pd.to_numeric,
        errors="coerce"
    ).to_numpy(
        dtype=float
    )

    gyro = smartphone[

        [
            "GYROSCOPE Yaw (rad/s)",
            "GYROSCOPE Pitch (rad/s)",
            "GYROSCOPE Roll (rad/s)"
        ]

    ].apply(
        pd.to_numeric,
        errors="coerce"
    ).to_numpy(
        dtype=float
    )

    # ========================================================
    # VBOX DATA
    # ========================================================

    velocity = pd.to_numeric(

        vbox[
            "Velocity (km/hr)"
        ],

        errors="coerce"

    ).to_numpy(
        dtype=float
    )

    indicated = pd.to_numeric(

        vbox[
            "Indicated Vehicle Speed (km/hr)"
        ],

        errors="coerce"

    ).to_numpy(
        dtype=float
    )

    wheel_fl = pd.to_numeric(

        vbox[
            "Wheel Speed Front Left (rad/sec)"
        ],

        errors="coerce"

    ).to_numpy(
        dtype=float
    )

    wheel_fr = pd.to_numeric(

        vbox[
            "Wheel Speed Front Right (rad/sec)"
        ],

        errors="coerce"

    ).to_numpy(
        dtype=float
    )

    wheel_rl = pd.to_numeric(

        vbox[
            "Wheel Speed Rear Left (rad/sec)"
        ],

        errors="coerce"

    ).to_numpy(
        dtype=float
    )

    wheel_rr = pd.to_numeric(

        vbox[
            "Wheel Speed Rear Right (rad/sec)"
        ],

        errors="coerce"

    ).to_numpy(
        dtype=float
    )

    # ========================================================
    # VBOX WHEEL SPEED
    # ========================================================

    wheel_matrix = np.column_stack([

        wheel_fl,
        wheel_fr,
        wheel_rl,
        wheel_rr

    ])

    wheel_mean = np.nanmean(

        wheel_matrix,

        axis=1

    )

    # ========================================================
    # VBOX TARGET CLEANING
    # ========================================================

    velocity_wheel_difference = (

        velocity
        -
        wheel_mean

    )

    velocity_indicated_difference = (

        velocity
        -
        indicated

    )

    suspicious = (

        (
            np.abs(
                velocity_wheel_difference
            )
            >
            5.0
        )

        |

        (
            np.abs(
                velocity_indicated_difference
            )
            >
            5.0
        )

    )

    suspicious_count = int(

        np.sum(
            suspicious
        )

    )

    suspicious_percent = (

        suspicious_count
        /
        len(vbox)
        *
        100.0

    )

    print(
        "\nVBOX TARGET CLEANING"
    )

    print(
        "===================="
    )

    print(
        f"Suspicious samples : "
        f"{suspicious_count}"
    )

    print(
        f"Suspicious percent  : "
        f"{suspicious_percent:.4f}%"
    )

    # ========================================================
    # TARGET
    #
    # Use VBOX Velocity as the training target.
    #
    # Suspicious samples are excluded.
    # ========================================================

    target_speed = (

        velocity
        /
        3.6

    )

    # ========================================================
    # VALID DATA
    # ========================================================

    valid_sensor = (

        np.all(
            np.isfinite(
                accel
            ),
            axis=1
        )

        &

        np.all(
            np.isfinite(
                gyro
            ),
            axis=1
        )

        &

        np.all(
            np.isfinite(
                gravity
            ),
            axis=1
        )

        &

        np.isfinite(
            target_speed
        )

        &

        ~suspicious

    )

    # ========================================================
    # BUILD WINDOWS
    # ========================================================

    print(
        "\nBUILDING TRAINING FEATURES..."
    )

    feature_rows = []

    target_rows = []

    for i in range(

        WINDOW - 1,

        len(smartphone)

    ):

        start = (

            i
            -
            WINDOW
            +
            1

        )

        indices = np.arange(

            start,

            i + 1

        )

        if not np.all(
            valid_sensor[
                indices
            ]
        ):

            continue

        features = make_features(

            accel[
                start:i + 1
            ],

            gyro[
                start:i + 1
            ],

            gravity[
                start:i + 1
            ]

        )

        feature_rows.append(
            features
        )

        target_rows.append(
            target_speed[i]
        )

    X = np.asarray(

        feature_rows,

        dtype=np.float32

    )

    y = np.asarray(

        target_rows,

        dtype=np.float32

    )

    print(
        f"VALID TRAINING WINDOWS: "
        f"{len(X)}"
    )

    print(
        f"FEATURE COUNT: "
        f"{X.shape[1]}"
    )

    # ========================================================
    # FEATURE CHECK
    # ========================================================

    if X.shape[1] != 53:

        raise ValueError(

            "\nFEATURE MISMATCH!\n"
            f"Expected: 53\n"
            f"Created : {X.shape[1]}"

        )

    # ========================================================
    # TIME-ORDERED SPLIT
    # ========================================================

    split_index = int(

        len(X)
        *
        0.75

    )

    X_train = X[
        :split_index
    ]

    y_train = y[
        :split_index
    ]

    X_test = X[
        split_index:
    ]

    y_test = y[
        split_index:
    ]

    print(
        f"\nTRAIN WINDOWS: "
        f"{len(X_train)}"
    )

    print(
        f"TEST WINDOWS : "
        f"{len(X_test)}"
    )

    # ========================================================
    # EXTRA TREES MODEL
    #
    # Designed to reduce variance and improve nonlinear
    # regression over the previous Random Forest.
    # ========================================================

    print(
        "\nTRAINING EXTRA TREES VELOCITY MODEL..."
    )

    model = ExtraTreesRegressor(

        n_estimators=300,

        max_depth=24,

        min_samples_leaf=2,

        max_features=1.0,

        n_jobs=-1,

        random_state=42

    )

    model.fit(

        X_train,

        y_train

    )

    # ========================================================
    # TEST PREDICTION
    # ========================================================

    prediction = model.predict(

        X_test

    )

    prediction = np.asarray(

        prediction,

        dtype=float

    )

    # ========================================================
    # METRICS
    # ========================================================

    mae = mean_absolute_error(

        y_test,

        prediction

    )

    rmse = np.sqrt(

        mean_squared_error(

            y_test,

            prediction

        )

    )

    absolute_error = np.abs(

        prediction
        -
        y_test

    )

    median_absolute_error = np.median(

        absolute_error

    )

    p90_absolute_error = np.percentile(

        absolute_error,

        90

    )

    p95_absolute_error = np.percentile(

        absolute_error,

        95

    )

    # ========================================================
    # TARGET STATISTICS
    # ========================================================

    target_mean = np.mean(
        y
    )

    target_std = np.std(
        y
    )

    target_min = np.min(
        y
    )

    target_max = np.max(
        y
    )

    # ========================================================
    # RESULTS
    # ========================================================

    print(
        "\nVELOCITY MODEL PERFORMANCE"
    )

    print(
        "=========================="
    )

    print(
        f"MAE  : "
        f"{mae:.6f} m/s"
    )

    print(
        f"RMSE : "
        f"{rmse:.6f} m/s"
    )

    print(
        f"Median absolute error : "
        f"{median_absolute_error:.6f} m/s"
    )

    print(
        f"P90 absolute error   : "
        f"{p90_absolute_error:.6f} m/s"
    )

    print(
        f"P95 absolute error   : "
        f"{p95_absolute_error:.6f} m/s"
    )

    # ========================================================
    # TARGET STATISTICS
    # ========================================================

    print(
        "\nCLEAN VBOX TARGET"
    )

    print(
        "================="
    )

    print(
        f"Mean : "
        f"{target_mean:.6f} m/s"
    )

    print(
        f"Std  : "
        f"{target_std:.6f} m/s"
    )

    print(
        f"Min  : "
        f"{target_min:.6f} m/s"
    )

    print(
        f"Max  : "
        f"{target_max:.6f} m/s"
    )

    # ========================================================
    # OUTPUT DIRECTORY
    # ========================================================

    os.makedirs(

        "data/processed",

        exist_ok=True

    )

    # ========================================================
    # MODEL BUNDLE
    # ========================================================

    bundle = {

        "model":
            model,

        "window":
            WINDOW,

        "feature_count":
            int(X.shape[1]),

        "feature_version":
            "53",

        "target":
            "VBOX VELOCITY (km/hr)",

        "target_units":
            "m/s",

        "dataset":
            "IOVNB",

        "driver":
            "A",

        "model_type":
            "ExtraTreesRegressor",

        "n_estimators":
            300,

        "max_depth":
            24,

        "min_samples_leaf":
            2,

        "max_features":
            1.0,

        "random_state":
            42,

        "test_mae":
            float(mae),

        "test_rmse":
            float(rmse)

    }

    # ========================================================
    # SAVE MODEL
    # ========================================================

    with open(

        MODEL_FILE,

        "wb"

    ) as f:

        pickle.dump(

            bundle,

            f

        )

    # ========================================================
    # SAVE PARAMETERS
    # ========================================================

    parameters = pd.DataFrame({

        "PARAMETER": [

            "DATASET",
            "DRIVER",
            "WINDOW",
            "FEATURE_COUNT",
            "FEATURE_VERSION",

            "MODEL",
            "N_ESTIMATORS",
            "MAX_DEPTH",
            "MIN_SAMPLES_LEAF",
            "MAX_FEATURES",
            "RANDOM_STATE",

            "TRAIN_WINDOWS",
            "TEST_WINDOWS",

            "SUSPICIOUS_VBOX_SAMPLES",
            "SUSPICIOUS_VBOX_PERCENT",

            "TARGET_MEAN_MS",
            "TARGET_STD_MS",
            "TARGET_MIN_MS",
            "TARGET_MAX_MS",

            "TEST_MAE_MS",
            "TEST_RMSE_MS",

            "TEST_MEDIAN_ABSOLUTE_ERROR_MS",
            "TEST_P90_ABSOLUTE_ERROR_MS",
            "TEST_P95_ABSOLUTE_ERROR_MS"

        ],

        "VALUE": [

            "IOVNB",
            "A",
            WINDOW,
            int(X.shape[1]),
            "53",

            "ExtraTreesRegressor",
            300,
            24,
            2,
            1.0,
            42,

            len(X_train),
            len(X_test),

            suspicious_count,
            suspicious_percent,

            target_mean,
            target_std,
            target_min,
            target_max,

            mae,
            rmse,

            median_absolute_error,
            p90_absolute_error,
            p95_absolute_error

        ]

    })

    parameters.to_csv(

        PARAMETERS_FILE,

        index=False

    )

    # ========================================================
    # FINAL
    # ========================================================

    print(
        "\nMODEL SAVED:"
    )

    print(
        MODEL_FILE
    )

    print(
        PARAMETERS_FILE
    )

    print(
        "\nTRAINING COMPLETE."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()