import pandas as pd
import numpy as np

file_path = "data/processed/imu_orientation_estimate.csv"

data = pd.read_csv(file_path)

print("ROWS:", len(data))
print("COLUMNS:", len(data.columns))

print("\nGRAVITY-BASED ROLL:")
print("Min:", data["GRAVITY_ROLL_DEG"].min())
print("Max:", data["GRAVITY_ROLL_DEG"].max())
print("Mean:", data["GRAVITY_ROLL_DEG"].mean())

print("\nGRAVITY-BASED PITCH:")
print("Min:", data["GRAVITY_PITCH_DEG"].min())
print("Max:", data["GRAVITY_PITCH_DEG"].max())
print("Mean:", data["GRAVITY_PITCH_DEG"].mean())

print("\nESTIMATED ROLL:")
print("Min:", data["ESTIMATED_ROLL_DEG"].min())
print("Max:", data["ESTIMATED_ROLL_DEG"].max())

print("\nESTIMATED PITCH:")
print("Min:", data["ESTIMATED_PITCH_DEG"].min())
print("Max:", data["ESTIMATED_PITCH_DEG"].max())

print("\nESTIMATED YAW:")
print("Min:", data["ESTIMATED_YAW_DEG"].min())
print("Max:", data["ESTIMATED_YAW_DEG"].max())