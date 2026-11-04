import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("data/processed/hip_knee_hospital.csv", dtype={"Facility ID": str})
df["has_rate"] = df["Score"].notna()

# 1. Which footnotes go with hospitals that have / lack a rate?
print("Footnote vs. whether a rate was reported:")
print(pd.crosstab(df["Footnote"].fillna("none"), df["has_rate"]))

# 2. State level: does the share of reporting hospitals relate to the rate?
rated = df[df["has_rate"]].copy()
rated["weighted"] = rated["Score"] * rated["Denominator"]
state = rated.groupby("State").agg(
    weighted=("weighted", "sum"),
    cases=("Denominator", "sum"),
    reporting=("Score", "size"),
)
state["rate"] = state["weighted"] / state["cases"]
state["hospitals"] = df.groupby("State").size()
state["pct_reporting"] = 100 * state["reporting"] / state["hospitals"]
state = state[state["reporting"] >= 10]

for label, table in [("All states shown", state), ("Excluding PR", state.drop("PR", errors="ignore"))]:
    rho, p = stats.spearmanr(table["pct_reporting"], table["rate"])
    print(f"\n{label} (n={len(table)}): Spearman rho = {rho:.2f}, p = {p:.3f}")

# 3. Hospital level: do hospitals with more cases have lower rates?
rho, p = stats.spearmanr(rated["Denominator"], rated["Score"])
print(f"\nHospital level (n={len(rated)}): cases vs. rate, rho = {rho:.2f}, p = {p:.4f}")