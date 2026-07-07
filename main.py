"""
app.py  —  KopiSeru Business Intelligence Dashboard
Entry point. Renders brand header at the TOP of the sidebar,
followed by the page navigation links, then runs the selected page.
"""

import base64
import streamlit as st
from pathlib import Path
from utils.icons import svg

@st.cache_data
def _img_b64(path: str) -> str:
    """Read a local image and return it as a base64 data URI for inline HTML."""
    img_path = Path(__file__).parent / path
    data = img_path.read_bytes()
    ext = img_path.suffix.lstrip(".")
    return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"

def _load_css(path: str) -> None:
    """Load and inject the shared stylesheet (assets/main.css)."""
    css_path = Path(__file__).parent / path
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="KopiSeru BI Dashboard",
    page_icon=_img_b64("assets/Icon_topi.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

_load_css("assets/main.css")

# Daftarkan 4 halaman, tapi sembunyikan nav otomatis bawaan Streamlit
# (position="hidden") supaya kita bisa atur urutan tampilan sidebar sendiri.
pages = [
    st.Page("pages/1_Executive_Summary.py", title="Executive Summary", icon=":material/bar_chart:", default=True),
    st.Page("pages/2_Business_Growth_&_Profitability.py", title="Business Growth & Profitability", icon=":material/trending_up:"),
    st.Page("pages/3_Branch_Performance_&_Expansion.py", title="Branch Performance & Expansion", icon=":material/store:"),
    st.Page("pages/4_Customer_Insight.py", title="Customer Insight", icon=":material/sentiment_satisfied:"),
]

nav = st.navigation(pages, position="hidden")
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #402218 0%, #6d4329 100%) !important;
        min-height: 100vh !important;
    }
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarNav"] {
        background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    _logo_b64 = _img_b64("assets/Icon_topi.png")
    _wordmark_b64 = _img_b64("assets/LogoKopiSeru.png")
    st.markdown(
        f"""
        <div style="text-align:center; padding: 0px 0 10px 0;">
            <div style="font-size:28px; font-weight:900;
                        color:#D4A853; letter-spacing:1px;">
                <img src="{_logo_b64}" style="height:80px; width:auto;
                     vertical-align:middle; margin-right:6px;">
            </div>
            <div style="margin-top:8px;">
                <img src="{_wordmark_b64}" style="height:28px; width:auto;">
            </div>
            <div style="font-size:15px; color:#C8A882;
                        margin-top:2px;">
                Business Intelligence Dashboard
            </div>
        </div>
        <hr style="border:1px solid rgba(245,230,211,0.2); margin:0 0 12px 0;">
        """,
        unsafe_allow_html=True,
    )

    # Deteksi halaman aktif secara Python DULU, sebelum render apapun
    _active_idx = None
    for _i, _p in enumerate(pages, start=1):
        if _p.url_path == nav.url_path:
            _active_idx = _i
            break

    # Inject CSS SEBELUM elemen nav dirender, supaya tidak ada jeda/flash
    if _active_idx:
        st.markdown(
            f"""
            <style>
            section[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
                transition: none !important;
                animation: none !important;
            }}
            div[class*="st-key-navlink_{_active_idx}"] [data-testid="stPageLink"] a {{
                background: rgba(212, 168, 83, 0.12) !important;
                border: 1.5px solid #D4A853 !important;
                color: #D4A853 !important;
                font-weight: 800 !important;
            }}
            div[class*="st-key-navlink_{_active_idx}"] [data-testid="stPageLink"] a p {{
                color: #D4A853 !important;
            }}
            div[class*="st-key-navlink_{_active_idx}"] [data-testid="stPageLink"] svg {{
                color: #D4A853 !important;
                filter: none !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    # ── Navigasi halaman (di bawah logo), tiap link dibungkus key unik ──────
    for _i, page in enumerate(pages, start=1):
        with st.container(key=f"navlink_{_i}"):
            st.page_link(page, icon=page.icon)

    st.markdown("<hr style='border:1px solid rgba(245,230,211,0.2); margin:12px 0;'>", unsafe_allow_html=True)

nav.run()