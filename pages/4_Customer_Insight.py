"""
pages/4_😊_Customer_Insight.py
Customer Insight - Customer satisfaction and behavior analysis
Layout: kolom KPI sempit di kiri, grid chart di kanan.
Tombol "Explain" dipindah ke pojok kanan atas tiap chart (sejajar judul).
Mengikuti pola 1_Executive_Summary.py.
"""

import streamlit as st
from utils.icons import svg
from utils import (
    load_data, apply_filters, build_summary_stats,
    satisfaction_by_factor, channel_distribution, channel_by_type,
    city_performance
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    satisfaction_histogram, satisfaction_by_factor_bar,
    satisfaction_trend, satisfaction_weather_box,
    channel_pie, channel_stacked_bar, delivery_share_city,
)
from components.cards import inject_compact_css

st.set_page_config(
    page_title="Customer Insight | KopiSeru BI",
    page_icon="",
    layout="wide",
)

inject_compact_css()

# ── Load & Filter data ────────────────────────────────────────────────────
with st.spinner("Loading KopiSeru data..."):
    raw_df = load_data()

filters = render_sidebar(raw_df)
df = apply_filters(raw_df, filters)

if df.empty:
    st.warning("No data matches the current filter selection. Please adjust the sidebar filters.")
    st.stop()

stats = build_summary_stats(df)

# ── Header ────────────────────────────────────────────────────────────────
section_header("Customer Insight",
               "Customer behavior, channel preferences, and satisfaction drivers")

# ── KPI calc ──────────────────────────────────────────────────────────────
sat_dist = df["customer_satisfaction"].value_counts().sort_index()
mode_sat = sat_dist.idxmax()
pct_high = len(df[df["customer_satisfaction"] >= 4.0]) / len(df) * 100
pct_low  = len(df[df["customer_satisfaction"] < 3.0]) / len(df) * 100
avg_sat  = stats["avg_satisfaction"]

# ── Aggregates (dipakai chart + panel insight) ────────────────────────────
sat_by_type  = satisfaction_by_factor(df, "branch_type")
sat_by_day   = satisfaction_by_factor(df, "day_type")
sat_by_promo = satisfaction_by_factor(df, "promo_label")
best_type    = sat_by_type.iloc[0]
worst_type   = sat_by_type.iloc[-1]

ch_df      = channel_distribution(df)
ch_type_df = channel_by_type(df)
city_df    = city_performance(df)


def _chart_header(title: str, key: str, chart_title: str, chart_df, compact: bool = False) -> None:
    """Judul chart."""
    st.markdown(f"#### {title}")


def _hlegend_top(fig):
    fig.update_layout(legend=dict(
        font=dict(size=9.5), orientation="h",
        yanchor="bottom", y=1.05, xanchor="center", x=0.5,
    ))


# ── KPI: baris horizontal di atas ─────────────────────────────────────────
with st.container(key="kpicol_main"):
    kpi_cols = st.columns(4, gap="small")
    with kpi_cols[0]:
        metric_card("Avg Satisfaction", f"{avg_sat:.2f} / 5.0", icon=svg("SMILE"))
    with kpi_cols[1]:
        metric_card("Mode Score", f"{mode_sat:.1f} / 5.0", icon=svg("TARGET"))
    with kpi_cols[2]:
        metric_card("High Satisfaction", f"{pct_high:.1f}%", icon=svg("THUMBUP"))
    with kpi_cols[3]:
        metric_card("At Risk (<3.0)", f"{pct_low:.1f}%", icon=svg("WARNING"))

st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)

if True:
    # ── HERO: Satisfaction Distribution (Customer Distribution) ────────────
    with st.container(border=True, key="chartbox_sat_hist"):
        _chart_header("Satisfaction Distribution", "satisfaction_hist",
                      "Customer Satisfaction Distribution",
                      df[["customer_satisfaction"]])
        fig = satisfaction_histogram(df)
        fig.update_layout(title="", height=320,
                          margin=dict(l=34, r=10, t=34, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SECONDARY: Satisfaction by Branch Type | Channel Distribution ──────
    r1c1, r1c2 = st.columns(2, gap="small")
    with r1c1:
        with st.container(border=True, key="chartbox_sat_branch"):
            _chart_header("Satisfaction by Branch Type", "satisfaction_branch_type",
                          "Satisfaction by Branch Type", sat_by_type, compact=True)
            fig = satisfaction_by_factor_bar(sat_by_type, "branch_type")
            fig.update_layout(title="", height=260, showlegend=False,
                              margin=dict(l=8, r=28, t=6, b=36),
                              xaxis=dict(automargin=True), yaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with r1c2:
        with st.container(border=True, key="chartbox_channel_dist"):
            _chart_header("Channel Distribution", "channel_distribution",
                          "Overall Channel Distribution", ch_df, compact=True)
            fig = channel_pie(ch_df)
            fig.update_traces(hole=0.32, textfont=dict(size=11))
            fig.update_layout(title="", height=260, margin=dict(l=4, r=4, t=6, b=34),
                              legend=dict(font=dict(size=9.5), orientation="h",
                                          yanchor="bottom", y=-0.22, xanchor="center", x=0.5))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SUPPORTING: Delivery Readiness by City (full width, lebih kecil) ───
    with st.container(border=True, key="chartbox_delivery_city"):
        _chart_header("Delivery Readiness by City", "delivery_readiness_city",
                      "Delivery Market Readiness by City", city_df)
        fig = delivery_share_city(city_df, df)
        fig.update_layout(title="", height=220, showlegend=False,
                          margin=dict(l=34, r=10, t=20, b=60),
                          xaxis=dict(automargin=True), yaxis=dict(automargin=True))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── BUSINESS HIGHLIGHTS: ringkasan statis, full width ──────────────────
    with st.container(border=True, key="sidepanel_insights"):
        st.markdown("#### Business Highlights")
        info_box(
            f'{svg("SMILE")} <b>Drivers:</b> {best_type["branch_type"]} tops '
            f'({best_type["avg_satisfaction"]:.2f}); atmosphere & service speed matter most',
            kind="success",
        )
        info_box(
            f'{svg("WARNING")} <b>No impact:</b> Weather, promo & weekday/weekend '
            "barely move satisfaction",
            kind="info",
        )
        info_box(
            f'{svg("TARGET")} <b>Target:</b> Lift {avg_sat:.2f} → 4.2 via staff '
            "training + queue management",
            kind="warning",
        )