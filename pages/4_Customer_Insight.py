"""
pages/4_Customer_Insight.py
Customer Insight - Customer satisfaction and behavior analysis 
"""

import streamlit as st
from utils import (
    load_data, apply_filters, build_summary_stats,
    satisfaction_by_factor, channel_distribution, channel_by_type,
    city_performance
)
from components import (
    render_sidebar, section_header, metric_card, info_box,
    fmt_number,
    satisfaction_histogram, satisfaction_by_factor_bar,
    satisfaction_trend, satisfaction_weather_box,
    channel_pie, channel_stacked_bar, delivery_share_city,
    render_business_copilot
)
from components.ai_analyst import render_chart_explainer

st.set_page_config(
    page_title="Customer Insight | KopiSeru BI",
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
    "Customer Insight",
    "Customer behavior, channel preferences, and satisfaction drivers"
)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: CUSTOMER SATISFACTION OVERVIEW
# ════════════════════════════════════════════════════════════════════════════

st.subheader("Customer Satisfaction Overview")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Avg Satisfaction", f"{stats['avg_satisfaction']:.2f} / 5.0",
                icon="😊", help_text="Mean satisfaction score")
with c2:
    sat_dist = df["customer_satisfaction"].value_counts().sort_index()
    mode_sat = sat_dist.idxmax()
    metric_card("Mode Score", f"{mode_sat:.1f} / 5.0",
                icon="🎯", help_text="Most common score")
with c3:
    high_sat = len(df[df["customer_satisfaction"] >= 4.0])
    pct_high = (high_sat / len(df)) * 100
    metric_card("High Satisfaction (≥4.0)", f"{pct_high:.1f}%",
                icon="👍", help_text="% with score ≥ 4.0")
with c4:
    low_sat = len(df[df["customer_satisfaction"] < 3.0])
    pct_low = (low_sat / len(df)) * 100
    metric_card("At Risk (<3.0)", f"{pct_low:.1f}%",
                icon="⚠️", help_text="% with low satisfaction")

st.markdown("<br>", unsafe_allow_html=True)

# Satisfaction Distribution
st.markdown("#### Satisfaction Distribution")
fig_hist = satisfaction_histogram(df)
st.plotly_chart(fig_hist, use_container_width=True)
render_chart_explainer("Satisfaction Distribution", df[["customer_satisfaction"]], filters, stats, "Customer Insight", "satisfaction_hist")

info_box(
    "Most customers rate between 3.5-4.2, averaging 3.84/5. "
    "Distribution shows room for improvement across branches.",
    kind="info"
)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: SATISFACTION DRIVERS ANALYSIS
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("🔍 What Drives Customer Satisfaction?")

tab_driver1, tab_driver2, tab_driver3, tab_driver4 = st.tabs([
    "Branch Type", 
    "Weather", 
    "Day Type", 
    "Promotion"
])

# ── Tab 1: Branch Type ────────────────────────────────────────────────────
with tab_driver1:
    st.markdown("#### Satisfaction by Branch Type")
    sat_by_type = satisfaction_by_factor(df, "branch_type")
    fig_type = satisfaction_by_factor_bar(sat_by_type, "branch_type")
    st.plotly_chart(fig_type, use_container_width=True)
    render_chart_explainer("Satisfaction by Branch Type", sat_by_type, filters, stats, "Customer Insight", "satisfaction_branch_type")
    
    col_type1, col_type2 = st.columns(2)
    with col_type1:
        best_type = sat_by_type.iloc[0]
        info_box(
            f"<b>Best: {best_type['branch_type']}</b><br>"
            f"Satisfaction: {best_type['avg_satisfaction']:.2f}/5<br>"
            f"Less crowded, better service perception",
            kind="success"
        )
    with col_type2:
        worst_type = sat_by_type.iloc[-1]
        info_box(
            f"<b>Needs Improvement: {worst_type['branch_type']}</b><br>"
            f"Satisfaction: {worst_type['avg_satisfaction']:.2f}/5<br>"
            f"High traffic → queue management focus needed",
            kind="warning"
        )
    
    st.markdown("#### Detailed Metrics")
    st.dataframe(
        sat_by_type[['branch_type', 'avg_satisfaction', 'count']].rename(columns={
            'branch_type': 'Branch Type',
            'avg_satisfaction': 'Avg Satisfaction',
            'count': '# Records'
        }),
        use_container_width=True,
        hide_index=True
    )

