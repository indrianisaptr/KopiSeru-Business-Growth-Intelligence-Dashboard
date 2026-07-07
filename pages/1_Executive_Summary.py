"""
pages/1_📊_Executive_Summary.py
Executive Summary - Business Health Overview
Layout: kolom KPI sempit di kiri, grid chart di kanan.
Tombol "Explain" dipindah ke pojok kanan atas tiap chart (sejajar judul).
"""

import streamlit as st
from utils.icons import svg
from utils import (
    load_data, apply_filters, build_summary_stats,
    monthly_revenue, yoy_growth, correlation_matrix,
    branch_type_performance, channel_distribution
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    fmt_currency, fmt_number,
    revenue_trend, revenue_yoy_bar, promo_boxplot, promo_avg_revenue,
    correlation_heatmap, branch_type_margin_bar, channel_pie,
)
from components.cards import inject_compact_css

st.set_page_config(
    page_title="Executive Summary | KopiSeru BI",
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
section_header("Executive Summary", "KopiSeru Business Health Overview · 2021–2023")

# ── YoY calc ─────────────────────────────────────────────────────────────
_yearly = df.groupby("year").agg(
    rev=("total_revenue", "sum"),
    pft=("profit", "sum"),
    txn=("total_transactions", "sum"),
).reset_index().sort_values("year")

_yrs = _yearly["year"].tolist()
if len(_yrs) >= 2:
    _c = _yearly[_yearly["year"] == _yrs[-1]].iloc[0]
    _p = _yearly[_yearly["year"] == _yrs[-2]].iloc[0]
    _rev_yoy = (_c["rev"] - _p["rev"]) / _p["rev"] * 100
    _pft_yoy = (_c["pft"] - _p["pft"]) / _p["pft"] * 100
    _txn_yoy = (_c["txn"] - _p["txn"]) / _p["txn"] * 100
else:
    _rev_yoy = _pft_yoy = _txn_yoy = 0.0

monthly_df = monthly_revenue(df)
bt_df = branch_type_performance(df)
ch_df = channel_distribution(df)


def _chart_header(title: str, key: str, chart_title: str, chart_df, compact: bool = False) -> None:
    """Judul chart."""
    st.markdown(f"#### {title}")

# ── KPI: baris horizontal di atas (bukan kolom sempit di kiri) ────────────
with st.container(key="kpicol_main"):
    kpi_cols = st.columns(6, gap="small")
    with kpi_cols[0]:
        metric_card("Total Revenue", fmt_currency(stats["total_revenue"]),
                    delta=f"+{_rev_yoy:.1f}% YoY", delta_positive=_rev_yoy >= 0, icon=svg("REVENUE"))
    with kpi_cols[1]:
        metric_card("Total Profit", fmt_currency(stats["total_profit"]),
                    delta=f"+{_pft_yoy:.1f}% YoY", delta_positive=_pft_yoy >= 0, icon=svg("PROFIT"))
    with kpi_cols[2]:
        metric_card("Profit Margin", f"{stats['avg_profit_margin']:.1f}%", icon=svg("MARGIN"))
    with kpi_cols[3]:
        metric_card("Total Transactions", fmt_number(stats["total_transactions"]),
                    delta=f"+{_txn_yoy:.1f}% YoY", delta_positive=_txn_yoy >= 0, icon=svg("TRANSACTION"))
    with kpi_cols[4]:
        metric_card("Avg Satisfaction", f"{stats['avg_satisfaction']:.2f}", icon=svg("SATISFACTION"))
    with kpi_cols[5]:
        metric_card("Total Branches", str(int(stats["num_branches"])), icon=svg("BRANCH"))

st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)

