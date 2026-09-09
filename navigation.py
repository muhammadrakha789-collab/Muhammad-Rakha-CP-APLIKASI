"""Unified sidebar navigation for the Client Ledger Streamlit workspace."""

import streamlit as st

NAV_ITEMS = [
    ("HOME", "Home", "Home.py", "⌂"),
    ("ANALYTICS", "Ringkasan", "pages/1_Ringkasan.py", "01"),
    ("ANALYTICS", "Detail Segmen", "pages/2_Detail_Segmen.py", "02"),
    ("DATA", "Data Pelanggan", "pages/3_Data_Pelanggan.py", "03"),
    ("DATA LAB", "Unggah Data Baru", "pages/4_Unggah_Data_Baru.py", "04"),
]


def render_navigation(active="Home", user_name=None):
    """Render a consistent, compact sidebar navigation across all pages."""
    st.sidebar.markdown(
        """
        <style>
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display:none; }
        section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { border:1px solid transparent; border-radius:10px; margin:2px 0; padding:8px 10px; transition:all .16s ease; }
        section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover { background:#111722; border-color:#29334A; transform:translateX(2px); }
        section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] { background:linear-gradient(90deg,rgba(139,92,246,.16),rgba(34,211,238,.05)); border-color:#39465F; box-shadow:inset 3px 0 0 #8B5CF6; }
        section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] span { color:#F4F7FB !important; font-weight:700; }
        .nav-heading { color:#F4F7FB; font-family:'Space Grotesk',sans-serif; font-size:.82rem; font-weight:700; letter-spacing:.10em; }
        .nav-intro { color:#64748B; font-size:.68rem; margin:2px 0 14px; }
        .nav-group { color:#64748B; font-size:.59rem; font-weight:700; letter-spacing:.14em; margin:14px 3px 5px; }
        .nav-user { margin-top:14px; padding:10px 11px; border:1px solid #29334A; border-radius:11px; background:linear-gradient(135deg,rgba(139,92,246,.10),rgba(34,211,238,.04)); }
        .nav-user span { display:block; color:#64748B; font-size:.56rem; letter-spacing:.12em; font-weight:700; margin-bottom:3px; }
        .nav-user b { color:#E6EBF2; font-size:.76rem; }
        .nav-footer { margin-top:13px; padding:11px 3px 0; border-top:1px solid #202938; color:#64748B; font-size:.62rem; line-height:1.55; }
        .nav-footer b { color:#8D98A9; letter-spacing:.08em; }
        .nav-footer span { color:#475569; }
        </style>
        <div class='nav-heading'>WORKSPACE</div>
        <div class='nav-intro'>Customer intelligence workspace</div>
        """,
        unsafe_allow_html=True,
    )

    current_group = None
    for group, label, path, icon in NAV_ITEMS:
        if group != current_group:
            st.sidebar.markdown(f"<div class='nav-group'>{group}</div>", unsafe_allow_html=True)
            current_group = group
        st.page_link(path, label=f"{icon}  {label}", use_container_width=True)

    if user_name:
        st.sidebar.markdown(
            f"<div class='nav-user'><span>LOGGED IN AS</span><b>{user_name}</b></div>",
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        "<div class='nav-footer'><b>CLIENT LEDGER</b><br>RFM · K-Means · Customer Intelligence<br><span>v2 · Executive Workspace</span></div>",
        unsafe_allow_html=True,
    )
