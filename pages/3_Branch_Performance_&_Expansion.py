"""
pages/3_Branch_Performance_&_Expansion.py
Branch Performance & Expansion Strategy 
"""

import streamlit as st
import pandas as pd
from utils import (
    load_data, apply_filters, build_summary_stats,
    city_performance, branch_type_performance,
    expansion_score, channel_by_type
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    fmt_currency, fmt_number,
    city_profit_bar, branch_type_margin_bar, city_bubble,
    expansion_bar, channel_stacked_bar, delivery_share_city,
    render_business_copilot
)
from components.ai_analyst import render_chart_explainer

st.set_page_config(
    page_title="Branch Performance & Expansion | KopiSeru BI",
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
    "Branch Performance & Expansion Strategy",
    "Evaluate branch performance and identify expansion opportunities"
)

# ── KPI Cards ─────────────────────────────────────────────────────────────

st.subheader("Portfolio Overview")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Active Branches", str(stats["num_branches"]),
                icon="🏪")
with c2:
    metric_card("Cities Covered", str(stats["num_cities"]),
                icon="🌆")
with c3:
    metric_card("Avg Revenue/Branch", fmt_currency(stats["total_revenue"] / stats["num_branches"]),
                icon="💰")
with c4:
    metric_card("Avg Profit/Branch", fmt_currency(stats["total_profit"] / stats["num_branches"]),
                icon="📈")

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: BRANCH PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Section 1: Branch Performance Analysis")

# Branch Type Performance
col_perf1, col_perf2 = st.columns([1.2, 1.8])

with col_perf1:
    st.markdown("#### Profit Margin by Branch Type")
    bt_df = branch_type_performance(df)
    fig_bt = branch_type_margin_bar(bt_df)
    st.plotly_chart(fig_bt, use_container_width=True)
    render_chart_explainer("Profit Margin by Branch Type", bt_df, filters, stats, "Branch Performance & Expansion", "branch_type_margin")