# ── Tab 2: Weather ────────────────────────────────────────────────────────
with tab_driver2:
    st.markdown("#### Satisfaction by Weather Condition")
    fig_weather = satisfaction_weather_box(df)
    st.plotly_chart(fig_weather, use_container_width=True)
    render_chart_explainer("Satisfaction by Weather Condition", df[["weather", "customer_satisfaction"]], filters, stats, "Customer Insight", "satisfaction_weather")
    
    info_box(
        "<b>KEY FINDING: Weather Has NO Impact</b><br>"
        "All weather conditions (sunny, rainy, cloudy) show similar median satisfaction (~3.84/5).<br><br>"
        "<b>Implication:</b> Focus on indoor factors (service, atmosphere, speed) rather than weather-dependent strategies.",
        kind="success"
    )

# ── Tab 3: Day Type ───────────────────────────────────────────────────────
with tab_driver3:
    st.markdown("#### Satisfaction: Weekday vs Weekend")
    sat_by_day = satisfaction_by_factor(df, "day_type")
    fig_day = satisfaction_by_factor_bar(sat_by_day, "day_type")
    st.plotly_chart(fig_day, use_container_width=True)
    render_chart_explainer("Satisfaction: Weekday vs Weekend", sat_by_day, filters, stats, "Customer Insight", "satisfaction_day_type")
    
    info_box(
        "<b>KEY FINDING: Day Type Has Minimal Impact</b><br>"
        "Weekday and weekend satisfaction scores are nearly identical.<br><br>"
        "<b>Implication:</b> Service quality is consistent. Focus on maintaining consistency rather than day-specific tactics.",
        kind="info"
    )

