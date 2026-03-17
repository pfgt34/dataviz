import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from api import appeler_api
from formatters import formater_euro, formater_nombre, formater_pourcentage


def _label_variation(value: float) -> str:
    if value > 0:
        return f"+{value:.2f}% vs periode precedente"
    return f"{value:.2f}% vs periode precedente"


def _build_storytelling(overview: dict) -> list[str]:
    messages = []

    if overview["variation_ca_pct"] >= 5:
        messages.append(
            "La dynamique commerciale est positive: le chiffre d'affaires progresse sensiblement sur la periode analysee."
        )
    elif overview["variation_ca_pct"] <= -5:
        messages.append(
            "Le chiffre d'affaires recule par rapport a la periode precedente: une action commerciale rapide est recommandee."
        )
    else:
        messages.append(
            "Le chiffre d'affaires est relativement stable: le levier principal est l'amelioration de la rentabilite."
        )

    if overview["marge_pct"] < 10:
        messages.append(
            "La marge globale est faible. Prioriser les offres et segments a meilleure contribution peut ameliorer le profit sans sur-solliciter les equipes."
        )
    else:
        messages.append(
            "La marge reste correcte. L'enjeu est de maintenir ce niveau tout en accelerant les categories les plus performantes."
        )

    if overview["concentration_top_clients_pct"] > 35:
        messages.append(
            "Le CA est concentre sur un nombre limite de clients: opportunite de diversification du portefeuille pour reduire le risque commercial."
        )
    else:
        messages.append(
            "Le portefeuille client est relativement equilibre, ce qui limite le risque de dependance a quelques grands comptes."
        )

    return messages


def show_commercial_view(params_filtres: dict):
    st.header("Vue Commerciale - KPI & Aide a la decision")
    st.caption(
        "Objectif atelier: proposer un reporting utile a la decision, en combinant KPI pertinents, visualisations ciblees et narration metier."
    )

    overview = appeler_api("/kpi/commercial/overview", params=params_filtres)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Chiffre d'affaires",
            formater_euro(overview["ca_total"]),
            delta=_label_variation(overview["variation_ca_pct"]),
        )
    with col2:
        st.metric(
            "Profit total",
            formater_euro(overview["profit_total"]),
            delta=_label_variation(overview["variation_profit_pct"]),
        )
    with col3:
        st.metric("Marge moyenne", formater_pourcentage(overview["marge_pct"]))
        st.metric("Remise moyenne", formater_pourcentage(overview["remise_moyenne_pct"]))
    with col4:
        st.metric("Clients actifs", formater_nombre(overview["nb_clients"]))
        st.metric("Panier moyen", formater_euro(overview["panier_moyen"]))

    tab1, tab2, tab3 = st.tabs(
        ["Performance commerciale", "Clients & risques", "Storytelling & decisions"]
    )

    with tab1:
        temporal = appeler_api("/kpi/temporel", params={**params_filtres, "periode": "mois"})
        df_temporal = pd.DataFrame(temporal)

        categories = appeler_api("/kpi/categories", params=params_filtres)
        df_cat = pd.DataFrame(categories)

        if df_temporal.empty or df_cat.empty:
            st.warning("Pas assez de donnees sur ce perimetre pour afficher les analyses de performance.")
        else:
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Evolution du CA et du profit")
                fig_trend = go.Figure()
                fig_trend.add_trace(
                    go.Scatter(
                        x=df_temporal["periode"],
                        y=df_temporal["ca"],
                        mode="lines+markers",
                        name="CA",
                    )
                )
                fig_trend.add_trace(
                    go.Scatter(
                        x=df_temporal["periode"],
                        y=df_temporal["profit"],
                        mode="lines+markers",
                        name="Profit",
                    )
                )
                fig_trend.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_trend, use_container_width=True)

            with col_right:
                st.subheader("Rentabilite par categorie")
                fig_margin = px.bar(
                    df_cat,
                    x="categorie",
                    y="marge_pct",
                    color="marge_pct",
                    color_continuous_scale="RdYlGn",
                )
                fig_margin.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_margin, use_container_width=True)

    with tab2:
        clients = appeler_api("/kpi/clients", params={**params_filtres, "limite": 15})
        geo = appeler_api("/kpi/geographique", params=params_filtres)
        df_clients = pd.DataFrame(clients["top_clients"])
        df_geo = pd.DataFrame(geo)

        if df_clients.empty or df_geo.empty:
            st.warning("Pas assez de donnees pour afficher la vue clients et geographique sur ce filtre.")
        else:
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Dependance aux meilleurs clients")
                fig_clients = px.bar(
                    df_clients.head(10),
                    x="ca_total",
                    y="nom",
                    orientation="h",
                    color="nb_commandes",
                )
                fig_clients.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=420,
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig_clients, use_container_width=True)

            with col_right:
                st.subheader("Performance geographique")
                fig_geo = px.scatter(
                    df_geo,
                    x="nb_clients",
                    y="ca",
                    size="nb_commandes",
                    color="profit",
                    hover_name="region",
                    color_continuous_scale="Tealgrn",
                )
                fig_geo.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_geo, use_container_width=True)

        st.info(
            f"Concentration du CA sur les 10 meilleurs clients: {overview['concentration_top_clients_pct']:.2f}%"
        )

    with tab3:
        st.subheader("Lecture metier")
        for insight in _build_storytelling(overview):
            st.write(f"- {insight}")

        st.subheader("Points d'attention")
        if overview["categories_alertes"]:
            for alert in overview["categories_alertes"]:
                st.warning(
                    f"Categorie a surveiller: {alert['Category']} (marge {alert['marge_pct']:.2f}%)"
                )
        else:
            st.success("Aucune categorie critique detectee sur le perimetre filtre.")

        st.subheader("Questions decisionnelles couvertes")
        st.write("- Quelle est la tendance recente du chiffre d'affaires et du profit ?")
        st.write("- Ou se situent les poches de rentabilite et les zones a faible marge ?")
        st.write("- Le portefeuille client est-il trop concentre ?")
        st.write("- Quelles regions meritent un effort commercial prioritaire ?")
