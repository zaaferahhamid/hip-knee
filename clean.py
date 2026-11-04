from pathlib import Path
import pandas as pd

data_folder = Path("data")
processed_folder = data_folder / "processed"
processed_folder.mkdir(exist_ok=True)  # makes data/processed if it doesn't exist yet

# Load both files. Reading Facility ID as text (str) protects leading zeros.
cjr = pd.read_csv(
    data_folder / "CJR_Quality_Reporting_January_2026_Production_File.csv",
    dtype={"Facility ID": str},
)
hospital = pd.read_csv(
    data_folder / "Complications_and_Deaths-Hospital.csv",
    dtype={"Facility ID": str},
)

# Pad every Facility ID to 6 digits so the two files can be matched.
cjr["Facility ID"] = cjr["Facility ID"].str.zfill(6)
hospital["Facility ID"] = hospital["Facility ID"].str.zfill(6)

# Keep only the hip/knee complication rows from the long hospital file.
hip_knee = hospital[hospital["Measure ID"] == "COMP_HIP_KNEE"].copy()

# Turn number-like text into real numbers. "Not Available" becomes NaN (empty).
for col in ["Denominator", "Score", "Lower Estimate", "Higher Estimate"]:
    hip_knee[col] = pd.to_numeric(hip_knee[col], errors="coerce")

# Turn percentile text like "53%" into the number 53.
for col in ["HCAHPS HLMR Percentile", "COMP-HIP-KNEE Percentile"]:
    cjr[col] = pd.to_numeric(cjr[col].str.rstrip("%"), errors="coerce")

# --- Quick checks: print what we ended up with ---
print("Hip/knee rows:", len(hip_knee))
print("Unique hospitals:", hip_knee["Facility ID"].nunique())
print("Rows with a score:", hip_knee["Score"].notna().sum())
print("Rows with an interval:", hip_knee["Lower Estimate"].notna().sum())

print("\nCompared to National values:")
print(hip_knee["Compared to National"].value_counts())

print("\nCase counts (Denominator):")
print(hip_knee["Denominator"].describe())

print("\nFootnotes on hip/knee rows:")
print(hip_knee["Footnote"].value_counts(dropna=False))

matched = cjr["Facility ID"].isin(hip_knee["Facility ID"])
print("\nCJR hospitals found in the hospital file:", matched.sum(), "of", len(cjr))

print("\nPRO column values (CJR file):")
print(cjr["PRO"].value_counts())

# Save cleaned copies so later scripts don't have to repeat the cleaning.
hip_knee.to_csv(processed_folder / "hip_knee_hospital.csv", index=False)
cjr.to_csv(processed_folder / "cjr_clean.csv", index=False)
print("\nSaved cleaned files to", processed_folder)