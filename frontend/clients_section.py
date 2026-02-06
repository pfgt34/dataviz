import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from api import appeler_api
from formatters import formater_nombre


def show_clients():
    st.header("👥 Analyse Clients")
    clients_data = appeler_api("/kpi/clients", params={'limite': 10})
    col_client1, col_client2 = st.columns([2, 1])
    with col_client1:
        st.subheader("🏆 Top 10 Clients")
        df_top_clients = pd.DataFrame(clients_data['top_clients'])
        fig_clients = px.bar(df_top_clients, x='ca_total', y='nom', orientation='h', color='nb_commandes')
        st.plotly_chart(fig_clients, use_container_width=True)
    with col_client2:
        st.subheader("📊 Statistiques clients")
        rec = clients_data['recurrence']
        st.metric("Total clients", formater_nombre(rec['total_clients']))
        st.metric("Clients récurrents", formater_nombre(rec['clients_recurrents']))
        st.metric("Clients 1 achat", formater_nombre(rec['clients_1_achat']))
        st.metric("Commandes/client", f"{rec['nb_commandes_moyen']:.2f}")
        taux_fidelisation = (rec['clients_recurrents'] / rec['total_clients'] * 100) if rec['total_clients'] > 0 else 0
        st.metric("Taux de fidélisation", f"{taux_fidelisation:.1f}%")
    st.subheader("💼 Performance par Segment Client")
    df_segments = pd.DataFrame(clients_data['segments'])
    fig_segments = go.Figure()
    fig_segments.add_trace(go.Bar(name='CA', x=df_segments['segment'], y=df_segments['ca']))
    fig_segments.add_trace(go.Bar(name='Profit', x=df_segments['segment'], y=df_segments['profit']))
    st.plotly_chart(fig_segments, use_container_width=True)
