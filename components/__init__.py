from .sidebar import render_sidebar
from .cards import (
    metric_card, section_header, info_box,
    ai_insight_card, fmt_currency, fmt_number
)
from .charts import (
    revenue_trend, revenue_yoy_bar,
    promo_boxplot, promo_avg_revenue,
    txn_vs_revenue_scatter, correlation_heatmap,
    weekday_bar,
    city_profit_bar, branch_type_margin_bar, city_bubble,
    expansion_bar,
    channel_pie, channel_stacked_bar, channel_trend_line, delivery_share_city,
    satisfaction_histogram, satisfaction_by_factor_bar,
    satisfaction_trend, satisfaction_weather_box,
)
from .ai_analyst import ask_ai, generate_page_insight, render_business_copilot