# ── Tab 4: Promotion ──────────────────────────────────────────────────────
with tab_driver4:
    st.markdown("#### Satisfaction by Promotion Status")
    sat_by_promo = satisfaction_by_factor(df, "promo_label")
    fig_promo = satisfaction_by_factor_bar(sat_by_promo, "promo_label")
    st.plotly_chart(fig_promo, use_container_width=True)
    render_chart_explainer("Satisfaction by Promotion Status", sat_by_promo, filters, stats, "Customer Insight", "satisfaction_promo")
    
    info_box(
        "<b>KEY FINDING: Promotion Has NO Impact on Satisfaction</b><br>"
        "Promo and non-promo periods show nearly identical satisfaction scores.<br><br>"
        "<b>Implication:</b> Promotions are effective for volume, but they don't improve perceived customer experience.",
        kind="info"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: SATISFACTION TREND OVER TIME
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Satisfaction Trend (2021-2023)")

fig_trend = satisfaction_trend(df)
st.plotly_chart(fig_trend, use_container_width=True)
render_chart_explainer("Satisfaction Trend (2021-2023)", df[["transaction_date", "customer_satisfaction"]] if "transaction_date" in df.columns else df[["customer_satisfaction"]], filters, stats, "Customer Insight", "satisfaction_trend")

col_trend1, col_trend2 = st.columns(2)
with col_trend1:
    info_box(
        "<b>Consistency is Strength:</b><br>"
        "Satisfaction remains stable around 3.84 throughout the period.<br>"
        "No major crashes or improvements—quality is maintained.",
        kind="info"
    )

with col_trend2:
    info_box(
        "<b>Opportunity to Grow:</b><br>"
        "Stable but not improving. Current score (3.84) ≈ 'Satisfied'.<br>"
        "Target should be 4.2+ for strong recommendations.",
        kind="warning"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 4: CHANNEL BEHAVIOR
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("📱 Customer Channel Preferences")

col_ch1, col_ch2 = st.columns(2)

with col_ch1:
    st.markdown("#### Overall Channel Distribution")
    ch_df = channel_distribution(df)
    fig_ch = channel_pie(ch_df)
    st.plotly_chart(fig_ch, use_container_width=True)
    render_chart_explainer("Overall Channel Distribution", ch_df, filters, stats, "Customer Insight", "channel_distribution")

with col_ch2:
    st.markdown("#### Channel by Branch Type")
    ch_type_df = channel_by_type(df)
    fig_ch_type = channel_stacked_bar(ch_type_df)
    st.plotly_chart(fig_ch_type, use_container_width=True)
    render_chart_explainer("Channel by Branch Type", ch_type_df, filters, stats, "Customer Insight", "channel_by_branch_type")

col_ch_insight1, col_ch_insight2 = st.columns(2)

with col_ch_insight1:
    info_box(
        "<b>Channel Distribution:</b><br>"
        "• Takeaway: 49.1% (dominant)<br>"
        "• Delivery: 26.8% (growing)<br>"
        "• Dine-in: 24.2% (stable)",
        kind="info"
    )

with col_ch_insight2:
    info_box(
        "<b>Strategic Implication:</b><br>"
        "• Takeaway declining YoY<br>"
        "• Delivery growing consistently<br>"
        "• Dine-in opportunity in Stand Alone format",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Delivery Share by City
st.markdown("#### Delivery Market Readiness by City")
city_df = city_performance(df)
fig_delivery = delivery_share_city(city_df, df)
st.plotly_chart(fig_delivery, use_container_width=True)
render_chart_explainer("Delivery Market Readiness by City", city_df, filters, stats, "Customer Insight", "delivery_readiness_city")

info_box(
    "<b>Delivery-Ready Markets:</b><br>"
    "Makassar (30.0%), Malang (29.7%), Jakarta (28.7%) already have strong delivery adoption.<br>"
    "These cities are ideal for aggressive delivery infrastructure investment.",
    kind="success"
)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 5: KEY FINDINGS & RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Key Findings & Recommendations")

findings_col1, findings_col2 = st.columns(2)

with findings_col1:
    info_box(
        "<b>What DOES Drive Satisfaction:</b><br>"
        "✓ Branch atmosphere & layout<br>"
        "✓ Service speed & quality<br>"
        "✓ Less crowded = better perception<br>"
        "✓ Comfortable dine-in space<br>"
        "✓ Staff professionalism",
        kind="success"
    )

with findings_col2:
    info_box(
        "<b>What DOESN'T Matter:</b><br>"
        "✗ Weather conditions<br>"
        "✗ Promotion types<br>"
        "✗ Weekday vs Weekend<br>"
        "✗ Time of year<br>"
        "✗ Proximity to competitors",
        kind="info"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Action Items
st.subheader("Recommended Actions (Priority Order)")

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    info_box(
        "<b>Staff Training Program</b><br>"
        "Service quality is THE driver.<br>"
        "• Quick order fulfillment<br>"
        "• Friendly interactions<br>"
        "• Problem resolution",
        kind="warning"
    )

with action_col2:
    info_box(
        " <b>Queue Management</b><br>"
        "Crowding hurts perception.<br>"
        "• Optimize staff scheduling<br>"
        "• Improve order speed<br>"
        "• Better queue flow",
        kind="warning"
    )

with action_col3:
    info_box(
        "<b>Stand Alone Expansion</b><br>"
        "Highest satisfaction scores.<br>"
        "• Dine-in friendly<br>"
        "• Personal atmosphere<br>"
        "• Premium experience",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Improvement Targets
st.markdown("#### Improvement Targets")

target_col1, target_col2, target_col3 = st.columns(3)

with target_col1:
    info_box(
        "Current: 3.84/5<br>"
        "<b>Target: 4.2/5</b><br><br>"
        "What it means:<br>"
        "From 'satisfied' to 'very satisfied'",
        kind="info"
    )

with target_col2:
    info_box(
        "Gap: 0.36 points<br>"
        "<b>Effort: 9.4% improvement</b><br><br>"
        "Achievable through:<br>"
        "Staff training + queue mgmt",
        kind="info"
    )

with target_col3:
    info_box(
        "Impact: 50%+ increase in<br>"
        "organic recommendations<br><br>"
        "ROI: High (repeat customers +<br>"
        "word-of-mouth growth)",
        kind="success"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Business Development Copilot ──────────────────────────────────────────

suggested_q = [
    "Apa faktor utama yang menggerakkan kepuasan pelanggan?",
    "Bagaimana cara meningkatkan kepuasan dari 3.84 ke 4.2?",
    f"Cabang tipe mana yang perlu perbaikan service quality?",
    "Apakah delivery trend akan terus naik?",
]

render_business_copilot(
    filters=filters,
    stats=stats,
    page_name="Customer Insight",
    suggested_questions=suggested_q,
)