with col_perf2:
    st.markdown("#### Branch Type Comparison")
    
    bt_display = bt_df[['branch_type', 'num_branches', 'total_revenue',
                         'total_profit', 'avg_profit_margin']].copy()
    bt_display.columns = ['Branch Type', '# Branches', 'Total Revenue', 'Total Profit', 'Margin %']
    
    st.dataframe(
        bt_display.sort_values('Margin %', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### Key Findings:")
    
    best_type = bt_df.nlargest(1, 'avg_profit_margin').iloc[0]
    worst_type = bt_df.nsmallest(1, 'avg_profit_margin').iloc[0]
    
    col_best, col_worst = st.columns(2)
    with col_best:
        info_box(
            f"<b>Best: {best_type['branch_type']}</b><br>"
            f"Margin: {best_type['avg_profit_margin']:.1f}%<br>"
            f"Branches: {int(best_type['num_branches'])}",
            kind="success"
        )
    with col_worst:
        info_box(
            f"<b>Worst: {worst_type['branch_type']}</b><br>"
            f"Margin: {worst_type['avg_profit_margin']:.1f}%<br>"
            f"Requires urgent review",
            kind="warning"
        )

st.markdown("<br>", unsafe_allow_html=True)

# City Performance
st.markdown("#### City Profitability Analysis")

col_city1, col_city2 = st.columns(2)

with col_city1:
    st.markdown("**Profit by City**")
    city_df = city_performance(df)
    fig_city = city_profit_bar(city_df)
    st.plotly_chart(fig_city, use_container_width=True)
    render_chart_explainer("Profit by City", city_df, filters, stats, "Branch Performance & Expansion", "city_profit")

with col_city2:
    st.markdown("**Detailed City Metrics**")
    city_display = city_df[['branch_city', 'num_branches', 'avg_profit_margin',
                            'revenue_per_branch', 'profit_per_branch']].copy()
    city_display.columns = ['City', '# Branches', 'Margin %', 'Rev/Branch', 'Profit/Branch']
    
    st.dataframe(
        city_display.sort_values('Margin %', ascending=False),
        use_container_width=True,
        hide_index=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: EXPANSION OPPORTUNITY
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Section 2: Expansion Opportunity Analysis")

# Expansion Score Methodology
with st.expander("How Expansion Score is Calculated", expanded=False):
    st.markdown("""
    **Expansion Score Formula:**
    ```
    Score = (Normalized Profit Margin + Normalized Market Saturation) / 2
    ```
    
    **Two Equally Weighted Factors:**
    1. **Profit Margin (0-1):** Higher margin = better profitability
    2. **Market Saturation (0-1):** Inverse of branch count (lower saturation = more opportunity)
    
    **Interpretation:**
    - High score + Low branches = Best expansion target
    - High score + High branches = Already developed market
    - Low score + Low branches = Needs market validation
    """)

# Expansion Rankings
expansion_df = expansion_score(df)

col_exp1, col_exp2 = st.columns([2, 1])

with col_exp1:
    st.markdown("#### Expansion Score Rankings")
    fig_exp = expansion_bar(expansion_df)
    st.plotly_chart(fig_exp, use_container_width=True)
    render_chart_explainer("Expansion Score Rankings", expansion_df, filters, stats, "Branch Performance & Expansion", "expansion_score")

with col_exp2:
    st.markdown("#### Top 3 Targets")
    for idx, (_, row) in enumerate(expansion_df.head(3).iterrows(), 1):
        info_box(
            f"<b>{idx}. {row['branch_city']}</b><br>"
            f"Score: {row['expansion_score']:.3f}<br>"
            f"Branches: {int(row['num_branches'])} | Margin: {row['avg_profit_margin']:.1f}%",
            kind="success" if idx == 1 else "info"
        )

st.markdown("<br>", unsafe_allow_html=True)

# Strategic Recommendations
st.markdown("#### Strategic Expansion Recommendations")

top1 = expansion_df.iloc[0]
top2 = expansion_df.iloc[1]
top3 = expansion_df.iloc[2]

rec1, rec2 = st.columns(2)

with rec1:
    info_box(
        f"<b>Priority 1: {top1['branch_city']}</b><br>"
        f"Score: {top1['expansion_score']:.3f} | Current: {int(top1['num_branches'])} branches<br>"
        f"Profit Margin: {top1['avg_profit_margin']:.1f}%<br><br>"
        f"<b>Action:</b> Aggressive expansion with Mall format (highest ROI)",
        kind="success"
    )

with rec2:
    info_box(
        f"<b>Priority 2: {top2['branch_city']}</b><br>"
        f"Score: {top2['expansion_score']:.3f} | Current: {int(top2['num_branches'])} branches<br>"
        f"Profit Margin: {top2['avg_profit_margin']:.1f}%<br><br>"
        f"<b>Action:</b> Phased expansion, validate market demand first",
        kind="info"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Saturation vs Profitability Matrix
st.markdown("#### Market Saturation vs Profitability Matrix")

fig_bubble = city_bubble(city_df)
st.plotly_chart(fig_bubble, use_container_width=True)
render_chart_explainer("Market Saturation vs Profitability Matrix", city_df, filters, stats, "Branch Performance & Expansion", "saturation_matrix")

info_box(
    "<b>Matrix Interpretation:</b><br>"
    "• Top-left: High margin + Low saturation = EXPAND<br>"
    "• Top-right: High margin + High saturation = DEFEND<br>"
    "• Bottom-left: Low margin + Low saturation = VALIDATE<br>"
    "• Bottom-right: Low margin + High saturation = OPTIMIZE",
    kind="info"
)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: CHANNEL STRATEGY BY LOCATION
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Channel Strategy for Expansion")

col_ch1, col_ch2 = st.columns([1.5, 1.5])

with col_ch1:
    st.markdown("#### Channel Mix by Branch Type")
    ch_type_df = channel_by_type(df)
    fig_ch = channel_stacked_bar(ch_type_df)
    st.plotly_chart(fig_ch, use_container_width=True)
    render_chart_explainer("Channel Mix by Branch Type", ch_type_df, filters, stats, "Branch Performance & Expansion", "channel_mix_type")

with col_ch2:
    st.markdown("#### Delivery Share by City")
    fig_delivery = delivery_share_city(city_performance(df), df)
    st.plotly_chart(fig_delivery, use_container_width=True)
    render_chart_explainer("Delivery Share by City", city_performance(df), filters, stats, "Branch Performance & Expansion", "delivery_share_city")

st.markdown("<br>", unsafe_allow_html=True)

col_ch_insight1, col_ch_insight2 = st.columns(2)

with col_ch_insight1:
    info_box(
        "<b>Channel Insights for Expansion:</b><br>"
        f"• <b>{top1['branch_city']} (Priority 1):</b><br>"
        f"  Delivery share: {df[df['branch_city']==top1['branch_city']]['delivery_percent'].mean():.1f}%<br>"
        f"  → Delivery-ready market<br><br>"
        f"• <b>{top2['branch_city']} (Priority 2):</b><br>"
        f"  Delivery share: {df[df['branch_city']==top2['branch_city']]['delivery_percent'].mean():.1f}%<br>"
        f"  → Customize channel mix",
        kind="info"
    )

with col_ch_insight2:
    info_box(
        "<b>Channel Recommendations:</b><br>"
        "• <b>Mall format:</b> Focus on takeaway (high foot traffic)<br>"
        "• <b>Stand Alone:</b> Maximize dine-in (comfortable seating)<br>"
        "• <b>Delivery-ready cities:</b> Invest in 3rd-party partnerships<br>"
        "• <b>Growing delivery trend:</b> Prepare infrastructure early",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# RISK ASSESSMENT
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Expansion Risk Assessment")

risk_col1, risk_col2, risk_col3 = st.columns(3)

with risk_col1:
    info_box(
        "🔴 <b>High Risk:</b><br>"
        f"{worst_type['branch_type']} format<br>"
        f"Margin: {worst_type['avg_profit_margin']:.1f}%<br>"
        "Action: Fix profitability first before expansion",
        kind="danger"
    )

with risk_col2:
    info_box(
        "🟡 <b>Medium Risk:</b><br>"
        "Market saturation in Jakarta<br>"
        "(Already 12 branches)<br>"
        "Action: Focus on underserved locations",
        kind="warning"
    )

with risk_col3:
    info_box(
        "🟢 <b>Low Risk:</b><br>"
        f"{best_type['branch_type']} format<br>"
        f"Margin: {best_type['avg_profit_margin']:.1f}%<br>"
        "Action: Prioritize this format in expansions",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Business Development Copilot ──────────────────────────────────────────

suggested_q = [
    f"Kapan harus buka cabang di {top1['branch_city']}?",
    "Tipe cabang apa yang paling profitable?",
    "Bagaimana mitigasi risiko ekspansi?",
    f"Kenapa {worst_type['branch_type']} margin negative?",
]

render_business_copilot(
    filters=filters,
    stats=stats,
    page_name="Branch Performance & Expansion",
    suggested_questions=suggested_q,
)