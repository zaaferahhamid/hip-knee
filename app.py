from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "processed" / "hip_knee_hospital.csv"
FUNNEL_IMAGE = Path(__file__).parent / "outputs" / "funnel_plot.png"
SIZE_LABELS = ["Smallest", "Small-mid", "Large-mid", "Largest"]

st.set_page_config(page_title="Hip/Knee Rate Reliability", layout="wide")


@st.cache_data
def load_data():
    """Load the cleaned hip/knee table and build everything the app needs."""
    df = pd.read_csv(DATA_FILE, dtype={"Facility ID": str})
    df["has_rate"] = df["Score"].notna()

    # Footnotes are stored as numbers like 5.0; turn them into plain text like "5".
    footnote = pd.to_numeric(df["Footnote"], errors="coerce")
    df["footnote_code"] = footnote.astype("Int64").astype("string").fillna("none")

    # A readable label for the hospital drop-down.
    df["label"] = (
        df["Facility Name"].str.title()
        + " - "
        + df["City/Town"].str.title()
        + ", "
        + df["State"]
        + " ("
        + df["Facility ID"]
        + ")"
    )

    # Only hospitals with a published rate go into the statistics.
    rated = df[df["has_rate"]].copy()
    rated["rate"] = rated["Score"] / 100
    pooled = np.average(rated["rate"], weights=rated["Denominator"])

    # Four equal-sized groups by number of cases.
    rated["size_group"] = pd.qcut(rated["Denominator"], 4, labels=SIZE_LABELS)

    # Scatter that chance alone would create if rates were raw proportions.
    rated["chance_se"] = np.sqrt(pooled * (1 - pooled) / rated["Denominator"])

    summary = rated.groupby("size_group", observed=True).agg(
        hospitals=("rate", "size"),
        min_cases=("Denominator", "min"),
        max_cases=("Denominator", "max"),
        median_rate=("rate", lambda s: s.median() * 100),
        p10=("rate", lambda s: s.quantile(0.10) * 100),
        p90=("rate", lambda s: s.quantile(0.90) * 100),
        real_spread=("rate", lambda s: s.std() * 100),
        chance_spread=("chance_se", lambda s: np.sqrt((s**2).mean()) * 100),
    )
    summary["ratio"] = summary["real_spread"] / summary["chance_spread"]

    period = f"{df['Start Date'].mode()[0]} to {df['End Date'].mode()[0]}"
    return df, rated, pooled, summary, period


def lookup_chart(rated, pooled, selected_id):
    """Every reporting hospital as a dot, with the chosen hospital highlighted."""
    n_grid = np.logspace(
        np.log10(rated["Denominator"].min()),
        np.log10(rated["Denominator"].max()),
        300,
    )
    se_grid = np.sqrt(pooled * (1 - pooled) / n_grid)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(
        rated["Denominator"], rated["Score"], s=8, alpha=0.35, color="gray",
        label="Reporting hospitals",
    )
    ax.fill_between(
        n_grid,
        (pooled - 1.96 * se_grid) * 100,
        (pooled + 1.96 * se_grid) * 100,
        alpha=0.15,
        color="orange",
        label="Range chance alone would produce (95%),\nif rates were not smoothed",
    )
    ax.axhline(
        pooled * 100, color="black", linewidth=1,
        label="Average across reporting hospitals",
    )
    chosen = rated[rated["Facility ID"] == selected_id]
    ax.scatter(
        chosen["Denominator"], chosen["Score"], s=90, color="crimson",
        zorder=5, label="Selected hospital",
    )
    ax.set_xscale("log")
    ax.set_xlabel("Number of cases (log scale)")
    ax.set_ylabel("Published complication rate (%)")
    ax.legend(fontsize=8)
    return fig


