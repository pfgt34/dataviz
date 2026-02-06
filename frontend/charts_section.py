import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from api import appeler_api
from formatters import formater_euro, formater_nombre


def show_charts(params_filtres):
    st.header("📈 Analyses Détaillées")
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Produits", "📦 Catégories", "📅 Temporel", "🌍 Géographique"])

    with tab1:
        st.subheader("Top Produits")
        col_tri, col_limite = st.columns([3, 1])
        with col_tri:
            critere_tri = st.radio("Trier par", options=['ca', 'profit', 'quantite'], format_func=lambda x: {'ca': '💰 CA', 'profit': '💵 Profit', 'quantite': '📦 Quantité'}[x], horizontal=True)
        with col_limite:
            nb_produits = st.number_input("Afficher", min_value=5, max_value=50, value=10, step=5)
        top_produits = appeler_api("/kpi/produits/top", params={'limite': nb_produits, 'tri_par': critere_tri})
        df_produits = pd.DataFrame(top_produits)
        fig_produits = px.bar(df_produits, x=critere_tri, y='produit', color='categorie', orientation='h', height=500)
        fig_produits.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_produits, use_container_width=True)

    with tab2:
        st.subheader("Performance par Catégorie")
        categories = appeler_api("/kpi/categories")
        df_cat = pd.DataFrame(categories)
        col_left, col_right = st.columns(2)
        with col_left:
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(name='CA', x=df_cat['categorie'], y=df_cat['ca'], marker_color='#667eea'))
            fig_cat.add_trace(go.Bar(name='Profit', x=df_cat['categorie'], y=df_cat['profit'], marker_color='#764ba2'))
            st.plotly_chart(fig_cat, use_container_width=True)
        with col_right:
            fig_marge = px.bar(df_cat, x='categorie', y='marge_pct', color='marge_pct', color_continuous_scale='Viridis')
            st.plotly_chart(fig_marge, use_container_width=True)

    with tab3:
        st.subheader("Évolution Temporelle")
        granularite = st.radio("Période d'analyse", options=['jour','mois','annee'], format_func=lambda x: {'jour':'📅 Par jour','mois':'📊 Par mois','annee':'📈 Par année'}[x], horizontal=True)
        temporal = appeler_api("/kpi/temporel", params={'periode': granularite})
        df_temporal = pd.DataFrame(temporal)
        fig_temporal = make_subplots(rows=2, cols=1, subplot_titles=("Évolution du CA et Profit","Évolution du Nombre de Commandes"))
        fig_temporal.add_trace(go.Scatter(x=df_temporal['periode'], y=df_temporal['ca'], mode='lines+markers', name='CA', fill='tozeroy'), row=1, col=1)
        fig_temporal.add_trace(go.Scatter(x=df_temporal['periode'], y=df_temporal['profit'], mode='lines+markers', name='Profit'), row=1, col=1)
        fig_temporal.add_trace(go.Bar(x=df_temporal['periode'], y=df_temporal['nb_commandes'], name='Commandes'), row=2, col=1)
        st.plotly_chart(fig_temporal, use_container_width=True)

    with tab4:
        st.subheader("Performance Géographique")
        geo = appeler_api("/kpi/geographique")
        df_geo = pd.DataFrame(geo)
        fig_geo_ca = px.bar(df_geo, x='region', y='ca', color='ca', color_continuous_scale='Blues')
        st.plotly_chart(fig_geo_ca, use_container_width=True)
