"""
components/charts.py
All Plotly chart functions for KopiSeru Dashboard.
Each function returns a go.Figure ready for st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_loader import COLORS, MONTH_ORDER, BRANCH_TYPE_ORDER
from .cards import fmt_currency

#  Shared layout defaults 
def _base_layout(**kwargs) -> dict:
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color=COLORS["text"], size=12),
        margin=dict(l=34, r=10, t=24, b=60),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
            orientation="h",
            yanchor="top",
            y=-0.38,
            xanchor="center",
            x=0.5,
        ),
    )
    base.update(kwargs)
    return base


def _axis_style(title: str = "", gridcolor: str = "#EEE") -> dict:
    return dict(
        title=dict(text=title, font=dict(size=12)),
        gridcolor=gridcolor,
        gridwidth=0.5,
        showline=True,
        linecolor="#DDD",
        linewidth=1,
        ticks="outside",
        tickfont=dict(size=12),
    )


# 1. Revenue Trend Line 

def revenue_trend(monthly_df: pd.DataFrame) -> go.Figure:
    """Monthly revenue trend split by year."""
    fig = go.Figure()
    colors = [COLORS["primary"], COLORS["accent"], COLORS["success"]]
    for i, yr in enumerate(sorted(monthly_df["year"].unique())):
        d = monthly_df[monthly_df["year"] == yr].sort_values("month")
        fig.add_trace(go.Scatter(
            x=d["month_label"], y=d["total_revenue"],
            name=str(yr),
            mode="lines+markers",
            line=dict(color=colors[i % len(colors)], width=2.5),
            marker=dict(size=6),
            hovertemplate="<b>%{x} %{fullData.name}</b><br>Revenue: Rp %{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        title="Monthly Revenue Trend (All Branches)",
        xaxis=_axis_style("Month"),
        yaxis=_axis_style("Total Revenue (Rp)"),
        **_base_layout(height=185),
    )
    return fig


def revenue_yoy_bar(yoy: dict) -> go.Figure:
    """YoY growth bar chart."""
    years = list(yoy.keys())
    vals  = list(yoy.values())
    colors = [COLORS["success"] if v >= 0 else COLORS["danger"] for v in vals]
    fig = go.Figure(go.Bar(
        x=[str(y) for y in years],
        y=vals,
        marker_color=colors,
        text=[f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%" for v in vals],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>YoY Growth: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="Year-on-Year Revenue Growth (%)",
        xaxis=_axis_style("Year"),
        yaxis=_axis_style("Growth (%)"),
        **_base_layout(height=300),
    )
    fig.add_hline(y=0, line_color="#999", line_dash="dot")
    return fig


# 2. Promo Charts 

def promo_boxplot(df: pd.DataFrame) -> go.Figure:
    """Revenue distribution: Promo vs Non-Promo box plot."""
    fig = go.Figure()
    for label, color in [("Promo", COLORS["accent"]), ("Non-Promo", COLORS["secondary"])]:
        d = df[df["promo_label"] == label]["total_revenue"]
        fig.add_trace(go.Box(
            y=d, name=label,
            marker_color=color,
            boxmean="sd",
            hovertemplate="<b>" + label + "</b><br>Revenue: Rp %{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        title="Revenue Distribution: Promo vs Non-Promo",
        yaxis=_axis_style("Total Revenue (Rp)"),
        **_base_layout(height=185),
    )
    return fig


def promo_avg_revenue(df: pd.DataFrame) -> go.Figure:
    """Bar chart of average revenue per promo type. Accepts raw df."""
    d = (
        df.groupby("promo_type", as_index=False)["total_revenue"]
        .mean()
        .rename(columns={"total_revenue": "avg_revenue"})
        .sort_values("avg_revenue", ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=d["avg_revenue"], y=d["promo_type"],
        orientation="h",
        marker_color=COLORS["accent"],
        text=[f"Rp {v/1e6:.1f} M" for v in d["avg_revenue"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Revenue: Rp %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title="Average Revenue per Promo Type",
        xaxis=_axis_style("Avg Revenue (Rp)"), 
        yaxis=dict(title="", tickfont=dict(size=12)),
        **_base_layout(height=320),
    )
    return fig


# 3. Transactions vs Revenue

def txn_vs_revenue_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter: transactions vs revenue, coloured by avg_ticket_size."""
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample,
        x="total_transactions", y="total_revenue",
        color="avg_ticket_size",
        color_continuous_scale=[[0, COLORS["accent2"]], [1, COLORS["primary"]]],
        labels={
            "total_transactions": "Total Transactions",
            "total_revenue":      "Total Revenue (Rp)",
            "avg_ticket_size":    "Avg Ticket Size (Rp)",
        },
        hover_data=["branch_name", "branch_city", "date"],
        title="Transactions vs Revenue (colour = Avg Ticket Size)",
    )
    fig.update_traces(marker=dict(size=8, opacity=0.65))
    fig.update_layout(
        **_base_layout(height=190),
        coloraxis_colorbar=dict(
            title=dict(text="Avg Ticket (Rp)", font=dict(size=12)),
            thickness=10,
            len=0.65,
            tickfont=dict(size=12),
            x=1.0,
        ),
    )
    return fig


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    """Correlation heatmap for key numeric columns."""
    labels = ["Transactions", "Revenue", "Avg Ticket", "Cups Sold", "Profit"]
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        colorscale=[[0, COLORS["bg"]], [0.5, COLORS["accent2"]], [1, COLORS["primary"]]],
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hovertemplate="<b>%{x} × %{y}</b><br>Corr: %{z:.2f}<extra></extra>",
        zmin=-1, zmax=1,
    ))
    fig.update_layout(
        title="Correlation Heatmap — Revenue & Transactions",
        **_base_layout(height=380),
    )
    return fig