if True:
    # ── HERO: Revenue Trend (full width, chart utama halaman) ─────────────
    with st.container(border=True, key="chartbox_revenue_trend"):
        _chart_header("Revenue Trend", "revenue_trend", "Monthly Revenue Trend", monthly_df)
        fig = revenue_trend(monthly_df)
        fig.update_layout(
            title="",
            height=275,
            margin=dict(l=34, r=10, t=34, b=10),
            legend=dict(
                font=dict(size=9.5),
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="center",
                x=0.5,
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SECONDARY: Profit Trend | Margin by Branch Type ────────────────────
    r1c1, r1c2 = st.columns(2, gap="small")
    with r1c1:
        with st.container(border=True, key="chartbox_profit_trend"):
            monthly_profit_df = monthly_df[['year', 'month', 'month_label', 'profit']].copy()
            monthly_profit_df = monthly_profit_df.sort_values(['year', 'month'])
            _chart_header("Profit Trend", "profit_trend", "Profit Trend", monthly_profit_df)

            # Ambil warna persis dari fig Revenue Trend (fig sudah dibuat di HERO di atas)
            _revenue_colors = [trace.line.color for trace in fig.data]

            import plotly.graph_objects as go
            fig_profit = go.Figure()
            for i, year in enumerate(sorted(monthly_profit_df['year'].unique())):
                year_data = monthly_profit_df[monthly_profit_df['year'] == year]
                _color = _revenue_colors[i % len(_revenue_colors)]
                fig_profit.add_trace(go.Scatter(
                    x=year_data['month_label'],
                    y=year_data['profit'],
                    mode='lines+markers',
                    name=str(year),
                    line=dict(color=_color),
                    marker=dict(color=_color),
                    hovertemplate='<b>%{x}</b><br>Profit: Rp %{y:,.0f}<extra></extra>'
                ))
            fig_profit.update_layout(
                xaxis=dict(title=dict(text="Month", font=dict(size=10)), tickfont=dict(size=9)),
                yaxis=dict(title=dict(text="Profit (Rp)", font=dict(size=10)), tickfont=dict(size=9)),
                hovermode='x unified',
                template='plotly_white',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=250,
                margin=dict(l=34, r=10, t=34, b=10),
                font=dict(size=10.5),
                legend=dict(
                    font=dict(size=9.5),
                    orientation="h",
                    yanchor="bottom",
                    y=1.05,
                    xanchor="center",
                    x=0.5,
                ),
            )
            st.plotly_chart(fig_profit, use_container_width=True, config={"displayModeBar": False})

    with r1c2:
        with st.container(border=True, key="chartbox_branch_margin"):
            _chart_header("Margin by Branch Type", "branch_type_margin",
                          "Profit Margin by Branch Type", bt_df)
            fig_bt = branch_type_margin_bar(bt_df)
            fig_bt.update_layout(
                title="",
                height=250,
                margin=dict(l=34, r=10, t=6, b=36),
                xaxis=dict(automargin=True),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_bt, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SUPPORTING: Revenue vs Transaction | Promotion Impact | Channel Distribution ──
    r2c1, r2c2, r2c3 = st.columns(3, gap="small")
    with r2c1:
        with st.container(border=True, key="chartbox_txn_revenue"):
            _chart_header("Revenue vs Transaction", "txn_revenue_corr",
                          "Revenue vs Transaction Correlation",
                          df[["total_transactions", "total_revenue"]], compact=True)
            from components import txn_vs_revenue_scatter
            fig_corr = txn_vs_revenue_scatter(df)
            fig_corr.update_layout(
                title="",
                height=220,
                margin=dict(l=32, r=6, t=6, b=44),
                xaxis=dict(title=dict(font=dict(size=10)), tickfont=dict(size=9), automargin=True),
                yaxis=dict(title=dict(font=dict(size=10)), tickfont=dict(size=9), automargin=True),
                coloraxis_colorbar=dict(
                    title=dict(text="Avg Ticket (Rp)", font=dict(size=8)),
                    thickness=8,
                    len=0.55,
                    tickfont=dict(size=7),
                    x=1.0,
                    xpad=2,
                ),
            )
            st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

    with r2c2:
        with st.container(border=True, key="chartbox_promo_impact"):
            _chart_header("Promotion Impact", "promo_impact", "Promotion Impact on Revenue",
                          df[["promo_label", "total_revenue"]], compact=True)
            fig_promo = promo_boxplot(df)
            fig_promo.update_layout(
                title="",
                height=220,
                margin=dict(l=32, r=8, t=40, b=30),
                legend=dict(
                    font=dict(size=9.5),
                    orientation="h",
                    yanchor="bottom",
                    y=1.05,
                    xanchor="center",
                    x=0.5,
                ),
            )
            st.plotly_chart(fig_promo, use_container_width=True, config={"displayModeBar": False})

    with r2c3:
        with st.container(border=True, key="chartbox_channel_dist"):
            _chart_header("Channel Distribution", "channel_dist", "Channel Distribution", ch_df, compact=True)
            fig_ch = channel_pie(ch_df)
            fig_ch.update_traces(hole=0.32, textfont=dict(size=11))
            fig_ch.update_layout(
                title="",
                height=220,
                margin=dict(l=4, r=4, t=6, b=34),
                legend=dict(
                    font=dict(size=9.5),
                    orientation="h",
                    yanchor="bottom",
                    y=-0.22,
                    xanchor="center",
                    x=0.5,
                ),
            )
            st.plotly_chart(fig_ch, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── BUSINESS HIGHLIGHTS: ringkasan statis, full width ──────────────────
    # AFTER
    with st.container(border=True, key="sidepanel_insights"):
        st.markdown("#### Business Highlights")
        st.markdown(
            """
            <div style="font-size:11px; color:var(--text-muted); margin:-18px 0 18px 0; line-height:1.6;">
                A quick snapshot of revenue growth, branch profitability, and expansion
                opportunities to help guide strategic business decisions.
            </div>
            """,
            unsafe_allow_html=True,
        )
        info_box(f'{svg("INSIGHT")} <b>Growth:</b> +73.7% (21 to 22), +49.2% (22 to 23)', kind="success")
        info_box(f'{svg("PIN")} <b>Branch Type:</b> Mall 35.2% margin, University -37.7%', kind="warning")
        info_box(f'{svg("BRANCH")} <b>Expansion:</b> Makassar & Denpasar top targets', kind="info")
        
        