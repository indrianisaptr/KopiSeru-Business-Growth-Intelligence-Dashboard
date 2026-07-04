"""
app.py  —  KopiSeru Business Intelligence Dashboard
Entry point. Renders brand header at the TOP of the sidebar,
followed by the page navigation links, then runs the selected page.
"""

import streamlit as st

st.set_page_config(
    page_title="KopiSeru BI Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Daftarkan 4 halaman, tapi sembunyikan nav otomatis bawaan Streamlit
# (position="hidden") supaya kita bisa atur urutan tampilan sidebar sendiri.
pages = [
    st.Page("pages/1_Executive_Summary.py", title="Executive Summary", icon="📊", default=True),
    st.Page("pages/2_Business_Growth_&_Profitability.py", title="Business Growth & Profitability", icon="📈"),
    st.Page("pages/3_Branch_Performance_&_Expansion.py", title="Branch Performance & Expansion", icon="🏪"),
    st.Page("pages/4_Customer_Insight.py", title="Customer Insight", icon="😊"),
]

nav = st.navigation(pages, position="hidden")

with st.sidebar:
    # ── Brand header (paling atas) ────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center; padding: 8px 0 12px 0;">
            <div style="font-size:28px; font-weight:900;
                        color:#D4A853; letter-spacing:1px;">
                ☕ KopiSeru
            </div>
            <div style="font-size:11px; color:#8B5E3C;
                        margin-top:2px;">
                Business Intelligence Dashboard
            </div>
        </div>
        <hr style="border:1px solid #D4A85333; margin:0 0 12px 0;">
        """,
        unsafe_allow_html=True,
    )

    # ── Navigasi halaman (di bawah logo) ────────────────────────────────────
    for page in pages:
        st.page_link(page, icon=page.icon)

    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)

nav.run()