# Hip/Knee Replacement Quality Monitor

An analysis project using public CMS hospital data to ask a simple question: **which hospitals' hip/knee replacement complication rates are meaningfully different from the national rate, and which just look different because of chance?**

**Status:** In progress. Data cleaning is done. The statistical analysis and web app are next.

## Why this question

Hospitals that perform few procedures produce noisy rates. A raw ranking can make a small hospital look like the best or worst in the country when the difference is mostly random variation. CMS accounts for this by labeling a hospital as better or worse than the national rate only when the entire 95% interval around its rate falls on one side of that rate. This project reproduces that idea and makes it visible, so a non-statistician can see how much to trust any single hospital's number.

## Data

All data is public and comes from the CMS Provider Data Catalog (data.cms.gov/provider-data). No patient-level information is used. Everything is hospital-level and aggregated.

| File | What it contains |
|---|---|
| `Complications_and_Deaths-Hospital.csv` | One row per hospital per measure. This project uses the hip/knee complication rows (`COMP_HIP_KNEE`), which include case counts, a rate, and a 95% interval. |
| `CJR_Quality_Reporting_January_2026_Production_File.csv` | The Comprehensive Care for Joint Replacement model file: 320 hospitals with a hip/knee complication rate, percentile ranks, and patient-survey scores. |

### Data notes

- **Facility IDs lose their leading zeros in one file.** The same hospital appears as `10023` in one file and `010023` in the other. IDs are read as text and padded to 6 digits before the files are matched.
- **The files cover different time windows.** In the files inspected, the CJR complication window and the hospital-file window do not line up, so their rates are not treated as the same measurement.
- **Missing values are stored as text.** Many cells say "Not Available" instead of being empty, so those columns are converted to numbers and the placeholders become true missing values.

## Project structure

```
hipKnee/
├── data/
│   ├── CJR_Quality_Reporting_January_2026_Production_File.csv
│   ├── Complications_and_Deaths-Hospital.csv
│   └── processed/          # cleaned copies created by clean.py
├── explore.py              # prints the structure of each raw file
├── clean.py                # cleans and saves the analysis-ready tables
├── requirements.txt
└── README.md
```

## How to run it

```bash
git clone https://github.com/zaaferahhamid/hip-knee.git
cd hip-knee
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python explore.py                # look at the raw files
python clean.py                  # create the cleaned files in data/processed/
```

## Planned analysis

- [x] Explore the raw files and document their structure
- [x] Clean the data and fix the Facility ID mismatch
- [ ] Write a one-page problem statement (decision supported, assumptions, how success is measured)
- [ ] Funnel plot of complication rates against case counts, with control limits around the national rate
- [ ] Check whether region or metro area explains differences between hospitals
- [ ] Compare snapshots over time and flag changes larger than chance would explain
- [ ] Unit tests for the cleaning and statistics code
- [ ] Interactive Streamlit app with a hospital lookup and plain-language explanations

## Limitations

- The data is aggregated, so it can show that hospitals differ but not why.
- Reported rates are already risk-standardized by CMS, but residual differences in patient mix could still exist.
- Hospitals with too few cases have no reported rate, so they cannot be assessed.
- This project is for learning and portfolio purposes and is not intended to guide clinical or purchasing decisions.

## Tech stack

Python, pandas, NumPy, SciPy, Matplotlib, DuckDB (SQL), Streamlit, pytest