def render_lookup(df, rated, pooled, summary):
    st.subheader("Look up a hospital")

    col_state, col_filter = st.columns([1, 2])
    states = ["All states"] + sorted(df["State"].unique())
    state = col_state.selectbox("State", states)
    only_rated = col_filter.checkbox(
        "Only show hospitals with a published rate", value=True
    )

    options = df
    if state != "All states":
        options = options[options["State"] == state]
    if only_rated:
        options = options[options["has_rate"]]
    options = options.sort_values("label")

    if options.empty:
        st.info("No hospitals match those choices.")
        return

    choice = st.selectbox("Hospital", options["label"].tolist())
    hospital = options[options["label"] == choice].iloc[0]

    st.markdown(f"### {hospital['Facility Name'].title()}")
    st.caption(f"{hospital['City/Town'].title()}, {hospital['State']}")

    if not hospital["has_rate"]:
        st.warning("No complication rate is published for this hospital.")
        st.write(
            f"In the data, this hospital carries footnote code "
            f"**{hospital['footnote_code']}**. Codes 1, 5, 7, and 19 appear only on "
            "hospitals with no published rate, but their exact meanings have not "
            "been confirmed from the CMS data dictionary. A description of the CMS "
            "data says rates are not publicly reported for hospitals with fewer "
            "than 25 eligible cases."
        )
        return

    rate = hospital["Score"]
    cases = int(hospital["Denominator"])
    group = rated.loc[rated["Facility ID"] == hospital["Facility ID"], "size_group"].iloc[0]
    stats = summary.loc[group]

    c1, c2, c3 = st.columns(3)
    c1.metric("Published complication rate", f"{rate:.1f}%")
    c2.metric("Cases behind the rate", f"{cases:,}")
    c3.metric("Average across reporting hospitals", f"{pooled * 100:.2f}%")

    st.markdown("#### How much weight does this number deserve?")
    st.write(
        f"This rate is based on {cases:,} cases, which puts the hospital in the "
        f"**{group.lower()}** quarter of reporting hospitals by case count "
        f"({int(stats['min_cases']):,} to {int(stats['max_cases']):,} cases). "
        f"In that group, the middle 80% of published rates fall between "
        f"{stats['p10']:.1f}% and {stats['p90']:.1f}%."
    )

    if stats["ratio"] < 0.5:
        st.write(
            "Rates in this group are much more tightly bunched than chance alone "
            "would produce if they were raw proportions. That is what you would "
            "expect if rates for hospitals with few cases are pulled toward the "
            "average (a hypothesis, not yet confirmed). On its own, a rate like "
            "this is weak evidence about this specific hospital."
        )
    else:
        st.write(
            "Rates in this group are less tightly bunched, but they still vary "
            "less than chance alone would produce if they were raw proportions. "
            "Differences from the average should still be read cautiously."
        )

    st.caption(
        "This tool does not rank hospitals or label any hospital better or worse. "
        "The data cannot show that."
    )

    fig = lookup_chart(rated, pooled, hospital["Facility ID"])
    st.pyplot(fig)
    plt.close(fig)


def render_reliability(rated, pooled, summary):
    st.subheader("How reliable are published rates for small hospitals?")
    st.write(
        "If published rates were raw proportions, hospitals with few cases would "
        "scatter widely by chance, and big hospitals would scatter much less. "
        "The table compares the real spread of published rates with the spread "
        "chance alone would create, by hospital size."
    )

    table = summary.rename(
        columns={
            "hospitals": "Hospitals",
            "min_cases": "Min cases",
            "max_cases": "Max cases",
            "median_rate": "Median rate (%)",
            "p10": "10th percentile (%)",
            "p90": "90th percentile (%)",
            "real_spread": "Real spread (pts)",
            "chance_spread": "Chance-only spread (pts)",
            "ratio": "Real / chance",
        }
    ).round(2)
    st.dataframe(table, use_container_width=True)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    x = np.arange(len(summary))
    ax.bar(x - 0.2, summary["real_spread"], width=0.4, label="Real spread of published rates")
    ax.bar(x + 0.2, summary["chance_spread"], width=0.4, label="Spread chance alone would create")
    ax.set_xticks(x)
    ax.set_xticklabels(summary.index.astype(str))
    ax.set_xlabel("Hospital size group (by number of cases)")
    ax.set_ylabel("Spread (percentage points)")
    ax.legend(fontsize=8)
    st.pyplot(fig)
    plt.close(fig)

    st.write(
        "The real spread barely changes with hospital size, while the chance-only "
        "spread falls sharply. This is consistent with CMS risk-standardized rates "
        "being pulled toward the average for small hospitals. The mechanism has "
        "not been confirmed against CMS methodology documents."
    )

    if FUNNEL_IMAGE.exists():
        st.image(
            str(FUNNEL_IMAGE),
            caption="Funnel plot: most hospitals sit well inside the limits chance would predict.",
        )


def render_about(df, rated, period):
    st.subheader("About this project")
    st.markdown(
        f"""
**Data.** Public CMS hospital data (data.cms.gov/provider-data), hospital-level only.
No patient information. The hip/knee complication measure covers **{period}**.

**Coverage.** {len(rated):,} of {len(df):,} hospitals ({len(rated) / len(df):.0%}) have a
published rate. Hospitals without one are not shown in the statistics.

**What this tool can say.** How many cases sit behind a published rate, and how much
weight a rate from a hospital of that size seems to deserve.

**What it cannot say.** Why hospitals differ, whether any hospital is better or worse,
or anything about an individual patient's risk.

**Still unconfirmed.** The smoothing method and the meaning of each footnote code.

**Not for clinical or purchasing decisions.** This is a learning and portfolio project.
"""
    )


st.title("Hip/Knee Replacement Rate Reliability")
st.write(
    "How much weight should you give a single hospital's published complication "
    "rate, given how many cases it is based on?"
)

if not DATA_FILE.exists():
    st.error(
        "Cleaned data not found. Run `python clean.py` first to create "
        "`data/processed/hip_knee_hospital.csv`."
    )
else:
    df, rated, pooled, summary, period = load_data()
    tab_lookup, tab_reliability, tab_about = st.tabs(
        ["Hospital lookup", "How reliable are the rates?", "About"]
    )
    with tab_lookup:
        render_lookup(df, rated, pooled, summary)
    with tab_reliability:
        render_reliability(rated, pooled, summary)
    with tab_about:
        render_about(df, rated, period)
        