# 4. Weekday vs Weekend 

def weekday_bar(ww_df: pd.DataFrame, metric: str = "avg_revenue",
                title: str = "Weekday vs Weekend", fmt: str = "currency") -> go.Figure:
    """Grouped bar for weekday vs weekend comparison."""
    colors = [COLORS["primary"], COLORS["accent"]]
    texts = []
    for v in ww_df[metric]:
        if fmt == "currency":
            texts.append(f"Rp {v/1e6:.1f} M")
        elif fmt == "pct":
            texts.append(f"{v:.1f}%")
        else:
            texts.append(f"{v:,.0f}")

    fig = go.Figure(go.Bar(
        x=ww_df["day_type"],
        y=ww_df[metric],
        marker_color=colors[:len(ww_df)],
        text=texts,
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>" + title + ": %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        yaxis=_axis_style(),
        hovermode="closest",
        **_base_layout(height=300),
    )
    return fig


# 5. City & Branch Performance 
def city_profit_bar(city_df: pd.DataFrame) -> go.Figure:
    """Total profit per city horizontal bar."""
    d = city_df.sort_values("total_profit", ascending=True)
    _max = max(list(d["total_profit"]) or [0])
    fig = go.Figure(go.Bar(
        x=d["total_profit"], y=d["branch_city"],
        orientation="h",
        marker_color=COLORS["primary"],
        text=[f"Rp {v/1e6:.2f} M" for v in d["total_profit"]],
        textposition="outside",
        customdata=d["num_branches"],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Total Profit: Rp%{x:,.0f}<br>"
            "Branches: %{customdata}<extra></extra>"
        ),
    ))
    fig.update_layout(
        title="Total Profit per City (2021–2023)",
        xaxis=_axis_style("Total Profit (Rp)"),
        yaxis=dict(title="", tickfont=dict(size=13)),
        **_base_layout(height=400),
    )
    fig.update_xaxes(range=[0, _max * 1.22])
    return fig

