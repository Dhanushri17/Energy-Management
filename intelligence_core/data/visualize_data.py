import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# SOLAR INTELLIGENCE CORE
# DATA VISUALIZATION
# ============================================================

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Dataset
DATA_FILE = PROJECT_ROOT / "data" / "synthetic.csv"

# Folder to save plots
PLOT_DIR = PROJECT_ROOT / "data" / "plots"
PLOT_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 60)
print("LOADING SOLAR DATA")
print("=" * 60)

df = pd.read_csv(DATA_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

print(f"Dataset loaded successfully!")
print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")
print("Timestamp converted successfully.")


# ============================================================
# 2. IRRADIANCE vs AC POWER
# ============================================================

print("\nGenerating Plot 1: Irradiance vs AC Power...")

plt.figure(figsize=(10, 5))

plt.scatter(
    df["irradiance"],
    df["ac_power"],
    alpha=0.4
)

plt.xlabel("Irradiance")
plt.ylabel("AC Power")
plt.title("Irradiance vs Solar AC Power")

plt.grid(True)
plt.tight_layout()

plt.savefig(PLOT_DIR / "irradiance_vs_power.png", dpi=150)
plt.close()


# ============================================================
# 3. PANEL TEMPERATURE vs AC POWER
# ============================================================

print("Generating Plot 2: Panel Temperature vs AC Power...")

plt.figure(figsize=(10, 5))

plt.scatter(
    df["panel_temperature"],
    df["ac_power"],
    alpha=0.4
)

plt.xlabel("Panel Temperature")
plt.ylabel("AC Power")
plt.title("Panel Temperature vs Solar AC Power")

plt.grid(True)
plt.tight_layout()

plt.savefig(PLOT_DIR / "temperature_vs_power.png", dpi=150)
plt.close()


# ============================================================
# 4. AC POWER OVER TIME
# ============================================================

print("Generating Plot 3: AC Power Over Time...")

plt.figure(figsize=(12, 5))

plt.plot(
    df["timestamp"],
    df["ac_power"]
)

plt.xlabel("Time")
plt.ylabel("AC Power")
plt.title("Solar AC Power Over Time")

plt.xticks(rotation=45)

plt.grid(True)
plt.tight_layout()

plt.savefig(PLOT_DIR / "power_over_time.png", dpi=150)
plt.close()


# ============================================================
# 5. COMPLETION
# ============================================================

print("\n" + "=" * 60)
print("DATA VISUALIZATION COMPLETE")
print("=" * 60)

print(f"Plots saved to: {PLOT_DIR}")

print("\nGenerated files:")
print("1. irradiance_vs_power.png")
print("2. temperature_vs_power.png")
print("3. power_over_time.png")