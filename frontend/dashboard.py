"""
Orchestrateur Streamlit : assemble les sections du dashboard
Les composants UI sont découpés sous forme de modules dans `frontend/`.
"""

from style_config import apply_page_config, apply_css
from sidebar import build_sidebar
from api import appeler_api
from kpi_section import show_kpis
from charts_section import show_charts
from clients_section import show_clients
from commercial_section import show_commercial_view
import streamlit as st


def main():
    apply_page_config()
    apply_css()

    with st.spinner("🔄 Connexion à l'API..."):
        info_api = appeler_api("/")
        st.success(f"✅ Connecté à l'API - Dataset : {info_api['dataset']} ({info_api['nb_lignes']} lignes)")

    st.title("🛒 Superstore BI Dashboard")
    st.markdown("**Analyse Business Intelligence du dataset Superstore - Tableau de bord interactif**")
    st.divider()

    params = build_sidebar()

    tab1, tab2 = st.tabs(["Vue standard", "Vue commerciale (atelier)"])

    with tab1:
        show_kpis(params)
        show_charts(params)
        show_clients(params)

    with tab2:
        show_commercial_view(params)


if __name__ == "__main__":
    main()
