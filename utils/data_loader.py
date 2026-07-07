"""
utils/data_loader.py
Handles all data loading, caching, and preprocessing for KopiSeru Dashboard.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "kopiseru_clean_v4.csv"

MONTH_MAP = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

MONTH_ORDER = list(MONTH_MAP.values())

CITY_ORDER = [
    "Jakarta", "Surabaya", "Bandung", "Makassar",
    "Denpasar", "Malang", "Medan", "Yogyakarta", "Semarang"
]

BRANCH_TYPE_ORDER = ["Mall", "Office Area", "Stand Alone", "University"]

# ── KopiSeru brand palette ───────────────────────────────────────────────────
COLORS = {
    "primary":       "#5C3D1E",   # deep coffee brown
    "secondary":     "#8B5E3C",   # medium brown
    "accent":        "#D4A853",   # warm gold
    "accent2":       "#E8C07D",   # light gold
    "bg":            "#FDF6EC",   # cream
    "surface":       "#FFFFFF",
    "text":          "#2C1A0E",
    "text_muted":    "#7A6552",
    "success":       "#4CAF82",
    "danger":        "#C40C0C",
    "warning":       "#F5A623",
    "babubabu":        "#37583D",
    "krim": "#EBD9A8",    
    # chart palette
    "chart": [
        "#5C3D1E", "#8B5E3C", "#D4A853",
        "#4CAF82", "#E05252", "#6B8DD6",
        "#E8A838", "#A3C4BC",
    ],
    # branch type colours
    "branch": {
        "Mall":        "#5C3D1E",
        "Office Area": "#8B5E3C",
        "Stand Alone": "#D4A853",
        "University":  "#E05252",
    },
    # channel colours
    "channel": {
        "Takeaway": "#D4A853",
        "Delivery": "#8B5E3C",
        "Dine-in":  "#5C3D1E",
    },
}


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load and return the raw KopiSeru dataset."""
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = _preprocess(df)
    return df


def _preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all preprocessing steps once at load time."""
    # ensure correct dtypes
    df["date"]       = pd.to_datetime(df["date"])
    df["is_weekend"] = df["is_weekend"].astype(bool)
    df["promo_active"] = df["promo_active"].astype(bool)

    # derived columns
    df["day_type"]      = df["is_weekend"].map({True: "Weekend", False: "Weekday"})
    df["promo_label"]   = df["promo_active"].map({True: "Promo", False: "Non-Promo"})
    df["year_month"]    = df["date"].dt.to_period("M").astype(str)

    # normalise percentage columns (already 0-100 in source)
    for col in ["dine_in_percent", "delivery_percent", "takeaway_percent"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # profit margin guard (avoid inf)
    df["profit_margin"] = df["profit_margin"].replace([np.inf, -np.inf], np.nan)

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filters to dataframe. Returns filtered copy."""
    fdf = df.copy()

    if filters.get("years"):
        fdf = fdf[fdf["year"].isin(filters["years"])]
    if filters.get("months"):
        fdf = fdf[fdf["month"].isin(filters["months"])]
    if filters.get("cities"):
        fdf = fdf[fdf["branch_city"].isin(filters["cities"])]
    if filters.get("branch_types"):
        fdf = fdf[fdf["branch_type"].isin(filters["branch_types"])]
    if filters.get("promotions"):
        fdf = fdf[fdf["promo_type"].isin(filters["promotions"])]
    if filters.get("weathers"):
        fdf = fdf[fdf["weather"].isin(filters["weathers"])]
    if filters.get("channels"):
        # channel filter works by keeping rows where the named channel columns > 0
        channel_map = {
            "Takeaway": "takeaway_percent",
            "Delivery": "delivery_percent",
            "Dine-in":  "dine_in_percent",
        }
        masks = [fdf[channel_map[c]] > 0 for c in filters["channels"] if c in channel_map]
        if masks:
            combined = masks[0]
            for m in masks[1:]:
                combined = combined | m
            fdf = fdf[combined]
    if filters.get("day_types"):
        fdf = fdf[fdf["day_type"].isin(filters["day_types"])]

    return fdf


# ── Aggregation helpers ───────────────────────────────────────────────────────

def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly total revenue aggregated across all filtered branches."""
    g = (
        df.groupby(["year", "month", "month_name"], as_index=False)
        .agg(total_revenue=("total_revenue", "sum"),
             total_transactions=("total_transactions", "sum"),
             total_cups=("total_cups_sold", "sum"),
             avg_ticket=("avg_ticket_size", "mean"),
             profit=("profit", "sum"))
    )
    g["month_label"] = g["month"].map(MONTH_MAP)
    g = g.sort_values(["year", "month"])
    return g


def yoy_growth(df: pd.DataFrame) -> dict:
    """Calculate Year-over-Year revenue growth."""
    yearly = df.groupby("year")["total_revenue"].sum()
    result = {}
    for yr in sorted(yearly.index):
        if yr - 1 in yearly.index:
            prev = yearly[yr - 1]
            curr = yearly[yr]
            result[yr] = (curr - prev) / prev * 100
    return result


def promo_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Average revenue by promo status and promo type."""
    return (
        df.groupby(["promo_label", "promo_type"], as_index=False)
        .agg(avg_revenue=("total_revenue", "mean"),
             avg_profit=("profit", "mean"),
             count=("total_revenue", "count"))
    )


