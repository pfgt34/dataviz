import streamlit as st
from datetime import datetime
from api import appeler_api


def build_sidebar():
    st.sidebar.header("🎯 Filtres d'analyse")
    st.sidebar.markdown("*Ajustez les filtres pour analyser des segments spécifiques*")
    valeurs_filtres = appeler_api("/filters/valeurs")

    # dates
    date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
    date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')
    col1, col2 = st.sidebar.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
    with col2:
        date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

    categorie = st.sidebar.selectbox("Sélectionner une catégorie", options=["Toutes"] + valeurs_filtres['categories'])
    region = st.sidebar.selectbox("Sélectionner une région", options=["Toutes"] + valeurs_filtres['regions'])
    segment = st.sidebar.selectbox("Sélectionner un segment", options=["Tous"] + valeurs_filtres['segments'])

    if st.sidebar.button("🔄 Réinitialiser les filtres", use_container_width=True):
        st.rerun()

    params = {
        'date_debut': date_debut.strftime('%Y-%m-%d'),
        'date_fin': date_fin.strftime('%Y-%m-%d')
    }
    if categorie != "Toutes":
        params['categorie'] = categorie
    if region != "Toutes":
        params['region'] = region
    if segment != "Tous":
        params['segment'] = segment

    return params
