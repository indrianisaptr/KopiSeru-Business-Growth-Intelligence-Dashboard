"""
components/cards.py
Reusable card/UI renderers for KopiSeru Dashboard.
Visual styling lives in assets/main.css (loaded once in main.py) —
this file only builds the HTML structure and feeds it CSS classes.

Replaces the old components/metrics.py. Function signatures are kept
identical to metrics.py so no page needs to change its calls.
"""

import streamlit as st
from utils.icons import svg


import base64
from pathlib import Path

_LOGO_CACHE = None
_BRAND_LOGO_CACHE = None

def _get_logo_b64() -> str:
    """Baca logo sekali, cache di memori supaya tidak baca file berulang."""
    global _LOGO_CACHE
    if _LOGO_CACHE is None:
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "Icon_topi.png"
        data = logo_path.read_bytes()
        _LOGO_CACHE = f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return _LOGO_CACHE


def _get_brand_logo_b64() -> str:
    """Baca logo KopiSeru (assets/LogoKopiSeru.png) sekali, cache di memori.

    Dipakai untuk menggantikan teks kuning "KOPISERU" di section_header()
    dengan logo resmi, tanpa mengubah logo bulat (Icon_topi.png) yang
    sudah tampil di sisi kiri header.
    """
    global _BRAND_LOGO_CACHE
    if _BRAND_LOGO_CACHE is None:
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "LogoKopiSeru.png"
        data = logo_path.read_bytes()
        _BRAND_LOGO_CACHE = f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return _BRAND_LOGO_CACHE


def _render_html(html: str) -> None:
    """
    Render raw HTML safely via st.markdown.

    Markdown treats lines indented by 4+ spaces as an indented code
    block, which causes raw HTML tags to print as plain text instead
    of being rendered. Stripping per-line leading whitespace avoids
    that without changing the HTML/CSS itself.
    """
    flat = "".join(line.strip() for line in html.splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def fmt_currency(val: float, short: bool = True, decimals: int = 1) -> str:
    """Format a Rupiah value.

    Single source of truth for currency formatting across the dashboard.

    Args:
        val: the raw Rupiah value.
        short: if True, abbreviate using K/M/B units.
        decimals: number of decimal places used for the abbreviated
            K/M/B forms (e.g. decimals=1 for KPI cards, decimals=2 for
            chart labels that need finer precision).
    """
    if val is None:
        return "—"
    if short:
        if abs(val) >= 1_000_000_000:
            return f"Rp {val/1_000_000_000:.{decimals}f} B"
        if abs(val) >= 1_000_000:
            return f"Rp {val/1_000_000:.{decimals}f} M"
        if abs(val) >= 1_000:
            return f"Rp {val/1_000:.{decimals}f} K"
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
    caption: str = "vs last year",
) -> None:
    """Render a styled KPI metric card. Uses .kpi-card from main.css."""
    cls = "positive" if delta_positive else "negative"
    arrow = "▲" if delta_positive else "▼"
    delta_html = (
        f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'
        if delta
        else '<div class="kpi-delta" aria-hidden="true" style="visibility:hidden;">0</div>'
    )
    caption_html = (
        f'<div class="kpi-caption">{caption}</div>' if (delta and caption) else ""
    )
    caption_html = (
    f'<div class="kpi-caption">{caption}</div>'
    if (delta and caption)
    else '<div class="kpi-caption" aria-hidden="true" style="visibility:hidden;">.</div>'
    )
    help_html = (
        f'<div style="font-size:11px; color:var(--text-muted); margin-top:4px;">{help_text}</div>'
        if help_text
        else ""
    )
    _render_html(
        f"""
        <div class="kpi-card">
            <span class="kpi-icon-watermark">{icon}</span>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            {caption_html}
            {help_html}
        </div>
        """
    )