def branch_type_margin_bar(bt_df: pd.DataFrame) -> go.Figure:
    """Average profit margin per branch type."""
    bt_df = bt_df.sort_values("avg_profit_margin", ascending=False)
    colors = [
        COLORS["secondary"] if v >= 0 else COLORS["danger"]
        for v in bt_df["avg_profit_margin"]
    ]
    fig = go.Figure(go.Bar(
        x=bt_df["branch_type"],
        y=bt_df["avg_profit_margin"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in bt_df["avg_profit_margin"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Avg Margin: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="#999", line_dash="dot")
    fig.update_layout(
        title="Average Profit Margin (%) per Branch Type",
        yaxis=_axis_style("Profit Margin (%)"),
        **_base_layout(height=185),
    )
    return fig


def city_bubble(city_df: pd.DataFrame, expansion_df: pd.DataFrame = None) -> go.Figure:
    """Bubble chart styled as an expansion opportunity matrix:
    x = saturation (num branches), y = profitability (avg margin),
    bubble size = avg revenue/branch, bubble color = expansion score.
    """
    fig = go.Figure()

    # Bring in expansion_score for color mapping (data/calculation itself is
    # untouched — this only merges an existing metric in for visualization).
    if expansion_df is not None and "expansion_score" in expansion_df.columns:
        merged = city_df.merge(
            expansion_df[["branch_city", "expansion_score"]],
            on="branch_city", how="left",
        )
    else:
        merged = city_df.copy()
        merged["expansion_score"] = 0.5

    # Area-proportional bubble sizing (sizemode="area") instead of diameter-linear
    # sizing: with the default sizemode, a 2x value looks ~4x bigger to the eye
    # because diameter scales linearly while perceived size is area-based. Using
    # sizemode="area" + sizeref maps value -> area directly, which is the
    # standard approach for professional BI bubble charts.
    DESIRED_MAX_DIAMETER = 28
    SIZE_MIN_FLOOR = 4  # visibility floor for the smallest bubble, not a manual range
    rev = merged["revenue_per_branch"]
    rev_max = rev.max()
    sizeref = 2.0 * rev_max / (DESIRED_MAX_DIAMETER ** 2)
    sizes = rev  

    fig.add_trace(go.Scatter(
        x=merged["num_branches"],
        y=merged["avg_profit_margin"],
        mode="markers",
        marker=dict(
            size=sizes,
            sizemode="area",
            sizeref=sizeref,
            sizemin=SIZE_MIN_FLOOR,
            color=merged["expansion_score"],
            colorscale="YlOrBr",
            cmin=0, cmax=1,
            opacity=0.75,
            line=dict(color="rgba(70,50,30,.45)", width=1),
            showscale=True,
            colorbar=dict(
                title=dict(text="Expansion Score<br><span style='font-size:6px'> </span>", font=dict(size=14)),
                thickness=10,
                len=0.85,
                x=1.04,
                tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                tickfont=dict(size=14),
                outlinewidth=0,
            ),
        ),
        customdata=merged[[
            "branch_city", "num_branches", "avg_profit_margin",
            "revenue_per_branch", "expansion_score",
        ]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Branches: %{customdata[1]}<br>"
            "Avg Margin: %{customdata[2]:.1f}%<br>"
            "Revenue/branch: Rp %{customdata[3]:,.0f}<br>"
            "Expansion Score: %{customdata[4]:.3f}<extra></extra>"
        ),
        showlegend=False,
    ))

    x_med = merged["num_branches"].median()
    y_med = merged["avg_profit_margin"].median()

    def _textposition(x_val, y_val) -> str:
        vert = "top" if y_val >= y_med else "bottom"
        horiz = "right" if x_val >= x_med else "left"
        return f"{vert} {horiz}"

    label_text = [row["branch_city"] for _, row in merged.iterrows()]
    label_positions = [
        _textposition(row["num_branches"], row["avg_profit_margin"])
        for _, row in merged.iterrows()
    ]

    fig.data[0].update(
        mode="markers+text",
        text=label_text,
        textposition=label_positions,
        textfont=dict(size=11, color=COLORS["text"]),
    )

    fig.data[0].update(cliponaxis=False)

    x_max = merged["num_branches"].max()
    y_min = merged["avg_profit_margin"].min()
    y_max = merged["avg_profit_margin"].max()

    fig.update_layout(
        title="Saturation vs Profitability (bubble size = avg revenue/branch, color = expansion score)",
        xaxis=dict(tickmode="linear", dtick=2, range=[1, x_max + 2],
                   **_axis_style("Number of Branches (Saturation)")),
        yaxis=dict(range=[y_min - 2, y_max + 4],
                   **_axis_style("Avg Profit Margin (%)")),
        showlegend=False,
        **_base_layout(height=430, margin=dict(l=70, r=90, t=40, b=60)),
    )
    return fig


#  6. Expansion 

def expansion_bar(exp_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar for expansion score per city."""
    d = exp_df.sort_values("expansion_score", ascending=True)
    colors = [COLORS["accent"] if v >= 0.6 else COLORS["secondary"]
              for v in d["expansion_score"]]
    fig = go.Figure(go.Bar(
        x=d["expansion_score"],
        y=d["branch_city"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.3f}" for v in d["expansion_score"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Expansion Score: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title="Expansion Potential Score per City (Profitability + Low Saturation)",
        xaxis=dict(range=[0, 1], **_axis_style("Score (0–1)")),
        yaxis=dict(title="", tickfont=dict(size=12)),
        **_base_layout(height=380),
    )
    return fig


#  7. Channel Charts 

def channel_pie(ch_df: pd.DataFrame) -> go.Figure:
    """Pie chart of overall channel distribution."""
    colors = [COLORS["channel"].get(c, COLORS["accent"]) for c in ch_df["channel"]]
    fig = go.Figure(go.Pie(
        labels=ch_df["channel"],
        values=ch_df["pct"],
        marker_colors=colors,
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Share: %{percent}<extra></extra>",
        hole=0.35,
    ))
    fig.update_layout(
        title="Transaction Channel Distribution (Overall)",
        **_base_layout(height=185),
    )
    return fig


def channel_stacked_bar(ch_type_df: pd.DataFrame) -> go.Figure:
    """Stacked bar: channel distribution per branch type."""
    fig = go.Figure()
    for ch, col in [("Dine-in", "dine_in"), ("Delivery", "delivery"), ("Takeaway", "takeaway")]:
        fig.add_trace(go.Bar(
            name=ch,
            x=ch_type_df["branch_type"],
            y=ch_type_df[col],
            marker_color=COLORS["channel"][ch],
            hovertemplate="<b>%{x}</b><br>" + ch + ": %{y:.1f}%<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        title="Channel Distribution per Branch Type",
        yaxis=_axis_style("Percentage (%)"),
        **_base_layout(height=360),
    )
    return fig


def channel_trend_line(ct_df: pd.DataFrame) -> go.Figure:
    """Line chart of channel share trend by year."""
    fig = go.Figure()
    for ch, col, color in [
        ("Dine-in",  "dine_in",  COLORS["primary"]),
        ("Delivery", "delivery", COLORS["secondary"]),
        ("Takeaway", "takeaway", COLORS["accent"]),
    ]:
        fig.add_trace(go.Scatter(
            x=ct_df["year"].astype(str), y=ct_df[col],
            name=ch, mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>" + ch + ": %{y:.1f}%<extra></extra>",
        ))
    fig.update_layout(
        title="Channel Trend per Year",
        yaxis=_axis_style("Percentage (%)"),
        **_base_layout(height=320),
    )
    return fig


def delivery_share_city(city_df: pd.DataFrame, full_df: pd.DataFrame) -> go.Figure:
    """Delivery share per city vs overall average."""
    city_del = (
        full_df.groupby("branch_city", as_index=False)
        .agg(delivery_share=("delivery_percent", "mean"))
        .sort_values("delivery_share", ascending=False)
    )
    avg = city_del["delivery_share"].mean()
    colors = [
        COLORS["accent"] if v >= avg else COLORS["secondary"]
        for v in city_del["delivery_share"]
    ]
    fig = go.Figure(go.Bar(
        x=city_del["branch_city"],
        y=city_del["delivery_share"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in city_del["delivery_share"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Delivery Share: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=avg, line_color=COLORS["danger"], line_dash="dash",
                  annotation_text=f"Avg {avg:.1f}%", annotation_position="top right")
    fig.update_layout(
        title="Average Delivery Share per City",
        yaxis=_axis_style("Delivery Share (%)"),
        **_base_layout(height=340),
    )
    return fig


#  8. Customer Satisfaction 

def satisfaction_histogram(df: pd.DataFrame) -> go.Figure:
    """Distribution histogram of customer satisfaction scores."""
    mean_val = df["customer_satisfaction"].mean()
    fig = go.Figure(go.Histogram(
        x=df["customer_satisfaction"],
        nbinsx=30,
        marker=dict(
            color=COLORS["accent"],
            line=dict(
                color=COLORS["text"],   
                width=1.5
            )
        ),
        opacity=0.85,
        hovertemplate="Score: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=mean_val, line_color=COLORS["babubabu"], line_dash="dash",
                  annotation_text=f"Mean: {mean_val:.2f}",
                  annotation_position="top")
    fig.update_layout(
        title="Customer Satisfaction Score Distribution",
        xaxis=_axis_style("Satisfaction Score (1–5)"),
        yaxis=_axis_style("Count"),
        **_base_layout(height=340),
    )
    return fig


def satisfaction_branch_box(data: pd.DataFrame) -> go.Figure:
    """Box plot of satisfaction distribution per branch type (dark→light fills)."""
    order = ["Office Area", "Mall", "Stand Alone", "University"]
    types = [t for t in order if t in data["branch_type"].unique()]
    fills = ["#3B2410", "#6B4B2A", "#BFA163", "#EBD9A8"]
    fig = go.Figure()
    for i, btype in enumerate(types):
        vals = data[data["branch_type"] == btype]["customer_satisfaction"]
        fig.add_trace(go.Box(
            y=vals, name=btype,
            fillcolor=fills[i % len(fills)],
            line=dict(color="#2C1A0E", width=1.1),
            marker=dict(color="#2C1A0E", size=4),
            boxpoints="outliers",
        ))
    fig.update_layout(showlegend=False)
    return fig


def satisfaction_promo_bar(sat_df: pd.DataFrame) -> go.Figure:
    """Vertical gradient bars of avg satisfaction per promo type (dark→light)."""
    d = sat_df.sort_values("avg_satisfaction", ascending=False).reset_index(drop=True)
    cats = d.iloc[:, 0].tolist()
    vals = d["avg_satisfaction"].tolist()
    shades = ["#4A2E16", "#6B4423", "#8B6B3D", "#B3934F", "#D4B571", "#EAD9A6"]
    colors = [shades[i % len(shades)] for i in range(len(cats))]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cats, y=vals,
        marker=dict(color=colors, line=dict(color=COLORS["text"], width=0.8)),
        width=0.56,
        text=[f"{v:.2f}" for v in vals],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text"]),
        hovertemplate="<b>%{x}</b><br>Avg Satisfaction: %{y:.2f}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        title="Average Satisfaction by Promo Type",
        xaxis=dict(tickfont=dict(size=14)), 
        yaxis=_axis_style("Avg Satisfaction"),
        **_base_layout(height=300),
    )
    return fig


def satisfaction_by_factor_bar(sat_df: pd.DataFrame, factor_label: str) -> go.Figure:
    """Bar chart of avg satisfaction by a given factor."""
    d = sat_df.sort_values("avg_satisfaction", ascending=True)
    fig = go.Figure(go.Bar(
        x=d["avg_satisfaction"],
        y=d.iloc[:, 0],    # first column = factor
        orientation="h",
        marker_color=COLORS["accent"],
        text=[f"{v:.2f}" for v in d["avg_satisfaction"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Satisfaction: %{x:.2f}<extra></extra>",
    ))
    min_x = max(0, d["avg_satisfaction"].min() - 0.2)
    fig.update_layout(
        title=f"Avg Satisfaction by {factor_label}",
        xaxis=dict(range=[min_x, 5], **_axis_style("Avg Satisfaction Score")),
        yaxis=dict(title="", tickfont=dict(size=12)),
        **_base_layout(height=300),
    )
    return fig


def satisfaction_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly avg satisfaction on a continuous timeline, colored per year."""
    g = (
        df.groupby(["year", "month"], as_index=False)
        .agg(avg_sat=("customer_satisfaction", "mean"))
    )
    g["date"] = pd.to_datetime(dict(year=g["year"], month=g["month"], day=1))
    g = g.sort_values("date")
    overall_mean = df["customer_satisfaction"].mean()

    year_colors = [COLORS["primary"], COLORS["accent"], COLORS["success"]]

    fig = go.Figure()
    for i, yr in enumerate(sorted(g["year"].unique())):
        d = g[g["year"] == yr]
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["avg_sat"],
            name=str(yr),
            mode="lines+markers",
            line=dict(color=year_colors[i % len(year_colors)], width=2),
            marker=dict(size=6),
            hovertemplate="%{x|%Y-%m}<br>Avg Satisfaction: %{y:.2f}<extra></extra>",
        ))
    xmin, xmax = g["date"].min(), g["date"].max()
    fig.add_trace(go.Scatter(
        x=[xmin, xmax], y=[overall_mean, overall_mean],
        mode="lines", name="Overall Mean",
        line=dict(color="#999", dash="dash", width=1.3),
        hovertemplate=f"Overall Mean: {overall_mean:.2f}<extra></extra>",
    ))

    layout = _base_layout(height=340)
    # legend outside the plot area (right side) so it never overlaps the lines
    layout["legend"] = dict(
        title=dict(text="Year", font=dict(size=10)),
        font=dict(size=12),
        orientation="v",
        yanchor="top", y=1.0, xanchor="left", x=1.01,
    )
    fig.update_layout(
        title=dict(text="<b>Monthly Average Customer Satisfaction Trend</b>",
                   font=dict(size=14, color=COLORS["text"]), x=0.5, xanchor="center"),
        xaxis=dict(type="date", dtick="M4", tickformat="%Y-%m",
                   tickangle=0, **_axis_style("")),
        yaxis=dict(range=[1, 5.5], dtick=0.5, **_axis_style("Avg Satisfaction Score")),
        **layout,
    )
    return fig


def satisfaction_weather_box(df: pd.DataFrame) -> go.Figure:
    """Box plot of satisfaction per weather type."""
    fig = go.Figure()
    colors = [COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["warning"]]
    for i, weather in enumerate(df["weather"].unique()):
        d = df[df["weather"] == weather]["customer_satisfaction"]
        q1, median, q3 = d.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        upper_fence = min(d.max(), q3 + 1.5 * iqr)
        lower_fence = max(d.min(), q1 - 1.5 * iqr)
        mean, std = d.mean(), d.std()

        # A single combined hoverlabel (instead of Plotly's default
        # per-statistic callouts) so the hover box behaves like a normal
        # tooltip and doesn't get anchored off-screen to the right for
        # the last category.
        hover_text = (
            f"<b>{weather}</b><br>"
            f"Max: {d.max():.1f}<br>"
            f"Upper fence: {upper_fence:.1f}<br>"
            f"Q3: {q3:.1f}<br>"
            f"Median: {median:.1f}<br>"
            f"Mean ± σ: {mean:.2f} ± {std:.2f}<br>"
            f"Q1: {q1:.1f}<br>"
            f"Lower fence: {lower_fence:.1f}<br>"
            f"Min: {d.min():.1f}"
        )
        fig.add_trace(go.Box(
            y=d, name=weather,
            marker_color=colors[i % len(colors)],
            boxmean="sd",
            hoveron="boxes",
            hovertemplate=hover_text + "<extra></extra>",
        ))
    fig.update_layout(
        title="Customer Satisfaction per Weather",
        yaxis=_axis_style("Satisfaction Score"),
        hovermode="closest",
        hoverlabel=dict(align="left"),
        **_base_layout(height=340),
    )
    return fig