"""
pages/3_🏪_Branch_Performance_&_Expansion.py
Branch Performance & Expansion Strategy
Layout: kolom KPI sempit di kiri, grid chart di kanan.
Tombol "Explain" dipindah ke pojok kanan atas tiap chart (sejajar judul).
Mengikuti pola 1_Executive_Summary.py.
"""

import streamlit as st
from utils.icons import svg
from utils import (
    load_data, apply_filters, build_summary_stats,
    city_performance, branch_type_performance,
    expansion_score, channel_by_type
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    fmt_currency,
    city_profit_bar, branch_type_margin_bar, city_bubble,
    expansion_bar, channel_stacked_bar, delivery_share_city,
)
from components.cards import inject_compact_css

st.set_page_config(
    page_title="Branch Performance & Expansion | KopiSeru BI",
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
section_header("Branch Performance & Expansion Strategy",
               "Evaluate branch performance and identify expansion opportunities")

# ── Aggregates (dipakai chart, tabel & panel insight) ─────────────────────
bt_df        = branch_type_performance(df)
city_df      = city_performance(df)
expansion_df = expansion_score(df)
ch_type_df   = channel_by_type(df)

best_type  = bt_df.nlargest(1, "avg_profit_margin").iloc[0]
worst_type = bt_df.nsmallest(1, "avg_profit_margin").iloc[0]
top1 = expansion_df.iloc[0]
top2 = expansion_df.iloc[1]


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
        metric_card("Active Branches", str(int(stats["num_branches"])), icon=svg("BRANCH"))
    with kpi_cols[1]:
        metric_card("Cities Covered", str(int(stats["num_cities"])), icon=svg("CITY"))
    with kpi_cols[2]:
        metric_card("Avg Revenue/Branch",
                    fmt_currency(stats["total_revenue"] / stats["num_branches"]), icon=svg("CASH"))
    with kpi_cols[3]:
        metric_card("Avg Profit/Branch",
                    fmt_currency(stats["total_profit"] / stats["num_branches"]), icon=svg("MARGIN"))

st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)

if True:
    # ── HERO: Profit by City (chart utama, full width) ─────────────────────
    with st.container(border=True, key="chartbox_city_profit"):
        _chart_header("Profit by City", "city_profit",
                      "Total Profit by City", city_df)
        fig = city_profit_bar(city_df)
        fig.update_layout(title="", height=300,
                          margin=dict(l=8, r=80, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SECONDARY: Margin by Branch Type | Expansion Score Rankings ────────
    r1c1, r1c2 = st.columns(2, gap="small")
    with r1c1:
        with st.container(border=True, key="chartbox_branch_margin"):
            _chart_header("Margin by Branch Type", "branch_type_margin",
                          "Profit Margin by Branch Type", bt_df)
            fig = branch_type_margin_bar(bt_df)
            fig.update_layout(title="", height=260, showlegend=False,
                              margin=dict(l=34, r=10, t=10, b=34),
                              xaxis=dict(automargin=True), yaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with r1c2:
        with st.container(border=True, key="chartbox_expansion"):
            _chart_header("Expansion Score Rankings", "expansion_score",
                          "Expansion Score Rankings", expansion_df, compact=True)
            fig = expansion_bar(expansion_df)
            fig.update_layout(title="", height=260,
                              margin=dict(l=8, r=36, t=20, b=32),
                              xaxis=dict(automargin=True), yaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SUPPORTING: Saturation | Channel Mix | Delivery Share ──────────────
    r2c1, r2c2, r2c3 = st.columns(3, gap="small")

    with r2c1:
        with st.container(border=True, key="chartbox_delivery_city"):
            _chart_header("Delivery Share by City", "delivery_share_city",
                          "Delivery Share by City", city_df)
            fig = delivery_share_city(city_df, df)
            fig.update_layout(title="", height=220, showlegend=False,
                              margin=dict(l=34, r=10, t=20, b=60),
                              xaxis=dict(automargin=True), yaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with r2c2:
        with st.container(border=True, key="chartbox_saturation"):
            _chart_header("Saturation vs Profitability", "saturation_matrix",
                          "Market Saturation vs Profitability Matrix", city_df, compact=True)
            fig = city_bubble(city_df)
            fig.update_layout(title="", height=220, showlegend=False,
                              margin=dict(l=34, r=12, t=26, b=40),
                              xaxis=dict(automargin=True), yaxis=dict(automargin=True))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with r2c3:
        with st.container(border=True, key="chartbox_channel_mix"):
            _chart_header("Channel Mix by Branch Type", "channel_mix_type",
                          "Channel Mix by Branch Type", ch_type_df, compact=True)
            fig = channel_stacked_bar(ch_type_df)
            fig.update_layout(title="", height=220, margin=dict(l=32, r=8, t=34, b=36),
                              xaxis=dict(automargin=True))
            _hlegend_top(fig)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── Detail tabel: dilipat ke expander, tidak memenuhi halaman utama ────
    with st.expander("Detailed Metrics — Branch Type & City Tables", expanded=False):
        t1, t2 = st.columns(2, gap="small")
        with t1:
            st.markdown("#### Branch Type Comparison")
            bt_display = bt_df[['branch_type', 'num_branches', 'total_revenue',
                                'total_profit', 'avg_profit_margin']].copy()
            bt_display['total_revenue'] = bt_display['total_revenue'].apply(fmt_currency)
            bt_display['total_profit'] = bt_display['total_profit'].apply(fmt_currency)
            bt_display['avg_profit_margin'] = bt_display['avg_profit_margin'].round(1)
            bt_display.columns = ['Branch Type', '# Branches', 'Total Revenue', 'Total Profit', 'Margin %']
            st.dataframe(bt_display.sort_values('Margin %', ascending=False),
                         use_container_width=True, hide_index=True)

        with t2:
            st.markdown("#### Detailed City Metrics")
            city_display = city_df[['branch_city', 'num_branches', 'avg_profit_margin',
                                    'revenue_per_branch', 'profit_per_branch']].copy()
            city_display['avg_profit_margin'] = city_display['avg_profit_margin'].round(1)
            city_display['revenue_per_branch'] = city_display['revenue_per_branch'].apply(fmt_currency)
            city_display['profit_per_branch'] = city_display['profit_per_branch'].apply(fmt_currency)
            city_display.columns = ['City', '# Branches', 'Margin %', 'Rev/Branch', 'Profit/Branch']
            st.dataframe(city_display.sort_values('Margin %', ascending=False),
                         use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── BUSINESS HIGHLIGHTS: ringkasan statis, full width ──────────────────
    with st.container(border=True, key="sidepanel_insights"):
        st.markdown("#### Business Highlights")
        info_box(
            f'{svg("PIN")} <b>Best:</b> {best_type["branch_type"]} leads at '
            f'{best_type["avg_profit_margin"]:.1f}% margin',
            kind="success",
        )
        info_box(
            f'{svg("WARNING")} <b>Worst:</b> {worst_type["branch_type"]} '
            f'{worst_type["avg_profit_margin"]:.1f}% — fix before expanding',
            kind="warning",
        )
        info_box(
            f'{svg("BRANCH")} <b>Expand:</b> {top1["branch_city"]} & '
            f'{top2["branch_city"]} are top targets',
            kind="info",
        )