def city_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Per-city aggregated performance metrics."""
    g = (
        df.groupby("branch_city", as_index=False)
        .agg(
            total_revenue=("total_revenue", "sum"),
            total_profit=("profit", "sum"),
            total_transactions=("total_transactions", "sum"),
            avg_profit_margin=("profit_margin", "mean"),
            avg_ticket=("avg_ticket_size", "mean"),
            num_branches=("branch_id", "nunique"),
            avg_satisfaction=("customer_satisfaction", "mean"),
        )
    )
    g["revenue_per_branch"] = g["total_revenue"] / g["num_branches"]
    g["profit_per_branch"]  = g["total_profit"]  / g["num_branches"]
    return g


def branch_type_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Per-branch-type aggregated metrics."""
    return (
        df.groupby("branch_type", as_index=False)
        .agg(
            total_revenue=("total_revenue", "sum"),
            total_profit=("profit", "sum"),
            avg_profit_margin=("profit_margin", "mean"),
            avg_satisfaction=("customer_satisfaction", "mean"),
            num_branches=("branch_id", "nunique"),
            total_transactions=("total_transactions", "sum"),
        )
    )


def weekday_weekend(df: pd.DataFrame) -> pd.DataFrame:
    """Weekday vs Weekend performance comparison."""
    return (
        df.groupby("day_type", as_index=False)
        .agg(
            avg_revenue=("total_revenue", "mean"),
            avg_transactions=("total_transactions", "mean"),
            avg_profit=("profit", "mean"),
            avg_margin=("profit_margin", "mean"),
        )
    )


def channel_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Overall and per-branch-type channel distribution."""
    overall = pd.DataFrame({
        "channel": ["Takeaway", "Delivery", "Dine-in"],
        "pct": [
            df["takeaway_percent"].mean(),
            df["delivery_percent"].mean(),
            df["dine_in_percent"].mean(),
        ]
    })
    return overall


def channel_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """Channel distribution per branch type."""
    g = (
        df.groupby("branch_type", as_index=False)
        .agg(
            takeaway=("takeaway_percent", "mean"),
            delivery=("delivery_percent", "mean"),
            dine_in=("dine_in_percent", "mean"),
        )
    )
    return g


def channel_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Annual channel trend."""
    g = (
        df.groupby("year", as_index=False)
        .agg(
            takeaway=("takeaway_percent", "mean"),
            delivery=("delivery_percent", "mean"),
            dine_in=("dine_in_percent", "mean"),
        )
    )
    return g


def satisfaction_by_factor(df: pd.DataFrame, factor: str) -> pd.DataFrame:
    """Average satisfaction grouped by a given categorical factor."""
    return (
        df.groupby(factor, as_index=False)
        .agg(avg_satisfaction=("customer_satisfaction", "mean"),
             count=("customer_satisfaction", "count"))
        .sort_values("avg_satisfaction", ascending=False)
    )


def expansion_score(df: pd.DataFrame) -> pd.DataFrame:
    """Compute expansion potential score per city (matching notebook logic)."""
    city = city_performance(df)

    # normalise profit margin (0-1)
    min_m = city["avg_profit_margin"].min()
    max_m = city["avg_profit_margin"].max()
    if max_m != min_m:
        city["norm_margin"] = (city["avg_profit_margin"] - min_m) / (max_m - min_m)
    else:
        city["norm_margin"] = 0.5

    # saturation: inverse of branch count normalised
    min_b = city["num_branches"].min()
    max_b = city["num_branches"].max()
    if max_b != min_b:
        city["norm_saturation"] = 1 - (city["num_branches"] - min_b) / (max_b - min_b)
    else:
        city["norm_saturation"] = 0.5

    # composite score (equal weight)
    city["expansion_score"] = (city["norm_margin"] + city["norm_saturation"]) / 2

    city = city.sort_values("expansion_score", ascending=False)
    return city


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return correlation matrix for key numeric columns."""
    cols = ["total_transactions", "total_revenue", "avg_ticket_size",
            "total_cups_sold", "profit"]
    return df[cols].corr()


def build_summary_stats(df: pd.DataFrame) -> dict:
    """Build a flat dict of headline KPIs for AI context."""
    return {
        "total_revenue":        df["total_revenue"].sum(),
        "total_profit":         df["profit"].sum(),
        "avg_profit_margin":    df["profit_margin"].mean(),
        "total_transactions":   df["total_transactions"].sum(),
        "avg_ticket_size":      df["avg_ticket_size"].mean(),
        "avg_satisfaction":     df["customer_satisfaction"].mean(),
        "num_branches":         df["branch_id"].nunique(),
        "num_cities":           df["branch_city"].nunique(),
        "rows":                 len(df),
    }