def section_header(title: str, subtitle: str = "") -> None:
    """Render hero header box: logo | logo KopiSeru | nama halaman | deskripsi."""
    logo_b64 = _get_logo_b64()
    brand_logo_b64 = _get_brand_logo_b64()
    sub_html = (
        f'<div style="font-size:15px; color:#E8D5BC; margin-top:4px;">{subtitle}</div>'
        if subtitle else ""
    )
    _render_html(
        f"""
        <div style="
            background: linear-gradient(135deg, #402218 0%, #6D4329 55%, #986938 100%);
            border-radius: 14px;
            padding: 18px 24px;
            margin: 0 0 20px 0;
            display: flex;
            align-items: center;
            gap: 18px;
            box-shadow:
                0 6px 16px rgba(64, 34, 24, 0.35),
                inset 0 1px 2px rgba(255, 255, 255, 0.12),
                inset 0 -2px 4px rgba(0, 0, 0, 0.25);
        ">
            <img src="{logo_b64}" style="height:56px; width:56px; object-fit:contain; flex-shrink:0;">
            <div>
                <div style="display:flex; align-items:center; margin-bottom:2px;">
                    <img src="{brand_logo_b64}" alt="KopiSeru"
                         style="height:19px; width:auto; object-fit:contain; display:block;">
                </div>
                <div style="font-size:24px; font-weight:800; color:#F1EEEA; line-height:1.15;">
                    {title}
                </div>
                {sub_html}
            </div>
        </div>
        """
    )


def info_box(text: str, kind: str = "info") -> None:
    """
    Render a styled info / insight box.
    kind: info | success | warning | danger
    Maps to .info-box / .success-box / .warning-box / .danger-box in main.css.
    """
    box_class = {
        "info": "info-box",
        "success": "success-box",
        "warning": "warning-box",
        "danger": "danger-box",
    }.get(kind, "info-box")
    _render_html(f'<div class="{box_class}">{text}</div>')


def ai_insight_card(insight_text: str) -> None:
    """Render the AI insight card. Uses .ai-insight-card from main.css."""
    insight_icon = svg("INSIGHT")
    _render_html(
        f"""
        <div class="ai-insight-card">
            <div class="ai-badge">{insight_icon} AI BUSINESS INSIGHT</div>
            <p>{insight_text}</p>
        </div>
        """
    )

