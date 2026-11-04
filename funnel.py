from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the cleaned hip/knee table and keep hospitals that have a rate.
df = pd.read_csv("data/processed/hip_knee_hospital.csv", dtype={"Facility ID": str})
df = df.dropna(subset=["Score", "Denominator"]).copy()

df["rate"] = df["Score"] / 100  # percent -> proportion (3.8 becomes 0.038)

# Center line: average rate, weighted so hospitals with more cases count more.
pooled = np.average(df["rate"], weights=df["Denominator"])

# Standard error shrinks as cases grow: se = sqrt(p * (1 - p) / n)
df["se"] = np.sqrt(pooled * (1 - pooled) / df["Denominator"])
df["z"] = (df["rate"] - pooled) / df["se"]  # how many standard errors from center

# z of 1.96 is the 95% limit; 3.09 is the 99.8% limit.
for label, limit in [("95%", 1.96), ("99.8%", 3.09)]:
    high = (df["z"] > limit).sum()
    low = (df["z"] < -limit).sum()
    print(f"Outside {label} limits: {high} high, {low} low")

print("Hospitals plotted:", len(df))
print(f"Pooled rate: {pooled:.2%}")
print(f"Expected outside 95% by chance alone: about {0.05 * len(df):.0f}")

# Draw the funnel limits across the range of case counts.
n_grid = np.logspace(np.log10(25), np.log10(df["Denominator"].max()), 300)
se_grid = np.sqrt(pooled * (1 - pooled) / n_grid)

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df["Denominator"], df["rate"] * 100, s=10, alpha=0.5, label="Hospital")
ax.axhline(pooled * 100, color="black", label="Pooled rate")
ax.plot(n_grid, (pooled + 1.96 * se_grid) * 100, "--", color="orange", label="95% limits")
ax.plot(n_grid, (pooled - 1.96 * se_grid) * 100, "--", color="orange")
ax.plot(n_grid, (pooled + 3.09 * se_grid) * 100, ":", color="red", label="99.8% limits")
ax.plot(n_grid, (pooled - 3.09 * se_grid) * 100, ":", color="red")
ax.set_xscale("log")
ax.set_xlabel("Number of cases (log scale)")
ax.set_ylabel("Complication rate (%)")
ax.set_title("Hip/knee complication rate vs. number of cases")
ax.legend()

Path("outputs").mkdir(exist_ok=True)
fig.savefig("outputs/funnel_plot.png", dpi=150, bbox_inches="tight")
print("Saved outputs/funnel_plot.png")