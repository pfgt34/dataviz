import streamlit as st
from api import appeler_api
from formatters import formater_euro, formater_nombre, formater_pourcentage


def show_kpis(params_filtres):
    st.header("📊 Indicateurs Clés de Performance (KPI)")
    with st.spinner("📈 Chargement des KPI..."):
        kpi_data = appeler_api("/kpi/globaux", params=params_filtres)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Chiffre d'affaires", formater_euro(kpi_data['ca_total']))
        st.metric("📈 Marge moyenne", formater_pourcentage(kpi_data['marge_moyenne']))
    with col2:
        st.metric("🧾 Commandes", formater_nombre(kpi_data['nb_commandes']))
        st.metric("💵 Profit total", formater_euro(kpi_data['profit_total']))
    with col3:
        st.metric("👥 Clients", formater_nombre(kpi_data['nb_clients']))
        st.metric("🛒 Panier moyen", formater_euro(kpi_data['panier_moyen']))
    with col4:
        st.metric("📦 Quantité vendue", formater_nombre(kpi_data['quantite_vendue']))
        articles_par_commande = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
        st.metric("📊 Articles/commande", f"{articles_par_commande:.2f}")
    st.divider()
