# Problem statement

## The question
How much weight should someone give to a single hospital's published hip/knee replacement complication rate, given how many cases it is based on?

## Intended audience
Anyone comparing hospitals on public quality data: a patient, a referral coordinator, or a quality analyst without a statistics background.

## The decision it informs
Whether a published rate is meaningful evidence about a hospital, or whether it should be treated as roughly the average because it carries little hospital-specific information.

## What the data shows so far
- 1,706 of 4,790 hospitals have a reported rate.
- The rates vary much less between small hospitals than chance alone would produce, consistent with smoothing toward the average.
- Hospitals with more cases tend to have somewhat lower published rates.

## Assumptions (to be checked)
- Published rates are risk-standardized and smoothed. The data is consistent with this, but the method has not been confirmed in CMS documentation.
- The case-weighted average rate across reporting hospitals is a reasonable stand-in for the national rate. The national file has not yet been used.
- Hospitals without a reported rate are excluded, so findings describe reporting hospitals only.

## What success looks like
- A viewer can look up a hospital and see its rate next to its case count and a plain-language note about how much weight that rate deserves.
- Every claim in the app matches what the data supports. No rankings, and no "better" or "worse" labels the data cannot back up.
- The analysis reruns from the raw files with one command, and tests cover the cleaning and statistics code.

## What this project cannot answer
- Why hospitals differ, or whether any hospital is actually better.
- Patient-level risk. The data is aggregated by hospital.
- Anything that should guide clinical or purchasing decisions.

## Next steps
- Confirm the smoothing method and footnote definitions from CMS documentation.
- Build the interactive hospital lookup in Streamlit.
- Add unit tests.
- Bring in the national file and compare it with the case-weighted average.