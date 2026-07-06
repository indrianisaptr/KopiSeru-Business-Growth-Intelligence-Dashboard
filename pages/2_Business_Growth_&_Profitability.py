"""
pages/2_Business_Growth_&_Profitability.py
Business Growth & Profitability Analysis 
"""

import streamlit as st
from utils import (
    load_data, apply_filters, build_summary_stats,
    weekday_weekend, promo_revenue, channel_trend, city_performance
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    fmt_currency, fmt_number,
    weekday_bar, promo_avg_revenue, city_profit_bar,
    render_business_copilot
)
from components.ai_analyst import render_chart_explainer

st.set_page_config(
    page_title="Business Growth & Profitability | KopiSeru BI",
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
    "Business Growth & Profitability Analysis",
    "Deep dive into growth drivers and profitability factors"
)

# ── KPI Cards ─────────────────────────────────────────────────────────────

st.subheader("Key Metrics")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Revenue", fmt_currency(stats["total_revenue"]),
                icon="💰")
with c2:
    metric_card("Total Profit", fmt_currency(stats["total_profit"]),
                icon="📈")
with c3:
    metric_card("Profit Margin", f"{stats['avg_profit_margin']:.1f}%",
                icon="💹")
with c4:
    metric_card("Total Transactions", fmt_number(stats["total_transactions"]),
                icon="🛒")

st.markdown("<br>", unsafe_allow_html=True)

# ── Weekday vs Weekend Analysis ───────────────────────────────────────────

st.subheader("Weekday vs Weekend Performance Analysis")

wd_df = weekday_weekend(df)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("#### Revenue")
    revenue_comparison = wd_df[['day_type', 'avg_revenue']].copy()
    fig_rev = weekday_bar(wd_df.copy())
    st.plotly_chart(fig_rev, use_container_width=True)
    render_chart_explainer("Weekday vs Weekend Revenue", wd_df, filters, stats, "Business Growth & Profitability", "weekday_revenue")
    
    wd_rev = wd_df.sort_values('day_type')['avg_revenue'].values
    if len(wd_rev) == 2:
        pct_change = ((wd_rev[1] - wd_rev[0]) / wd_rev[0]) * 100
        info_box(
            f"Revenue change: {pct_change:+.1f}%<br>Relatively stable",
            kind="info"
        )

with col_b:
    st.markdown("#### Transactions")
    wd_txn = wd_df.sort_values('day_type')['avg_transactions'].values
    if len(wd_txn) == 2:
        pct_txn = ((wd_txn[1] - wd_txn[0]) / wd_txn[0]) * 100
        
        import plotly.graph_objects as go
        fig_txn = go.Figure()
        fig_txn.add_trace(go.Bar(
            x=wd_df['day_type'],
            y=wd_df['avg_transactions'],
            marker_color=['#8B5E3C', '#D4A853'],
            text=wd_df['avg_transactions'].apply(lambda x: f'{x:.0f}'),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Transactions: %{y:.0f}<extra></extra>'
        ))
        fig_txn.update_layout(
            title="",
            xaxis_title="Day Type",
            yaxis_title="Avg Transactions",
            showlegend=False,
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_txn, use_container_width=True)
        render_chart_explainer("Weekday vs Weekend Transactions", wd_df, filters, stats, "Business Growth & Profitability", "weekday_txn")
        
        info_box(
            f"Transaction change: {pct_txn:+.1f}%<br>Stable across week",
            kind="info"
        )

with col_c:
    st.markdown("#### Profit")
    wd_profit = wd_df.sort_values('day_type')['avg_profit'].values
    if len(wd_profit) == 2:
        pct_profit = ((wd_profit[1] - wd_profit[0]) / wd_profit[0]) * 100
        
        fig_profit = go.Figure()
        fig_profit.add_trace(go.Bar(
            x=wd_df['day_type'],
            y=wd_df['avg_profit'],
            marker_color=['#5C3D1E', '#E05252'],
            text=wd_df['avg_profit'].apply(lambda x: f'Rp {x/1e6:.1f}JT'),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Profit: Rp %{y:,.0f}<extra></extra>'
        ))
        fig_profit.update_layout(
            title="",
            xaxis_title="Day Type",
            yaxis_title="Avg Profit (Rp)",
            showlegend=False,
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_profit, use_container_width=True)
        render_chart_explainer("Weekday vs Weekend Profit", wd_df, filters, stats, "Business Growth & Profitability", "weekday_profit")
        
        info_box(
            f"<b>CRITICAL:</b><br>Profit change: {pct_profit:+.1f}%<br>"
            "Weekend margin drops significantly!",
            kind="warning"
        )

