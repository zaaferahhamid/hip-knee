import numpy as np
import pandas as pd

df = pd.read_csv("data/processed/hip_knee_hospital.csv", dtype={"Facility ID": str})
df = df.dropna(subset=["Score", "Denominator"]).copy()

df["rate"] = df["Score"] / 100
pooled = np.average(df["rate"], weights=df["Denominator"])

# Split hospitals into four equal-sized groups by number of cases.
df["size_group"] = pd.qcut(
    df["Denominator"], 4, labels=["Smallest", "Small-mid", "Large-mid", "Largest"]
)

# How much scatter would chance alone create for each hospital?
df["chance_se"] = np.sqrt(pooled * (1 - pooled) / df["Denominator"])

summary = df.groupby("size_group", observed=True).agg(
    hospitals=("rate", "size"),
    min_cases=("Denominator", "min"),
    max_cases=("Denominator", "max"),
    mean_rate_pct=("rate", lambda s: s.mean() * 100),
    observed_spread_pct=("rate", lambda s: s.std() * 100),
    chance_spread_pct=("chance_se", lambda s: np.sqrt((s**2).mean()) * 100),
)
summary["observed_vs_chance"] = (
    summary["observed_spread_pct"] / summary["chance_spread_pct"]
)

print(summary.round(2).to_string())
print("\nLowest rate:", round(df["rate"].min() * 100, 2), "%")
print("Highest rate:", round(df["rate"].max() * 100, 2), "%")