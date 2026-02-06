import streamlit as st


def apply_page_config():
    st.set_page_config(
        page_title="Superstore BI Dashboard",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_css():
    st.markdown(
        """
    <style>
        .kpi-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:20px; border-radius:10px; color:white }
        .stMetric { background-color: #f8f9fa; padding: 15px; border-radius:8px; border-left:4px solid #667eea }
        h1 { color:#2c3e50; font-weight:700 }
        h2 { color:#34495e; font-weight:600 }
    </style>
    """,
        unsafe_allow_html=True,
    )