st.markdown("---")

# ── Critical Finding ─────────────────────────────────────────────────────

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    info_box(
        "<b>Root Cause Analysis Needed:</b><br>"
        "• Revenue only -3% but Profit -19%<br>"
        "• Likely higher operational costs<br>"
        "• Staff scheduling inefficiency?<br>"
        "• Menu/inventory waste?",
        kind="warning"
    )

with col_insight2:
    info_box(
        "<b>Immediate Actions:</b><br>"
        "• Review weekend labor scheduling<br>"
        "• Implement dynamic pricing<br>"
        "• Optimize menu for weekend demand<br>"
        "• Monitor cost per transaction closely",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Promotion Analysis ────────────────────────────────────────────────────

st.subheader("Promotion Effectiveness")

col_promo1, col_promo2 = st.columns(2)

with col_promo1:
    st.markdown("#### Average Revenue by Promotion Type")
    promo_df = promo_revenue(df)
    fig_promo = promo_avg_revenue(df)
    st.plotly_chart(fig_promo, use_container_width=True)
    render_chart_explainer("Average Revenue by Promotion Type", promo_df, filters, stats, "Business Growth & Profitability", "promo_avg_revenue")
    
    info_box(
        "All promotion types generate similar revenue (~Rp 4.7-4.9 JT). "
        "Presence of promo matters more than the type.",
        kind="info"
    )

with col_promo2:
    st.markdown("#### Promo vs Non-Promo")
    promo_summary = df.groupby('promo_label').agg({
        'total_revenue': 'mean',
        'profit': 'mean',
        'profit_margin': 'mean'
    }).round(2)
    
    import plotly.graph_objects as go
    fig_comp = go.Figure(data=[
        go.Bar(name='Avg Revenue',
               x=['Promo', 'Non-Promo'],
               y=[promo_summary.loc['Promo', 'total_revenue'],
                  promo_summary.loc['Non-Promo', 'total_revenue']],
               marker_color=['#D4A853', '#8B5E3C']),
    ])
    fig_comp.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="Avg Revenue (Rp)",
        showlegend=False,
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_comp, use_container_width=True)
    render_chart_explainer("Promo vs Non-Promo Revenue", promo_summary.reset_index(), filters, stats, "Business Growth & Profitability", "promo_vs_nonpromo")
    
    info_box(
        f"Promo boost: {((promo_summary.loc['Promo', 'total_revenue'] / promo_summary.loc['Non-Promo', 'total_revenue']) - 1) * 100:.1f}%<br>"
        "Effective for volume, but margin impact needs evaluation.",
        kind="info"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── City Profitability ────────────────────────────────────────────────────

st.subheader("Profitability by City")

city_df = city_performance(df)
fig_city = city_profit_bar(city_df)
st.plotly_chart(fig_city, use_container_width=True)
render_chart_explainer("Profitability by City", city_df, filters, stats, "Business Growth & Profitability", "city_profitability")

col_city1, col_city2 = st.columns(2)

with col_city1:
    top_city = city_df.nlargest(1, 'total_profit').iloc[0]
    info_box(
        f"<b>Top Profit City:</b><br>"
        f"{top_city['branch_city']}<br>"
        f"Total: Rp {top_city['total_profit']:,.0f}",
        kind="success"
    )

with col_city2:
    top_margin = city_df.nlargest(1, 'avg_profit_margin').iloc[0]
    info_box(
        f"<b>Best Margin City:</b><br>"
        f"{top_margin['branch_city']}<br>"
        f"Margin: {top_margin['avg_profit_margin']:.1f}%",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Detailed Metrics Table ────────────────────────────────────────────────

with st.expander("Detailed Profitability Metrics by City"):
    st.dataframe(
        city_df[[
            'branch_city', 'num_branches', 'total_revenue', 'total_profit',
            'avg_profit_margin', 'revenue_per_branch', 'profit_per_branch'
        ]].sort_values('avg_profit_margin', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ── Business Development Copilot ──────────────────────────────────────────

suggested_q = [
    "Mengapa profit weekend drop 19% padahal revenue stabil?",
    "Bagaimana cara optimalkan weekend profitability?",
    "Promo mana yang paling cost-effective?",
    "Kota mana yang paling profitable per branch?",
]

render_business_copilot(
    filters=filters,
    stats=stats,
    page_name="Business Growth & Profitability",
    suggested_questions=suggested_q,
)