"""
pages/2_📈_Business_Growth_&_Profitability.py
Business Growth & Profitability Analysis
"""

import streamlit as st
from utils.icons import svg
from utils import (
    load_data, apply_filters, build_summary_stats,
    weekday_weekend, promo_revenue, channel_trend, city_performance
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    fmt_currency, fmt_number,
    weekday_bar, promo_avg_revenue, city_profit_bar,
)
from components.cards import inject_compact_css

st.set_page_config(
    page_title="Business Growth & Profitability | KopiSeru BI",
    page_icon="",
    layout="wide",
)

inject_compact_css()

# Load & Filter data
with st.spinner("Loading KopiSeru data..."):
    raw_df = load_data()

filters = render_sidebar(raw_df)
df = apply_filters(raw_df, filters)

if df.empty:
    st.warning("No data matches the current filter selection. Please adjust the sidebar filters.")
    st.stop()

stats = build_summary_stats(df)

# Page Content

section_header(
    "Business Growth & Profitability Analysis",
    "Deep dive into growth drivers and profitability factors"
)

# Repeated calculations for charts
wd_df = weekday_weekend(df)
promo_df = promo_revenue(df)
city_df = city_performance(df)

promo_summary = df.groupby('promo_label').agg({
    'total_revenue': 'mean',
    'profit': 'mean',
    'profit_margin': 'mean'
}).round(2)

import plotly.graph_objects as go


def _chart_header(title: str, key: str, chart_title: str, chart_df, compact: bool = False,
                   extra_text: str = "", extra_kind: str = "info") -> None:
    """Judul chart, dengan insight statis (hasil kalkulasi, bukan AI) opsional
    ditampilkan sebagai info_box di bawah judul."""
    st.markdown(f"#### {title}")
    if extra_text:
        info_box(extra_text, kind=extra_kind)


# ROW 1 Key Metrics (2x2) | Avg Revenue by Promo Type | Promo vs Non-Promo

# KPI
with st.container(key="kpicol_std"):
    kpi_cols = st.columns(4, gap="small")
    with kpi_cols[0]:
        metric_card("Total Revenue", fmt_currency(stats["total_revenue"]), icon=svg("REVENUE"))
    with kpi_cols[1]:
        metric_card("Total Profit", fmt_currency(stats["total_profit"]), icon=svg("PROFIT"))
    with kpi_cols[2]:
        metric_card("Profit Margin", f"{stats['avg_profit_margin']:.1f}%", icon=svg("MARGIN"))
    with kpi_cols[3]:
        metric_card("Total Transactions", fmt_number(stats["total_transactions"]), icon=svg("CART"))

st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)


# Profitability by City 

with st.container(border=True, key="chartbox_city_profitability"):
    top_city = city_df.nlargest(1, 'total_profit').iloc[0]
    top_margin = city_df.nlargest(1, 'avg_profit_margin').iloc[0]

    st.markdown("#### Profitability by City")
    info_box(
        f"<b>Top Profit City:</b> {top_city['branch_city']} • "
        f"Total: Rp{top_city['total_profit']:,.0f}<br>"
        f"<b>Best Margin City:</b> {top_margin['branch_city']} • "
        f"Margin: {top_margin['avg_profit_margin']:.1f}%",
        kind="success"
    )

    fig_city = city_profit_bar(city_df)
    _city_max = max(list(fig_city.data[0].x) or [0])
    fig_city.update_xaxes(range=[0, _city_max * 1.22])
    fig_city.update_layout(
        title="",
        height=300,
        margin=dict(l=90, r=30, t=10, b=40),
    )
    st.plotly_chart(fig_city, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)


# SECONDARY Avg Revenue by Promo Type | Promo vs Non-Promo

row1_c2, row1_c3 = st.columns(2, gap="small")

with row1_c2:
    with st.container(border=True, key="chartbox_promo_avg_revenue"):
        _chart_header("Average Revenue by Promotion Type", "promo_avg_revenue",
                      "Average Revenue by Promotion Type", promo_df, compact=True,
                      extra_text="All promotion types generate similar revenue "
                                 "(~Rp4.7-4.9 M). Presence of promo matters more "
                                 "than the type.",
                      extra_kind="info")
        fig_promo = promo_avg_revenue(df)
        _promo_max = max(list(fig_promo.data[0].x) or [0])
        _promo_labels = list(fig_promo.data[0].y)
        _left_margin = max(len(str(lbl)) for lbl in _promo_labels) * 6.7 + 8
        fig_promo.update_xaxes(range=[0, _promo_max * 1.1])
        fig_promo.update_yaxes(automargin=False, ticklabelstandoff=0, tickfont=dict(size=12))
        fig_promo.update_traces(textposition="outside", cliponaxis=False)
        fig_promo.update_layout(
            title="",
            height=300,
            bargap=0.18,
            margin=dict(l=_left_margin, r=28, t=10, b=34),
        )
        st.plotly_chart(fig_promo, use_container_width=True, config={"displayModeBar": False})

with row1_c3:
    with st.container(border=True, key="chartbox_promo_vs_nonpromo"):
        _promo_boost = ((promo_summary.loc['Promo', 'total_revenue'] /
                         promo_summary.loc['Non-Promo', 'total_revenue']) - 1) * 100
        _chart_header("Promo vs Non-Promo", "promo_vs_nonpromo",
                      "Promo vs Non-Promo Revenue", promo_summary.reset_index(), compact=True,
                      extra_text=f"Promo boost: {_promo_boost:.1f}%<br>Effective for volume, but margin impact needs evaluation.",
                      extra_kind="info")
        fig_comp = go.Figure(data=[
            go.Bar(name='Avg Revenue',
                   x=['Promo', 'Non-Promo'],
                   y=[promo_summary.loc['Promo', 'total_revenue'],
                      promo_summary.loc['Non-Promo', 'total_revenue']],
                   marker_color=['#D4A853', '#8B5E3C']),
        ])
        fig_comp.update_layout(
            title="",
            xaxis=dict(
                title=dict(text="", font=dict(size=14)),   
                tickfont=dict(size=14),                     
            ),
            yaxis=dict(
                title=dict(text="Avg Revenue (Rp)", font=dict(size=14)),  
                tickfont=dict(size=14),                     
            ),
            showlegend=False,
            yaxis_title="Avg Revenue (Rp)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=34, r=10, t=10, b=34),
        )
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)


# ROW 2 Weekday vs Weekend: Revenue | Transactions | Profit

row2_c1, row2_c2, row2_c3 = st.columns([1, 1, 1], gap="small")

with row2_c1:
    with st.container(border=True, key="chartbox_weekday_revenue"):
        wd_rev = wd_df.sort_values('day_type')['avg_revenue'].values
        _rev_extra = ""
        if len(wd_rev) == 2:
            pct_change = ((wd_rev[1] - wd_rev[0]) / wd_rev[0]) * 100
            _rev_extra = f"Revenue change: {pct_change:+.1f}%<br>Relatively stable"

        _chart_header("Revenue", "weekday_revenue",
                      "Weekday vs Weekend Revenue", wd_df, compact=True,
                      extra_text=_rev_extra, extra_kind="info")
        fig_rev = weekday_bar(wd_df.copy())
        fig_rev.update_layout(
            title="",
            yaxis_title="Avg Revenue (Rp)",
            height=238.5,
            margin=dict(l=34, r=30, t=10, b=40),
        )
        st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})

with row2_c2:
    with st.container(border=True, key="chartbox_weekday_txn"):
        wd_txn = wd_df.sort_values('day_type')['avg_transactions'].values
        _txn_extra = ""
        if len(wd_txn) == 2:
            pct_txn = ((wd_txn[1] - wd_txn[0]) / wd_txn[0]) * 100
            _txn_extra = f"Transaction change: {pct_txn:+.1f}%<br>Stable across week"

        _chart_header("Transactions", "weekday_txn",
                      "Weekday vs Weekend Transactions", wd_df, compact=True,
                      extra_text=_txn_extra, extra_kind="info")

        if len(wd_txn) == 2:
            fig_txn = go.Figure()
            fig_txn.add_trace(go.Bar(
                x=wd_df['day_type'],
                y=wd_df['avg_transactions'],
                marker_color=['#5C3D1E', '#D4A853'],
                text=wd_df['avg_transactions'].apply(lambda x: f'{x:.0f}'),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Transactions: %{y:.0f}<extra></extra>'
            ))
            fig_txn.update_layout(
                title="",
                yaxis_title="Avg Transactions",
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=238.5,
                margin=dict(l=34, r=10, t=10, b=40),
            )
            st.plotly_chart(fig_txn, use_container_width=True, config={"displayModeBar": False})

