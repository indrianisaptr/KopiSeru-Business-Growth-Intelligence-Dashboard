"""
pages/4_😊_Customer_Insight.py
Customer Insight - Customer satisfaction and behavior analysis
Layout: kolom KPI sempit di kiri, grid chart di kanan.
Tombol "Explain" dipindah ke pojok kanan atas tiap chart (sejajar judul).
Mengikuti pola 1_Executive_Summary.py.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.icons import svg
from utils import (
    load_data, apply_filters, build_summary_stats,
    satisfaction_by_factor,
)
from utils.data_loader import COLORS
from components import (
    render_sidebar, section_header, metric_card, info_box,
    satisfaction_histogram,
    satisfaction_trend, satisfaction_weather_box,
    satisfaction_branch_box, satisfaction_promo_bar
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
sat_by_promo = satisfaction_by_factor(df, "promo_type")
best_type    = sat_by_type.iloc[0]
worst_type   = sat_by_type.iloc[-1]


def _chart_header(title: str, key: str, chart_title: str, chart_df, compact: bool = False) -> None:
    """Judul chart."""
    st.markdown(f"#### {title}")


# ── KPI: baris horizontal di atas ─────────────────────────────────────────
with st.container(key="kpicol_std"):
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
    # ── ROW 1: Satisfaction Distribution (full width, 1 chart) ─────────────
    with st.container(border=True, key="chartbox_sat_hist"):
        _chart_header("Satisfaction Distribution", "satisfaction_hist",
                      "Customer Satisfaction Distribution",
                      df[["customer_satisfaction"]])
        fig = satisfaction_histogram(df)
        fig.update_layout(title="", height=300,
                          margin=dict(l=34, r=10, t=34, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── ROW 2: Branch Type box | Promo bar | Weather box (3 charts) ────────
    r2c1, r2c2, r2c3 = st.columns(3, gap="small")
    with r2c1:
        with st.container(border=True, key="chartbox_sat_branch"):
            _chart_header("Satisfaction Distribution by Branch Type",
                          "satisfaction_branch_type",
                          "Satisfaction Distribution by Branch Type",
                          sat_by_type, compact=True)
            fig = satisfaction_branch_box(df)
            fig.update_layout(title="", height=220, showlegend=False,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color=COLORS["text"], size=10.5),
                              margin=dict(l=8, r=10, t=6, b=36),
                              yaxis=dict(title="Satisfaction Score", automargin=True),
                              xaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with r2c2:
        with st.container(border=True, key="chartbox_sat_promo"):
            _chart_header("Average Satisfaction by Promo Type",
                          "satisfaction_promo_type",
                          "Average Satisfaction by Promo Type",
                          sat_by_promo, compact=True)
            fig = satisfaction_promo_bar(sat_by_promo)
            fig.update_layout(title="", height=220, showlegend=False,
                              margin=dict(l=8, r=10, t=18, b=60),
                              yaxis=dict(range=[0, 5.4], dtick=1,
                                         title="Avg Satisfaction", automargin=True),
                              xaxis=dict(tickangle=-40, tickfont=dict(size=8),
                                         automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with r2c3:
        with st.container(border=True, key="chartbox_sat_weather"):
            _chart_header("Customer Satisfaction by Weather",
                          "satisfaction_weather",
                          "Customer Satisfaction by Weather", df, compact=True)
            fig = satisfaction_weather_box(df)
            fig.update_layout(title="", height=220, showlegend=False,
                              margin=dict(l=8, r=10, t=6, b=36),
                              yaxis=dict(title="Satisfaction Score", automargin=True),
                              xaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── ROW 3: Monthly Avg Customer Satisfaction Trend (full width) ────────
    with st.container(border=True, key="chartbox_sat_trend"):
        _chart_header("Monthly Average Customer Satisfaction Trend",
                      "satisfaction_trend",
                      "Monthly Average Customer Satisfaction Trend", df)
        fig = satisfaction_trend(df)
        fig.update_layout(title="", height=300,
                          margin=dict(l=34, r=95, t=10, b=45))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── BUSINESS HIGHLIGHTS: ringkasan statis, full width ──────────────────
    with st.container(border=True, key="sidepanel_insights"):
        st.markdown("#### Business Highlights")
        st.markdown(
            """
            <div style="font-size:11px; color:var(--text-muted); margin:-18px 0 18px 0; line-height:1.6;">
                Highlights what drives customer satisfaction and where it falls short, so
                the team can focus improvement efforts where they'll have the most impact.
            </div>
            """,
            unsafe_allow_html=True,
        )
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
            f'{svg("TARGET")} <b>Target:</b> Lift {avg_sat:.2f} to 4.2 via staff '
            "training + queue management",
            kind="warning",
        )