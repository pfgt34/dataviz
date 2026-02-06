from fastapi import Query
from typing import Optional
from app_core import app
from data import df
from models import KPIGlobaux
from utils import filtrer_dataframe


@app.get("/kpi/globaux", response_model=KPIGlobaux, tags=["KPI"])
def get_kpi_globaux(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    ca_total = df_filtered['Sales'].sum()
    nb_commandes = df_filtered['Order ID'].nunique()
    nb_clients = df_filtered['Customer ID'].nunique()
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    quantite_vendue = int(df_filtered['Quantity'].sum())
    profit_total = df_filtered['Profit'].sum()
    marge_moyenne = (profit_total / ca_total * 100) if ca_total > 0 else 0
    return KPIGlobaux(
        ca_total=round(ca_total, 2),
        nb_commandes=nb_commandes,
        nb_clients=nb_clients,
        panier_moyen=round(panier_moyen, 2),
        quantite_vendue=quantite_vendue,
        profit_total=round(profit_total, 2),
        marge_moyenne=round(marge_moyenne, 2)
    )


@app.get("/kpi/produits/top", tags=["KPI"])
def get_top_produits(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits"),
    tri_par: str = Query("ca", regex="^(ca|profit|quantite)$", description="Critère de tri")
):
    produits = df.groupby(['Product Name', 'Category']).agg({
        'Sales': 'sum', 'Quantity': 'sum', 'Profit': 'sum'
    }).reset_index()
    colonne_tri = {'ca': 'Sales', 'profit': 'Profit', 'quantite': 'Quantity'}[tri_par]
    produits = produits.sort_values(colonne_tri, ascending=False).head(limite)
    result = []
    for _, row in produits.iterrows():
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "ca": round(row['Sales'], 2),
            "quantite": int(row['Quantity']),
            "profit": round(row['Profit'], 2)
        })
    return result


@app.get("/kpi/categories", tags=["KPI"])
def get_performance_categories():
    categories = df.groupby('Category').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique'
    }).reset_index()
    categories['marge_pct'] = (categories['Profit'] / categories['Sales'] * 100).round(2)
    categories.columns = ['categorie', 'ca', 'profit', 'nb_commandes', 'marge_pct']
    categories = categories.sort_values('ca', ascending=False)
    return categories.to_dict('records')


@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', regex='^(jour|mois|annee)$', description="Granularité")
):
    df_temp = df.copy()
    format_date = {'jour': '%Y-%m-%d', 'mois': '%Y-%m', 'annee': '%Y'}[periode]
    df_temp['periode'] = df_temp['Order Date'].dt.strftime(format_date)
    temporal = df_temp.groupby('periode').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique', 'Quantity': 'sum'
    }).reset_index()
    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    temporal = temporal.sort_values('periode')
    return temporal.to_dict('records')


@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique():
    geo = df.groupby('Region').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Customer ID': 'nunique', 'Order ID': 'nunique'
    }).reset_index()
    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo = geo.sort_values('ca', ascending=False)
    return geo.to_dict('records')


@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients")
):
    clients = df.groupby('Customer ID').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique', 'Customer Name': 'first'
    }).reset_index()
    clients.columns = ['customer_id', 'ca_total', 'profit_total', 'nb_commandes', 'nom']
    clients['valeur_commande_moy'] = (clients['ca_total'] / clients['nb_commandes']).round(2)
    top_clients = clients.sort_values('ca_total', ascending=False).head(limite)
    recurrence = {
        "clients_1_achat": len(clients[clients['nb_commandes'] == 1]),
        "clients_recurrents": len(clients[clients['nb_commandes'] > 1]),
        "nb_commandes_moyen": round(clients['nb_commandes'].mean(), 2),
        "total_clients": len(clients)
    }
    segments = df.groupby('Segment').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Customer ID': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients']
    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }
