"""
pages/1_📊_Executive_Summary.py
Executive Summary - Business Health Overview with AI Copilot
"""

import streamlit as st
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
    render_business_copilot
)
from components.ai_analyst import render_chart_explainer

st.set_page_config(
    page_title="Executive Summary | KopiSeru BI",
    page_icon="",
    layout="wide",
)

# ── Load & Filter data ────────────────────────────────────────────────────
with st.spinner("Loading KopiSeru data..."):
    raw_df = load_data()

filters = render_sidebar(raw_df)
df = apply_filters(raw_df, filters)

if df.empty:
    st.warning("No data matches the current filter selection. Please adjust the sidebar filters.")
    st.stop()

stats = build_summary_stats(df)

# ── Page Content ──────────────────────────────────────────────────────────

section_header(
    "Executive Summary",
    "KopiSeru Business Health Overview · 2021–2023"
)

# ── KPI Cards ─────────────────────────────────────────────────────────────

st.subheader("Key Performance Indicators")

# Row 1: 4 cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Revenue", fmt_currency(stats["total_revenue"]),
                icon="💰", help_text="All branches, filtered period")
with c2:
    yoy = yoy_growth(df)
    latest_yoy = list(yoy.values())[-1] if yoy else 0
    metric_card("YoY Growth", f"+{latest_yoy:.1f}%" if latest_yoy >= 0 else f"{latest_yoy:.1f}%",
                delta=f"{latest_yoy:+.1f}%", delta_positive=latest_yoy >= 0,
                icon="📊", help_text="Latest year-on-year growth")
with c3:
    metric_card("Total Profit", fmt_currency(stats["total_profit"]),
                icon="📈", help_text="Net profit after operating costs")
with c4:
    metric_card("Avg Profit Margin", f"{stats['avg_profit_margin']:.1f}%",
                icon="💹", help_text="Average margin across all branches")

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: 2 additional cards
c5, c6 = st.columns([2, 1])
with c5:
    metric_card("Total Transactions", fmt_number(stats["total_transactions"]),
                icon="🛒", help_text="All transactions across branches")
with c6:
    metric_card("Customer Satisfaction", f"{stats['avg_satisfaction']:.2f} / 5",
                icon="😊", help_text="Mean satisfaction score")

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Charts ───────────────────────────────────────────────────────────

st.subheader("Business Performance")

# Row 1: Revenue & Profit Trends
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Revenue Trend")
    monthly_df = monthly_revenue(df)
    fig = revenue_trend(monthly_df)
    st.plotly_chart(fig, use_container_width=True)
    render_chart_explainer("Monthly Revenue Trend", monthly_df, filters, stats, "Executive Summary", "revenue_trend")

with col_b:
    st.markdown("#### Profit Trend")
    # Create profit trend (similar structure to revenue trend)
    monthly_profit_df = monthly_df[['year', 'month', 'month_label', 'profit']].copy()
    monthly_profit_df = monthly_profit_df.sort_values(['year', 'month'])
    
    import plotly.graph_objects as go
    fig_profit = go.Figure()
    for year in monthly_profit_df['year'].unique():
        year_data = monthly_profit_df[monthly_profit_df['year'] == year]
        fig_profit.add_trace(go.Scatter(
            x=year_data['month_label'],
            y=year_data['profit'],
            mode='lines+markers',
            name=str(year),
            hovertemplate='<b>%{x}</b><br>Profit: Rp %{y:,.0f}<extra></extra>'
        ))
    fig_profit.update_layout(
        title="",
        xaxis_title="Month",
        yaxis_title="Profit (Rp)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_profit, use_container_width=True)
    render_chart_explainer("Profit Trend", monthly_profit_df, filters, stats, "Executive Summary", "profit_trend")

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: Revenue vs Transaction & Promo Impact
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("#### Revenue vs Transaction Correlation")
    from components import txn_vs_revenue_scatter
    fig_corr = txn_vs_revenue_scatter(df)
    st.plotly_chart(fig_corr, use_container_width=True)
    render_chart_explainer("Revenue vs Transaction Correlation", df[["total_transactions", "total_revenue"]], filters, stats, "Executive Summary", "txn_revenue_corr")
    info_box(
        "💡 Strong correlation (0.83) between transactions and revenue, but ticket size matters too.",
        kind="info"
    )

with col_d:
    st.markdown("#### Promotion Impact")
    fig_promo = promo_boxplot(df)
    st.plotly_chart(fig_promo, use_container_width=True)
    render_chart_explainer("Promotion Impact on Revenue", df[["promo_label", "total_revenue"]], filters, stats, "Executive Summary", "promo_impact")
    info_box(
        "📌 Promos boost volume. All types show similar effectiveness (~Rp 4.7-4.9 JT avg revenue).",
        kind="info"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Row 3: Branch Type & Channel
col_e, col_f = st.columns(2)

with col_e:
    st.markdown("#### Profit Margin by Branch Type")
    bt_df = branch_type_performance(df)
    fig_bt = branch_type_margin_bar(bt_df)
    st.plotly_chart(fig_bt, use_container_width=True)
    render_chart_explainer("Profit Margin by Branch Type", bt_df, filters, stats, "Executive Summary", "branch_type_margin")

with col_f:
    st.markdown("#### Channel Distribution")
    ch_df = channel_distribution(df)
    fig_ch = channel_pie(ch_df)
    st.plotly_chart(fig_ch, use_container_width=True)
    render_chart_explainer("Channel Distribution", ch_df, filters, stats, "Executive Summary", "channel_dist")

st.markdown("<br>", unsafe_allow_html=True)

# ── Key Insights ──────────────────────────────────────────────────────────

section_header("Key Business Insights", "Summary of current performance")

i1, i2, i3 = st.columns(3)

with i1:
    info_box(
        "<b>Growth Momentum:</b><br>Revenue grew +73.7% (2021→2022) "
        "and +49.2% (2022→2023), showing sustained growth.",
        kind="success"
    )

with i2:
    info_box(
        "<b>Branch Type Matters:</b><br>Mall branches lead with 35.2% margin. "
        "University branches are at -37.7% — requires urgent attention.",
        kind="warning"
    )

with i3:
    info_box(
        "<b>Expansion Priority:</b><br>Makassar and Denpasar identified as top "
        "expansion targets based on profitability and low saturation.",
        kind="info"
    )

# ── Business Development Copilot ──────────────────────────────────────────

suggested_q = [
    "Apakah bisnis kami tetap tumbuh?",
    "Margin cabang tipe mana yang paling sehat?",
    "Kota mana yang paling layak untuk ekspansi?",
    "Apakah promosi masih efektif untuk revenue?",
]

render_business_copilot(
    filters=filters,
    stats=stats,
    page_name="Executive Summary",
    suggested_questions=suggested_q,
)