def inject_compact_css() -> None:
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            height: 2.2rem !important;
            min-height: 2.2rem !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        header[data-testid="stHeader"] [data-testid="stDecoration"],
        [data-testid="stDecoration"] {
            display: none !important;
        }

        section.main .block-container,
        [data-testid="stMain"] .block-container {
            padding-top: 0.4rem !important;
            padding-bottom: 0.8rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            max-width: 100% !important;
        }

        section.main div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"] {
            gap: 0.55rem !important;
            align-items: stretch !important;
        }
        section.main div[data-testid="stColumn"],
        [data-testid="stMain"] div[data-testid="stColumn"] {
            display: flex !important;
            flex-direction: column !important;
        }
        /* Buat wrapper otomatis Streamlit "transparan" & teruskan tinggi 100%
           ke SEMUA level wrapper di antara kolom dan card, memakai descendant
           selector (bukan direct child) supaya tetap match berapapun lapis
           wrapper yang disisipkan Streamlit versi ini. */
        section.main div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(> div[class*="st-key-chartbox_"]),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(> div[class*="st-key-chartbox_"]),
        section.main div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(> div[class*="st-key-sidepanel_"]),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(> div[class*="st-key-sidepanel_"]),
        section.main div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(> div[class*="st-key-kpicol_"]),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(> div[class*="st-key-kpicol_"]),
        section.main div[data-testid="stColumn"] div[data-testid="element-container"]:has(> div[class*="st-key-chartbox_"]),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="element-container"]:has(> div[class*="st-key-chartbox_"]),
        section.main div[data-testid="stColumn"] div[data-testid="element-container"]:has(> div[class*="st-key-sidepanel_"]),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="element-container"]:has(> div[class*="st-key-sidepanel_"]),
        section.main div[data-testid="stColumn"] div[data-testid="element-container"]:has(> div[class*="st-key-kpicol_"]),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="element-container"]:has(> div[class*="st-key-kpicol_"]) {
            display: contents !important;
        }
        section.main div[data-testid="stColumn"] div[data-testid="stVerticalBlock"],
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stVerticalBlock"],
        section.main div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"],
        section.main div[data-testid="stColumn"] div[data-testid="stElementContainer"],
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stElementContainer"],
        section.main div[data-testid="stColumn"] div[data-testid="element-container"],
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="element-container"] {
            flex: 1 1 auto !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }
        /* ── FIX: jangan paksa height:100% pada pembungkus chart Plotly ──────
        Rule generic di atas membuat wrapper Plotly ikut stretch ke height:100%
        dari parent yang tinggi-nya tidak pasti di rantai flex, sehingga chart
        (yang sudah punya tinggi tetap dari fig.update_layout) ter-crop/squish
        jadi kotak kecil. Wrapper yang berisi .js-plotly-plot dikecualikan agar
        memakai tinggi natural sesuai kode chart, bukan dipaksa oleh flex. */
        section.main div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(.js-plotly-plot),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="stElementContainer"]:has(.js-plotly-plot),
        section.main div[data-testid="stColumn"] div[data-testid="element-container"]:has(.js-plotly-plot),
        [data-testid="stMain"] div[data-testid="stColumn"] div[data-testid="element-container"]:has(.js-plotly-plot) {
            height: auto !important;
            flex: 0 0 auto !important;
        }
        section.main div[data-testid="stColumn"] .js-plotly-plot,
        [data-testid="stMain"] div[data-testid="stColumn"] .js-plotly-plot,
        section.main div[data-testid="stColumn"] .plot-container.plotly,
        [data-testid="stMain"] div[data-testid="stColumn"] .plot-container.plotly {
            width: 100% !important;
        }

        section.main div[data-testid="stVerticalBlock"],
        [data-testid="stMain"] div[data-testid="stVerticalBlock"] {
            gap: 0.3rem !important;
        }
        section.main div[data-testid="stElementContainer"],
        [data-testid="stMain"] div[data-testid="stElementContainer"] {
            margin-bottom: 0.15rem !important;
        }

        /* ── KPI card ─────────────────────────────────────────────────────── */
        section.main .kpi-card,
        [data-testid="stMain"] .kpi-card {
            padding: 16px 16px 14px 16px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
        }
        section.main .kpi-label, [data-testid="stMain"] .kpi-label { font-size: 15px !important; margin-bottom: 4px !important; }
        section.main .kpi-value, [data-testid="stMain"] .kpi-value { font-size: 25px !important; line-height: 1.1 !important; }
        section.main .kpi-delta, [data-testid="stMain"] .kpi-delta { font-size: 15px !important; margin-top: 4px !important; }
        section.main .kpi-caption, [data-testid="stMain"] .kpi-caption { font-size: 10px !important; }

        /* Judul "KPI" — diperbesar, jarak ke card pertama dirapatkan */
        section.main div[class*="st-key-kpicol_"] h5,
        [data-testid="stMain"] div[class*="st-key-kpicol_"] h5 {
            font-size: 15px !important;
            font-weight: 700 !important;
            color: var(--primary, #5C3D1E) !important;
            text-transform: none !important;
            letter-spacing: normal !important;
            margin: 0 0 4px 0 !important;
        }

        /* Jarak antar KPI card */
        section.main div[class*="st-key-kpicol_"],
        [data-testid="stMain"] div[class*="st-key-kpicol_"] {
            gap: 0.7rem !important;
        }
        section.main div[class*="st-key-kpicol_"] div[data-testid="stElementContainer"],
        [data-testid="stMain"] div[class*="st-key-kpicol_"] div[data-testid="stElementContainer"] {
            margin-bottom: 0.7rem !important;
        }

        /* ── Heading chart ────────────────────────────────────────────────── */
        section.main .section-title, [data-testid="stMain"] .section-title { font-size: 18px !important; }
        section.main h3, [data-testid="stMain"] h3 { font-size: 13px !important; margin: 4px 0 3px 0 !important; }
        section.main h4, [data-testid="stMain"] h4 { font-size: 15.5px !important; margin: 0 0 4px 0 !important; font-weight:700 !important; }
        section.main h5, [data-testid="stMain"] h5 {
            font-size: 11px !important; margin: 2px 0 4px 0 !important;
            text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted);
        }
        section.main h5, [data-testid="stMain"] h5 {
            font-size: 11px !important; margin: 2px 0 4px 0 !important;
            text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted);
        }

        /* Override khusus: h4 di dalam card chart, margin 0 murni agar sejajar dgn Key Insights */
        section.main div[class*="st-key-chartbox_"] h4,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] h4 {
            font-size: 18px !important;
            font-weight: 700 !important;
            line-height: 1.1 !important;
            margin: 0 !important;
        }
        /* Hilangkan spacing ekstra dari baris kolom judul + tombol Explain */
        section.main div[class*="st-key-chartbox_"] div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="stHorizontalBlock"] {
            margin: 0 !important;
            align-items: flex-start !important;
        }
        section.main div[class*="st-key-chartbox_"] div[data-testid="stColumn"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="stColumn"] {
            align-items: flex-start !important;
        }
        section.main div[class*="st-key-chartbox_"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* ── Tombol Explain This Chart / Explain Chart (header chart) ─────── */
        section.main div[class*="st-key-chartbox_"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] {
            background: var(--surface, #F1EEEA) !important;
            border: 1px solid rgba(140, 100, 60, 0.18) !important;
            border-radius: 10px !important;
            padding: 14px 16px 12px 16px !important;
            box-sizing: border-box !important;
            height: 100% !important;
            flex: 1 1 auto !important;
            min-height: 0 !important;
            box-shadow:
                0 4px 10px rgba(90, 60, 30, 0.14),
                inset 0 1px 2px rgba(255, 255, 255, 0.6),
                inset 0 -2px 4px rgba(0, 0, 0, 0.05) !important;
        }

        /* ── TAMBAHAN BARU: hilangkan spacing ekstra pada baris judul+tombol ── */
        section.main div[class*="st-key-chartbox_"] div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="stHorizontalBlock"] {
            margin: 0 !important;
            align-items: flex-start !important;
        }
        section.main div[class*="st-key-chartbox_"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        section.main div[class*="st-key-chartbox_"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] {
            background: linear-gradient(180deg, #FBF6F0 0%, #F7EFE6 100%) !important;
            border: 1px solid rgba(140, 100, 60, 0.18) !important;
            border-radius: 10px !important;
            padding: 14px 16px 12px 16px !important;
            box-sizing: border-box !important;
            height: 100% !important;
            flex: 1 1 auto !important;
            min-height: 0 !important;
            box-shadow:
                0 4px 10px rgba(90, 60, 30, 0.14),
                inset 0 1px 2px rgba(255, 255, 255, 0.6),
                inset 0 -2px 4px rgba(0, 0, 0, 0.05) !important;
        }

        /* Rapatkan jarak judul chart ke info-box/success-box/warning-box di bawahnya
           — style global .info-box punya padding/margin sendiri yg terlalu lebar
           untuk konteks kartu chart yang lebih kecil ini. */
        section.main div[class*="st-key-chartbox_"] .info-box,
        section.main div[class*="st-key-chartbox_"] .success-box,
        section.main div[class*="st-key-chartbox_"] .warning-box,
        section.main div[class*="st-key-chartbox_"] .danger-box,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] .info-box,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] .success-box,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] .warning-box,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] .danger-box {
            margin-top: 2px !important;
            margin-bottom: 6px !important;
            padding: 8px 12px !important;
            line-height: 1.35 !important;
        }
        section.main div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.info-box),
        section.main div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.success-box),
        section.main div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.warning-box),
        section.main div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.danger-box),
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.info-box),
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.success-box),
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.warning-box),
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(.danger-box) {
            margin-top: 0 !important;
            margin-bottom: 4px !important;
            flex: 0 0 auto !important;
            height: auto !important;
        }
        /* Container judul (h4) juga jangan ikut stretch flex:1 — sama seperti
           info-box di atas. Inilah akar whitespace: sebelumnya h4 & info-box
           container ikut aturan generic flex:1 1 auto milik stColumn, sehingga
           keduanya menyerap sisa ruang kosong padahal isinya pendek. Container
           chart (.js-plotly-plot) TETAP flex:0 0 auto (aturan global sudah ada
           di atas) — jangan diutak-atik lagi, itu fix squish sebelumnya. */
        section.main div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(h4),
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="element-container"]:has(h4) {
            flex: 0 0 auto !important;
            height: auto !important;
        }
        section.main div[class*="st-key-chartbox_"] div[data-testid="stColumn"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] div[data-testid="stColumn"] {
            align-items: flex-start !important;
        }
        section.main div[class*="st-key-chartbox_"] > div[data-testid="stVerticalBlock"],
        [data-testid="stMain"] div[class*="st-key-chartbox_"] > div[data-testid="stVerticalBlock"] {
            justify-content: flex-start !important;
            gap: 4px !important;
        }

        section.main div[class*="st-key-chartbox_"] [data-testid="stPopover"] button,
        [data-testid="stMain"] div[class*="st-key-chartbox_"] [data-testid="stPopover"] button {
            padding: 2px 6px !important;
            font-size: 10px !important;
            height: 26px !important;
            min-height: 26px !important;
            width: 100% !important;
            max-width: 100% !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-sizing: border-box !important;
        }
        section.main .stButton button,
        [data-testid="stMain"] .stButton button {
            padding: 2px 8px !important;
            font-size: 11px !important;
            height: 24px !important;
            min-height: 24px !important;
        }

        /* ── Panel KPI ────────────────────────────────────────────────────── */
        section.main div[class*="st-key-kpicol_"],
        [data-testid="stMain"] div[class*="st-key-kpicol_"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            box-shadow: none !important;
        }

        /* ── Panel Insight + Copilot — 1 box, tinggi presisi = chart sebelah ── */
        section.main div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]),
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) {
            align-items: stretch !important;
        }
        section.main div[class*="st-key-sidepanel_"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] {
            background: linear-gradient(180deg, #FBF6F0 0%, #F7EFE6 100%) !important;
            border: 1px solid rgba(140, 100, 60, 0.18) !important;
            border-radius: 10px !important;
            padding: 14px 20px 12px 20px !important;
            box-sizing: border-box !important;
            height: 100% !important;
            flex: 1 1 auto !important;
            min-height: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            box-shadow:
                0 4px 10px rgba(90, 60, 30, 0.14),
                inset 0 1px 2px rgba(255, 255, 255, 0.6),
                inset 0 -2px 4px rgba(0, 0, 0, 0.05) !important;
        }

        /* Jaga agar kolom Key Insights & kolom chart di row yang sama benar-benar
        stretch penuh, top & bottom sejajar */
        section.main div[data-testid="stColumn"]:has(div[class*="st-key-sidepanel_"]),
        [data-testid="stMain"] div[data-testid="stColumn"]:has(div[class*="st-key-sidepanel_"]),
        section.main div[data-testid="stColumn"]:has(div[class*="st-key-chartbox_branch_margin"]),
        [data-testid="stMain"] div[data-testid="stColumn"]:has(div[class*="st-key-chartbox_branch_margin"]) {
            align-self: stretch !important;
        }
        section.main div[class*="st-key-sidepanel_"] > div[data-testid="stVerticalBlock"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] > div[data-testid="stVerticalBlock"] {
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }
        section.main div[class*="st-key-sidepanel_"] h4,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] h4 {
            font-size: 19px !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            margin: 0 0 16px 0 !important;
        }
        section.main div[class*="st-key-sidepanel_"] .info-box,
        section.main div[class*="st-key-sidepanel_"] .success-box,
        section.main div[class*="st-key-sidepanel_"] .warning-box,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .info-box,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .success-box,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .warning-box {
            font-size: 16.5px !important;
            line-height: 1.7 !important;
            padding: 18px 20px !important;
            margin: 0 0 14px 0 !important;
            min-height: 56px !important;
            box-sizing: border-box !important;
        }
        /* Dorong elemen popover Copilot ke bawah + beri jarak lebih besar dari insight terakhir */
        section.main div[class*="st-key-sidepanel_"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has([data-testid="stPopover"]),
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has([data-testid="stPopover"]),
        section.main div[class*="st-key-sidepanel_"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:has([data-testid="stPopover"]),
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:has([data-testid="stPopover"]) {
            margin-top: auto !important;
            padding-top: 26px !important;
        }
        section.main div[class*="st-key-sidepanel_"] [data-testid="stPopover"] button,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] [data-testid="stPopover"] button {
            width: 100% !important;
            height: 46px !important;
            min-height: 46px !important;
            font-size: 14.5px !important;
            font-weight: 600 !important;
            padding: 8px 14px !important;
        }
        /* ── Kunci tinggi row 3 (Margin by Branch Type & Key Insights) agar
        benar-benar presisi sejajar top & bottom, tanpa mempengaruhi row lain ── */
        section.main div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]),
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) {
            display: flex !important;
            align-items: stretch !important;
        }
        section.main div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) > div[data-testid="stColumn"],
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) > div[data-testid="stColumn"] {
            height: 100% !important;
            align-self: stretch !important;
            box-sizing: border-box !important;
        }
        section.main div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) div[data-testid="stVerticalBlock"],
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) div[data-testid="stVerticalBlock"],
        section.main div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) div[data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-sidepanel_"]) div[data-testid="stVerticalBlockBorderWrapper"] {
            height: 100% !important;
            min-height: 100% !important;
            box-sizing: border-box !important;
        }
        section.main div[class*="st-key-chartbox_branch_margin"],
        [data-testid="stMain"] div[class*="st-key-chartbox_branch_margin"],
        section.main div[class*="st-key-sidepanel_"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] {
            min-height: 100% !important;
            box-sizing: border-box !important;
        }

        /* (Rule lama "kunci tinggi 350px + overflow:hidden" untuk
           chartbox_promo_avg_revenue / chartbox_promo_vs_nonpromo sudah
           dihapus — itu peninggalan layout lama sebelum KPI dipindah ke atas,
           dan menyebabkan chart ter-clip karena tingginya sudah dinaikkan
           melebihi 350px. Card sekarang mengikuti tinggi konten secara alami.) */
        /* ── Row 3 Business Growth: kunci tinggi Profitability by City == Copilot ── */
        section.main div[class*="st-key-chartbox_city_profitability"],
        [data-testid="stMain"] div[class*="st-key-chartbox_city_profitability"],
        section.main div[class*="st-key-sidepanel_biz_copilot"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_biz_copilot"] {
            min-height: 100% !important;
            height: 100% !important;
            box-sizing: border-box !important;
        }

        /* ── Tabs Copilot: equal width, center ────────────────────────────── */
        section.main div[class*="st-key-sidepanel_"] div[data-baseweb="tab-list"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
            justify-content: center !important;
            gap: 4px !important;
        }
        section.main div[class*="st-key-sidepanel_"] div[data-baseweb="tab-list"] button,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[data-baseweb="tab-list"] button {
            flex: 1 1 0 !important;
            justify-content: center !important;
            text-align: center !important;
        }

        /* ── Tombol Generate Insight / Recommendations / Ask AI: full width, proporsional ── */
        section.main div[class*="st-key-sidepanel_"] div[class*="st-key-ai_insight_"] button,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[class*="st-key-ai_insight_"] button,
        section.main div[class*="st-key-sidepanel_"] div[class*="st-key-recommendations_"] button,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[class*="st-key-recommendations_"] button,
        section.main div[class*="st-key-sidepanel_"] div[class*="st-key-ask_btn_"] button,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[class*="st-key-ask_btn_"] button {
            width: 100% !important;
            height: 44px !important;
            min-height: 44px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            padding: 8px 14px !important;
        }

        /* ── Suggested Questions: chip mengikuti isi, bukan full width ──────── */
        section.main div[class*="st-key-sidepanel_"] div[class*="st-key-suggested_"] button,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[class*="st-key-suggested_"] button {
            width: auto !important;
            max-width: 100% !important;
            height: auto !important;
            min-height: 30px !important;
            padding: 6px 12px !important;
            font-size: 12.5px !important;
            line-height: 1.3 !important;
            white-space: normal !important;
            border-radius: 16px !important;
        }

        /* ── Ask Your Own Question: kontras textarea ─────────────────────── */
        section.main div[class*="st-key-sidepanel_"] .stTextArea textarea,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .stTextArea textarea {
            background: #FFFFFF !important;
            color: var(--text, #3A2A1A) !important;
            border: 1px solid rgba(140, 100, 60, 0.35) !important;
        }
        section.main div[class*="st-key-sidepanel_"] .stTextArea textarea::placeholder,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .stTextArea textarea::placeholder {
            color: rgba(90, 70, 50, 0.55) !important;
        }
        /* ── Rapatkan spacing internal Copilot (berlaku di semua page) ─────── */
        section.main div[class*="st-key-sidepanel_"] hr,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] hr {
            margin: 8px 0 !important;
        }
        section.main div[class*="st-key-sidepanel_"] .stTabs,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .stTabs {
            margin-top: 4px !important;
        }
        section.main div[class*="st-key-sidepanel_"] [data-baseweb="tab-panel"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] [data-baseweb="tab-panel"] {
            padding-top: 10px !important;
        }
        section.main div[class*="st-key-sidepanel_"] h3,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] h3 {
            margin: 4px 0 6px 0 !important;
        }
        section.main div[class*="st-key-sidepanel_"] div[class*="st-key-suggested_"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[class*="st-key-suggested_"] {
            margin-bottom: 4px !important;
        }
        section.main div[class*="st-key-sidepanel_"] div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] div[data-testid="stHorizontalBlock"] {
            gap: 0.4rem !important;
            margin-bottom: 2px !important;
        }
        section.main div[class*="st-key-sidepanel_"] .stTextArea,
        [data-testid="stMain"] div[class*="st-key-sidepanel_"] .stTextArea {
            margin: 2px 0 8px 0 !important;
        }
        /* ── Popover Business Development Copilot (Executive Summary, dst)
        Konten popover dirender React portal terpisah dari container
        "sidepanel_", jadi butuh selector sendiri yang menyasar body
        popover-nya, dibatasi hanya utk popover Copilot via :has(). ── */
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) {
            width: 460px !important;
            max-width: 92vw !important;
            padding: 18px 20px !important;
            box-sizing: border-box !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) .info-box,
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) .warning-box,
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) .success-box {
            font-size: 13px !important;
            line-height: 1.5 !important;
            padding: 14px 16px !important;
            margin: 0 0 12px 0 !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) hr {
            margin: 8px 0 !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) h3 {
            font-size: 13px !important;
            margin: 4px 0 6px 0 !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) [data-baseweb="tab-panel"] {
            padding-top: 10px !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[data-testid="stHorizontalBlock"] {
            gap: 0.4rem !important;
            margin-bottom: 2px !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
            justify-content: center !important;
            gap: 4px !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[data-baseweb="tab-list"] button {
            flex: 1 1 0 !important;
            justify-content: center !important;
            text-align: center !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[class*="st-key-ai_insight_"] button,
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[class*="st-key-recommendations_"] button,
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[class*="st-key-ask_btn_"] button {
            width: 100% !important;
            height: 42px !important;
            min-height: 42px !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            padding: 8px 14px !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[class*="st-key-suggested_"] button {
            width: auto !important;
            max-width: 100% !important;
            height: auto !important;
            min-height: 30px !important;
            padding: 6px 12px !important;
            font-size: 12px !important;
            line-height: 1.3 !important;
            white-space: normal !important;
            border-radius: 16px !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) div[class*="st-key-suggested_"] {
            margin-bottom: 4px !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) .stTextArea {
            margin: 2px 0 8px 0 !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) .stTextArea textarea {
            background: #FFFFFF !important;
            color: var(--text, #3A2A1A) !important;
            border: 1px solid rgba(140, 100, 60, 0.35) !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) .stTextArea textarea::placeholder {
            color: rgba(90, 70, 50, 0.55) !important;
        }
        div[data-testid="stPopoverBody"]:has(div[class*="st-key-ai_insight_"]) h4 {
            font-size: 17px !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            margin: 0 0 12px 0 !important;
            color: var(--primary, #5C3D1E) !important;
        }
        /* ── Hilangkan background wrapper KPI di Executive Summary,
        sisakan hanya masing-masing kpi-card. kpicol_biz (Business Growth)
        tidak terpengaruh karena selector ini spesifik ke "kpicol_main". ── */
        section.main div[class*="st-key-kpicol_main"],
        [data-testid="stMain"] div[class*="st-key-kpicol_main"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        /* ── Rapatkan isi panel KPI Executive Summary ke atas (bukan center),
        + perbesar judul "KPI". Tidak menyentuh kpicol_biz (Business Growth)
        karena selector spesifik ke "kpicol_main". ── */
        section.main div[class*="st-key-kpicol_main"],
        [data-testid="stMain"] div[class*="st-key-kpicol_main"] {
            justify-content: flex-start !important;
        }
        section.main div[class*="st-key-kpicol_main"] h5,
        [data-testid="stMain"] div[class*="st-key-kpicol_main"] h5 {
            font-size: 18px !important;
            margin: 0 0 2px 0 !important;
        }
        /* ── Perbesar KPI card di Business Growth (kpicol_biz) secukupnya
        agar pas mengisi panel fixed-height 350px, tanpa overflow.
        kpicol_main (Executive Summary) tidak terpengaruh. ── */
        section.main div[class*="st-key-kpicol_biz"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] {
            justify-content: flex-start !important;
        }
        section.main div[class*="st-key-kpicol_biz"] h5,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] h5 {
            font-size: 19px !important;
            margin: 0 0 2px 0 !important;
        }
        section.main div[class*="st-key-kpicol_biz"] .kpi-card,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] .kpi-card {
            min-height: 112px !important;
            padding: 13px 14px !important;
            justify-content: flex-start !important;
        }
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;
        }
        section.main div[class*="st-key-kpicol_biz"] .kpi-icon,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] .kpi-icon {
            font-size: 15px !important;
        }
        section.main div[class*="st-key-kpicol_biz"] .kpi-label,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] .kpi-label {
            font-size: 16px !important;
            margin-bottom: 4px !important;
        }
        section.main div[class*="st-key-kpicol_biz"] .kpi-value,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] .kpi-value {
            font-size: 21px !important;
            line-height: 1.15 !important;
        }
        section.main div[class*="st-key-kpicol_biz"] .kpi-delta,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] .kpi-delta {
            font-size: 10px !important;
            margin-top: 4px !important;
        }
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stElementContainer"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stElementContainer"] {
            margin-bottom: 0.45rem !important;
        }
        /* ── Reset paksaan height:100% dari rule generic (inject_compact_css)
        khusus di dalam kpicol_biz, supaya 2 baris kartu (Revenue/Profit &
        Margin/Transactions) tidak "direntangkan" dan malah menyisakan gap
        aneh di tengah. Card jadi packed rapat dari atas. ── */
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stVerticalBlock"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stVerticalBlock"],
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stElementContainer"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stElementContainer"],
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="element-container"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="element-container"],
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stHorizontalBlock"],
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stColumn"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stColumn"] {
            height: auto !important;
            flex: none !important;
        }
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stHorizontalBlock"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0.45rem !important;
        }
        /* ── Sembunyikan ikon anchor-link otomatis di judul "Key Metrics" ─── */
        section.main div[class*="st-key-kpicol_biz"] h5 a,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] h5 a {
            display: none !important;
        }
        /* ── Pastikan 2 kolom kartu KPI benar-benar full-width simetris ───── */
        section.main div[class*="st-key-kpicol_biz"] div[data-testid="stColumn"],
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] div[data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 0 !important;
        }
        section.main div[class*="st-key-kpicol_biz"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:first-child,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:first-child,
        section.main div[class*="st-key-kpicol_biz"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child,
        [data-testid="stMain"] div[class*="st-key-kpicol_biz"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child {
            margin-bottom: 4px !important;
            padding-top: 0 !important;
        }
        /* ── KPI card: Executive Summary (6 kartu, lebih tinggi) ─────────────── */
        section.main div[class*="st-key-kpicol_main"] .kpi-card,
        [data-testid="stMain"] div[class*="st-key-kpicol_main"] .kpi-card {
            height: 225px !important;
            min-height: 225px !important;
        }

        /* ── KPI card: Business Growth, Branch Performance, Customer Insight (4 kartu) ── */
        section.main div[class*="st-key-kpicol_std"] .kpi-card,
        [data-testid="stMain"] div[class*="st-key-kpicol_std"] .kpi-card {
            height: 190px !important;
            min-height: 190px !important;
        }
        .kpi-card {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #6F4E37 0%, #4A2A1D 100%);
            border-radius: 16px;
            padding: 18px 18px 16px 18px;    
            z-index: 0;
            box-shadow: 0 4px 14px rgba(64, 34, 24, 0.18);
            transition: transform 200ms ease, box-shadow 200ms ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(64, 34, 24, 0.28);
        }
        .kpi-card > * {
            position: relative;   /* ← bikin semua child langsung punya stacking context sendiri */
            z-index: 1;           /* ← naikkan di atas watermark */
        }

        .kpi-icon-watermark {
            position: absolute;
            bottom: 6px;
            left: 50%;
            right: auto;
            top: auto;
            transform: translateX(-50%);
            font-size: 65px;
            color: #FFFFFF;
            opacity: 0.35;
            pointer-events: none;
            z-index: 0;
        }

        .kpi-label {
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #F1EEEA;
            margin-bottom: 4px;
            padding-right: 0px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .kpi-value {
            font-size: 20px;
            font-weight: 800;
            color: #FFEDAC;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
            line-height: 1.1;
        }

        .kpi-delta {
            font-size: 12px;
            font-weight: 700;
            margin-top: 8px;
        }
        .kpi-delta.positive { color: #2E7D32; }
        .kpi-delta.negative { color: #C62828; }

        .kpi-caption {
            font-size: 11px;
            color: #F1EEEA;
            margin-top: 1px;
        }
        """,
        unsafe_allow_html=True,
    )