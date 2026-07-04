"""
components/metrics.py
Reusable KPI metric card renderer for KopiSeru Dashboard.
"""

import streamlit as st
from utils.data_loader import COLORS


def _render_html(html: str) -> None:
    """
    Render raw HTML safely via st.markdown.

    Streamlit/Markdown treats any line indented by 4+ spaces as an
    indented code block, which causes raw HTML tags to be printed as
    plain text instead of being rendered (this is the root cause of
    KPI cards showing raw <div style="..."> tags, especially when the
    card is rendered inside st.columns()). Stripping per-line leading
    whitespace before passing the string to st.markdown avoids that
    markdown code-block detection while keeping the HTML/CSS identical.
    """
    flat = "".join(line.strip() for line in html.splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def fmt_currency(val: float, short: bool = True) -> str:
    """Format a Rupiah value."""
    if val is None:
        return "—"
    if short:
        if abs(val) >= 1_000_000_000:
            return f"Rp {val/1_000_000_000:.1f} M"
        if abs(val) >= 1_000_000:
            return f"Rp {val/1_000_000:.1f} JT"
        if abs(val) >= 1_000:
            return f"Rp {val/1_000:.0f} RB"
    return f"Rp {val:,.0f}"


def fmt_number(val: float, suffix: str = "") -> str:
    if val is None:
        return "—"
    if abs(val) >= 1_000_000:
        return f"{val/1_000_000:.1f}M{suffix}"
    if abs(val) >= 1_000:
        return f"{val/1_000:.1f}K{suffix}"
    return f"{val:,.0f}{suffix}"


def metric_card(
    label: str,
    value: str,
    delta: str = "",
    delta_positive: bool = True,
    icon: str = "",
    help_text: str = "",
) -> None:
    """Render a styled KPI metric card."""
    delta_color = COLORS["success"] if delta_positive else COLORS["danger"]
    delta_html = (
        f'<span style="color:{delta_color}; font-size:13px; font-weight:600;">'
        f"{delta}</span>"
        if delta
        else ""
    )
    help_html = (
        f'<div style="font-size:11px; color:{COLORS["text_muted"]}; margin-top:4px;">'
        f"{help_text}</div>"
        if help_text
        else ""
    )
    _render_html(
        f"""
        <div style="
            background: {COLORS['surface']};
            border: 1px solid {COLORS['accent2']}55;
            border-left: 4px solid {COLORS['accent']};
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        ">
            <div style="font-size:12px; color:{COLORS['text_muted']};
                        font-weight:600; text-transform:uppercase;
                        letter-spacing:0.5px; margin-bottom:6px;">
                {icon} {label}
            </div>
            <div style="font-size:26px; font-weight:800;
                        color:{COLORS['primary']}; line-height:1.1;">
                {value}
            </div>
            {delta_html}
            {help_html}
        </div>
        """
    )


def section_header(title: str, subtitle: str = "") -> None:
    """Render a styled section header."""
    sub_html = (
        f'<p style="color:{COLORS["text_muted"]}; font-size:14px; margin:4px 0 0 0;">'
        f"{subtitle}</p>"
        if subtitle
        else ""
    )
    _render_html(
        f"""
        <div style="margin: 24px 0 16px 0;">
            <h2 style="color:{COLORS['primary']}; font-weight:800;
                       margin:0; font-size:22px;">
                {title}
            </h2>
            {sub_html}
            <hr style="border:2px solid {COLORS['accent']}; margin:10px 0 0 0;
                       width:60px;">
        </div>
        """
    )


def info_box(text: str, kind: str = "info") -> None:
    """Render a styled info / insight box."""
    palette = {
        "info":    (COLORS["accent2"], COLORS["primary"]),
        "success": ("#d4edda", "#155724"),
        "warning": ("#fff3cd", "#856404"),
        "danger":  ("#f8d7da", "#721c24"),
    }
    bg, fg = palette.get(kind, palette["info"])
    _render_html(
        f"""
        <div style="background:{bg}; color:{fg}; border-radius:8px;
                    padding:12px 16px; margin:8px 0; font-size:14px;
                    line-height:1.6;">
            {text}
        </div>
        """
    )


def ai_insight_card(insight_text: str) -> None:
    """Render the AI insight card."""
    _render_html(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']}EE, {COLORS['secondary']}EE);
            color: #fff;
            border-radius: 12px;
            padding: 18px 20px;
            margin: 16px 0;
            box-shadow: 0 4px 16px rgba(92,61,30,0.18);
        ">
            <div style="font-size:13px; font-weight:700; letter-spacing:0.5px;
                        margin-bottom:8px; opacity:0.85;">
                AI BUSINESS INSIGHT
            </div>
            <div style="font-size:14px; line-height:1.7;">
                {insight_text}
            </div>
        </div>
        """
    )