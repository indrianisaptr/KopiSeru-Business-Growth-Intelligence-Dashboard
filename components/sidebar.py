"""
components/sidebar.py
Global sidebar filters for KopiSeru Dashboard.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import COLORS, MONTH_ORDER


def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Render the global sidebar and return a filters dict.
    The filters dict is keyed to match apply_filters() expectations.
    """
    with st.sidebar:
        st.markdown(
            f"<p style='font-size:12px; color:{COLORS['text_muted']}; "
            "margin-bottom:4px;'><b>GLOBAL FILTERS</b></p>",
            unsafe_allow_html=True,
        )

        # ── Year ────────────────────────────────────────────────────────────
        years_avail = sorted(df["year"].unique().tolist())
        years_sel = st.multiselect(
            "Year",
            options=years_avail,
            default=years_avail,
            key="filter_year",
        )

        # ── Month ───────────────────────────────────────────────────────────
        months_avail = sorted(df["month"].unique().tolist())
        month_labels = {m: MONTH_ORDER[m - 1] for m in months_avail}
        months_sel_labels = st.multiselect(
            "Month",
            options=list(month_labels.values()),
            default=list(month_labels.values()),
            key="filter_month",
        )
        # convert labels back to int
        label_to_int = {v: k for k, v in month_labels.items()}
        months_sel = [label_to_int[l] for l in months_sel_labels]

        # ── City ────────────────────────────────────────────────────────────
        cities_avail = sorted(df["branch_city"].unique().tolist())
        cities_sel = st.multiselect(
            "City",
            options=cities_avail,
            default=cities_avail,
            key="filter_city",
        )

        # ── Branch Type ─────────────────────────────────────────────────────
        btypes_avail = sorted(df["branch_type"].unique().tolist())
        btypes_sel = st.multiselect(
            "Branch Type",
            options=btypes_avail,
            default=btypes_avail,
            key="filter_branch_type",
        )

        # ── Promotion ───────────────────────────────────────────────────────
        promos_avail = sorted(df["promo_type"].unique().tolist())
        promos_sel = st.multiselect(
            "Promotion",
            options=promos_avail,
            default=promos_avail,
            key="filter_promo",
        )

        # ── Weather ─────────────────────────────────────────────────────────
        weathers_avail = sorted(df["weather"].unique().tolist())
        weathers_sel = st.multiselect(
            "Weather",
            options=weathers_avail,
            default=weathers_avail,
            key="filter_weather",
        )

        # ── Channel ─────────────────────────────────────────────────────────
        channels_avail = ["Takeaway", "Delivery", "Dine-in"]
        channels_sel = st.multiselect(
            "Channel",
            options=channels_avail,
            default=channels_avail,
            key="filter_channel",
        )

        # ── Day Type ────────────────────────────────────────────────────────
        day_types_avail = ["Weekday", "Weekend"]
        day_types_sel = st.multiselect(
            "Day Type",
            options=day_types_avail,
            default=day_types_avail,
            key="filter_day_type",
        )

        st.markdown(
            "<hr style='border:1px solid #ccc; margin:16px 0 8px 0;'>",
            unsafe_allow_html=True,
        )
        st.caption("Data period: Jan 2021 – Dec 2023")
        st.caption("Source: KopiSeru Operational Data")

    filters = {
        "years":       years_sel       or years_avail,
        "months":      months_sel      or months_avail,
        "cities":      cities_sel      or cities_avail,
        "branch_types": btypes_sel     or btypes_avail,
        "promotions":  promos_sel      or promos_avail,
        "weathers":    weathers_sel    or weathers_avail,
        "channels":    channels_sel    or channels_avail,
        "day_types":   day_types_sel   or day_types_avail,
    }
    return filters