with row2_c3:
    with st.container(border=True, key="chartbox_weekday_profit"):
        wd_profit = wd_df.sort_values('day_type')['avg_profit'].values
        _profit_extra = ""
        if len(wd_profit) == 2:
            pct_profit = ((wd_profit[1] - wd_profit[0]) / wd_profit[0]) * 100
            _profit_extra = (
                f"<b>CRITICAL:</b><br>Profit change: {pct_profit:+.1f}%<br>"
                "Weekend margin drops significantly!"
            )

        _chart_header("Profit", "weekday_profit",
                      "Weekday vs Weekend Profit", wd_df, compact=True,
                      extra_text=_profit_extra, extra_kind="warning")

        if len(wd_profit) == 2:
            fig_profit = go.Figure()
            fig_profit.add_trace(go.Bar(
                x=wd_df['day_type'],
                y=wd_df['avg_profit'],
                marker_color=['#5C3D1E', '#D4A853'],
                text=wd_df['avg_profit'].apply(lambda x: f'Rp{x/1e6:.1f}M'),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Profit: Rp%{y:,.0f}<extra></extra>'
            ))
            fig_profit.update_layout(
                title="",
                yaxis_title="Avg Profit (Rp)",
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=220,
                margin=dict(l=34, r=10, t=10, b=40),
            )
            st.plotly_chart(fig_profit, use_container_width=True, config={"displayModeBar": False})

# Critical Finding
st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

with st.expander("Weekend Profit Drop: Further Analysis & Recommended Actions", expanded=False):
    col_insight1, col_insight2 = st.columns(2, gap="small")

    with col_insight1:
        st.markdown("**Further Analysis Required**")
        info_box(
            "• Revenue only -3% but Profit -19%<br>"
            "• Likely higher operational costs<br>"
            "• Staff scheduling inefficiency?<br>"
            "• Menu/inventory waste?",
            kind="warning"
        )

    with col_insight2:
        st.markdown("**Recommended Actions**")
        info_box(
            "• Review weekend labor scheduling<br>"
            "• Implement dynamic pricing<br>"
            "• Optimize menu for weekend demand<br>"
            "• Monitor cost per transaction closely",
            kind="success"
        )

st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)


# BUSINESS HIGHLIGHTS 

top_city = city_df.nlargest(1, 'total_profit').iloc[0]
top_margin = city_df.nlargest(1, 'avg_profit_margin').iloc[0]

with st.container(border=True, key="sidepanel_insights"):
    st.markdown("#### Business Highlights")
    st.markdown(
        """
        <div style="font-size:11px; color:var(--text-muted); margin:-18px 0 18px 0; line-height:1.6;">
            Summarizes which cities drive the most profit, how well promotions
            pay off, and where weekend performance needs closer attention.
        </div>
        """,
        unsafe_allow_html=True,
    )
    info_box(
        f"<b>Top Profit City:</b> {top_city['branch_city']} • "
        f"Total: Rp{top_city['total_profit']:,.0f}<br>"
        f"<b>Best Margin City:</b> {top_margin['branch_city']} • "
        f"Margin: {top_margin['avg_profit_margin']:.1f}%",
        kind="success"
    )
    info_box(
        f"Promo boost: {_promo_boost:.1f}% • effective for volume, "
        "margin impact still needs evaluation.",
        kind="info"
    )
    info_box(
        "Weekend profit drops sharply vs weekday see Further Analysis above.",
        kind="warning"
    )