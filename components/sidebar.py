"""
components/sidebar.py
Global sidebar filters for KopiSeru Dashboard.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import MONTH_ORDER
from utils.icons import svg


def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Render the global sidebar and return a filters dict.
    The filters dict is keyed to match apply_filters() expectations.
    """
    # ── Sidebar CSS ────────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        /* Gradient — target div pertama yg diberi warna oleh Streamlit theme */
        section[data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #402218 0%, #6d4329 100%) !important;
            min-height: 100vh !important;
            box-shadow: inset -4px 0 12px rgba(0, 0, 0, 0.18) !important;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(200, 155, 109, 0.2) !important;
        }
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarNav"] {
            background: transparent !important;
        }

        /* All text in sidebar */
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] li {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stMultiSelect,
        section[data-testid="stSidebar"] [data-testid="stMultiSelect"],
        section[data-testid="stSidebar"] [data-testid="element-container"]:has([data-baseweb="select"]) {
            background-color: rgba(234, 230, 225, 0.40) !important;   
            border: 1px solid rgba(255, 255, 255, 0.22) !important;   
            border-radius: 10px !important;
            padding: 8px 10px 10px 10px !important;
            margin: 4px 0 8px 0 !important;
            box-shadow:
                0 6px 16px rgba(0, 0, 0, 0.25),
                0 0 0 1px rgba(212, 168, 83, 0.18) !important;
        }


        /* Expander filter group — sederhana, jarak konsisten, sedikit polish */
        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(200, 155, 109, 0.2) !important;
            border-radius: 10px !important;
            margin-bottom: 5px !important;
            transition: border-color 0.15s ease, background-color 0.15s ease;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"]:hover {
            border-color: rgba(212, 168, 83, 0.4) !important;
        }

        /* Header (summary) — default state, transparan, tanpa overlay putih bawaan */
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
            padding: 6px 10px !important;
            background-color: transparent !important;
            border-radius: 8px !important;
            transition: background-color 0.15s ease, border-color 0.15s ease;
        }
        /* Expander filter group — sederhana, jarak konsisten, sedikit polish */
        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(200, 155, 109, 0.2) !important;
            border-radius: 10px !important;
            margin-bottom: 5px !important;
            transition: border-color 0.15s ease, background-color 0.15s ease;
        }

        /* Header (summary) — default state, transparan, TANPA efek hover apapun */
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
            padding: 6px 10px !important;
            background-color: transparent !important;
            border-radius: 8px !important;
            transition: background-color 0.15s ease, border-color 0.15s ease;
        }

        /* Saat expander TERBUKA (active) — satu-satunya kondisi yang dapat outline emas */
        section[data-testid="stSidebar"] [data-testid="stExpander"][open] {
            border: 1.5px solid #D4A853 !important;
            background-color: rgba(212, 168, 83, 0.12) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"][open] summary {
            background-color: transparent !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"][open] summary p {
            color: #D4A853 !important;
            font-weight: 800 !important;
        }
        /* Saat expander terbuka (active) — border & tint emas persis seperti nav "Executive Summary" */
        section[data-testid="stSidebar"] [data-testid="stExpander"][open] {
            border: 1.5px solid #D4A853 !important;
            background-color: rgba(212, 168, 83, 0.12) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"][open] summary {
            background-color: transparent !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"][open] summary p {
            color: #D4A853 !important;
            font-weight: 800 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
            font-size: 12.5px !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em;
        }
        /* Ikon material di dalam expander/button — warna emas aksen, bukan putih polos */
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
        section[data-testid="stSidebar"] button [data-testid="stIconMaterial"] {
            color: #D4A853 !important;
        }
        /* Tombol Reset — outline emas permanen, sama seperti "Executive Summary" */
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: rgba(212, 168, 83, 0.12) !important;
            border: 1.5px solid #D4A853 !important;
            color: #D4A853 !important;
            font-size: 12.5px !important;
            font-weight: 800 !important;
            border-radius: 8px !important;
            transition: background-color 0.15s ease !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: rgba(212, 168, 83, 0.2) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
            padding: 2px 8px 8px 8px !important;
        }

        /* Filter labels */
        section[data-testid="stSidebar"] .stMultiSelect label,
        section[data-testid="stSidebar"] [data-testid="stMultiSelect"] label,
        section[data-testid="stSidebar"] [data-testid="element-container"]:has([data-baseweb="select"]) label {
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 12px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        section[data-testid="stSidebar"] .stMultiSelect label p,
        section[data-testid="stSidebar"] [data-testid="stMultiSelect"] label p,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
        }

        /* Select input box */
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(200, 155, 109, 0.3) !important;
            border-radius: 8px !important;
        }
        /* Ikon "Clear all" (x) dan dropdown arrow (chevron) di multiselect */
        section[data-testid="stSidebar"] [data-baseweb="select"] svg {
            fill: #6f4e37 !important;
            color: #6f4e37 !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="select"] [role="button"] svg {
            fill: #6f4e37 !important;
            color: #6f4e37 !important;
        }

        /* Placeholder / typed text */
        section[data-testid="stSidebar"] [data-baseweb="select"] input {
            color: #F5E6D3 !important;
        }

        /* Selected tags / chips */
        section[data-testid="stSidebar"] [data-baseweb="tag"] {
            background-color: #6f4e37 !important;
            border: none !important;
            border-radius: 6px !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            padding: 4px 6px 4px 10px !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="tag"] span {
            color: #ffffff !important;
            font-size: 12px !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="tag"] svg {
            display: inline-block !important;
            width: 14px !important;
            height: 14px !important;
            fill: #ffffff !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        /* Bungkus svg biasanya elemen terakhir di dalam tag — beri lingkaran
           background supaya kelihatan sebagai tombol klik, bukan cuma garis putih tipis */
        section[data-testid="stSidebar"] [data-baseweb="tag"] > *:last-child {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 16px !important;
            height: 16px !important;
            border-radius: 50% !important;
            background: rgba(255, 255, 255, 0.18) !important;
            cursor: pointer !important;
            opacity: 1 !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="tag"] > *:last-child:hover {
            background: rgba(255, 255, 255, 0.32) !important;
        }

        /* Divider / hr */
        section[data-testid="stSidebar"] hr {
            border-color: rgba(200, 155, 109, 0.25) !important;
        }

        /* Caption text */
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
            color: #ffffff !important;
        }

        /* Sidebar collapse/expand button */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            z-index: 999999 !important;
        }
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"] button {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            color: #C89B6D !important;
            background: rgba(200, 155, 109, 0.12) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(200, 155, 109, 0.28) !important;
        }
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="collapsedControl"] svg {
            color: #C89B6D !important;
            fill: #C89B6D !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Compute branch / city counts for the info box ──────────────────────
    n_branches = int(df["branch_id"].nunique()) if "branch_id" in df.columns else "—"
    n_cities   = int(df["branch_city"].nunique()) if "branch_city" in df.columns else "—"

    with st.sidebar:
        # ── Filters header ─────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="padding: 2px 0 6px 0;">
                <p style="font-size:13px; font-weight:700; color:#C89B6D;
                           letter-spacing:0.08em; text-transform:uppercase;
                           margin:0;">{svg("FILTER")} Filters</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Reset All Filters — state setup (tombolnya dipindah ke bawah,
        # di bawah section "Data Information") ─────────────────────────────
        _filter_bases = [
            "filter_year", "filter_month", "filter_city", "filter_branch_type",
            "filter_promo", "filter_weather", "filter_channel", "filter_day_type",
        ]
        if "filter_reset_counter" not in st.session_state:
            st.session_state["filter_reset_counter"] = 0

        _rc = st.session_state["filter_reset_counter"]

        # ── Date Filter (terbuka default) ───────────────────────────────
        with st.expander("Date Filter", expanded=True, icon=":material/calendar_month:"):
            years_avail = sorted(df["year"].unique().tolist())
            years_sel = st.multiselect(
                "Year",
                options=years_avail,
                default=years_avail,
                key=f"filter_year_{_rc}",
            )

            months_avail = sorted(df["month"].unique().tolist())
            month_labels = {m: MONTH_ORDER[m - 1] for m in months_avail}
            months_sel_labels = st.multiselect(
                "Month",
                options=list(month_labels.values()),
                default=list(month_labels.values()),
                key=f"filter_month_{_rc}",
            )
            label_to_int = {v: k for k, v in month_labels.items()}
            months_sel = [label_to_int[l] for l in months_sel_labels]

        # ── Location Filter ──────────────────────────────────────────────
        with st.expander("Location Filter", expanded=False, icon=":material/location_on:"):
            cities_avail = sorted(df["branch_city"].unique().tolist())
            cities_sel = st.multiselect(
                "City",
                options=cities_avail,
                default=cities_avail,
                key=f"filter_city_{_rc}",
            )

        # ── Branch Filter ────────────────────────────────────────────────
        with st.expander("Branch Filter", expanded=False, icon=":material/storefront:"):
            btypes_avail = sorted(df["branch_type"].unique().tolist())
            btypes_sel = st.multiselect(
                "Branch Type",
                options=btypes_avail,
                default=btypes_avail,
                key=f"filter_branch_type_{_rc}",
            )

        # ── Promotion Filter ─────────────────────────────────────────────
        with st.expander("Promotion Filter", expanded=False, icon=":material/campaign:"):
            promos_avail = sorted(df["promo_type"].unique().tolist())
            promos_sel = st.multiselect(
                "Promotion",
                options=promos_avail,
                default=promos_avail,
                key=f"filter_promo_{_rc}",
            )

        # ── Sales Channel ────────────────────────────────────────────────
        with st.expander("Sales Channel", expanded=False, icon=":material/local_shipping:"):
            channels_avail = ["Takeaway", "Delivery", "Dine-in"]
            channels_sel = st.multiselect(
                "Channel",
                options=channels_avail,
                default=channels_avail,
                key=f"filter_channel_{_rc}",
            )

        # ── Operational Condition ────────────────────────────────────────
        with st.expander("Operational Condition", expanded=False, icon=":material/cloud:"):
            weathers_avail = sorted(df["weather"].unique().tolist())
            weathers_sel = st.multiselect(
                "Weather",
                options=weathers_avail,
                default=weathers_avail,
                key=f"filter_weather_{_rc}",
            )

            day_types_avail = ["Weekday", "Weekend"]
            day_types_sel = st.multiselect(
                "Day Type",
                options=day_types_avail,
                default=day_types_avail,
                key=f"filter_day_type_{_rc}",
            )

        # ── Reset All Filters (dipindah ke atas, sebelum garis & info data) ──
        if st.button("Reset All Filters", use_container_width=True, key="btn_reset_filters"):
            old_rc = st.session_state["filter_reset_counter"]
            for base in _filter_bases:
                st.session_state.pop(f"{base}_{old_rc}", None)
            st.session_state["filter_reset_counter"] = old_rc + 1
            st.rerun()

        st.markdown("<hr style='margin: 10px 0 6px 0;'>", unsafe_allow_html=True)

        # ── Data Info (diperkecil, ringkas satu baris) ──────────────────────
        st.markdown(
            f"""
            <p style="font-size:10.5px; color:#D9C7B8; margin:0; line-height:1.6;">
                {svg("INSIGHT")} 2021–2023 · {svg("BRANCH")} {n_branches} branches · {svg("PIN")} {n_cities} cities
            </p>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:3px;'></div>", unsafe_allow_html=True)

    filters = {
        "years":        years_sel   or years_avail,
        "months":       months_sel  or months_avail,
        "cities":       cities_sel  or cities_avail,
        "branch_types": btypes_sel  or btypes_avail,
        "promotions":   promos_sel  or promos_avail,
        "weathers":     weathers_sel or weathers_avail,
        "channels":     channels_sel or channels_avail,
        "day_types":    day_types_sel or day_types_avail,
    }
    return filters