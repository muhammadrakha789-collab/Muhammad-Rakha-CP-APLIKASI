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
    """Render the same navigation structure on every authenticated page."""
    st.sidebar.markdown(
        """
        <div class='nav-heading'>WORKSPACE</div>
        <div class='nav-intro'>Customer intelligence workspace</div>
        """,
        unsafe_allow_html=True,
    )

    current_group = None
    for group, label, path, icon in NAV_ITEMS:
        if group != current_group:
            st.sidebar.markdown(
                f"<div class='nav-group'>{group}</div>",
                unsafe_allow_html=True,
            )
            current_group = group
        st.page_link(
            path,
            label=f"{icon}  {label}",
            use_container_width=True,
        )

    if user_name:
        st.sidebar.markdown(
            f"<div class='nav-user'><span>LOGGED IN AS</span><b>{user_name}</b></div>",
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        "<div class='nav-footer'><b>CLIENT LEDGER</b><br>RFM · K-Means · Customer Intelligence<br><span>v2 · Executive Workspace</span></div>",
        unsafe_allow_html=True,
    )
