from fastapi import Query
from typing import Optional
from datetime import datetime, timedelta
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
    tri_par: str = Query("ca", regex="^(ca|profit|quantite)$", description="Critère de tri"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    produits = df_filtered.groupby(['Product Name', 'Category']).agg({
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
def get_performance_categories(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    categories = df_filtered.groupby('Category').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique'
    }).reset_index()
    categories['marge_pct'] = (categories['Profit'] / categories['Sales'] * 100).round(2)
    categories.columns = ['categorie', 'ca', 'profit', 'nb_commandes', 'marge_pct']
    categories = categories.sort_values('ca', ascending=False)
    return categories.to_dict('records')


@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', regex='^(jour|mois|annee)$', description="Granularité"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_temp = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment).copy()
    format_date = {'jour': '%Y-%m-%d', 'mois': '%Y-%m', 'annee': '%Y'}[periode]
    df_temp['periode'] = df_temp['Order Date'].dt.strftime(format_date)
    temporal = df_temp.groupby('periode').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique', 'Quantity': 'sum'
    }).reset_index()
    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    temporal = temporal.sort_values('periode')
    return temporal.to_dict('records')


@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    geo = df_filtered.groupby('Region').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Customer ID': 'nunique', 'Order ID': 'nunique'
    }).reset_index()
    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo = geo.sort_values('ca', ascending=False)
    return geo.to_dict('records')


@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)

    clients = df_filtered.groupby('Customer ID').agg({
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
    segments = df_filtered.groupby('Segment').agg({
        'Sales': 'sum', 'Profit': 'sum', 'Customer ID': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients']
    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }


@app.get("/kpi/commercial/overview", tags=["KPI"])
def get_commercial_overview(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    df_current = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)

    ca_total = float(df_current['Sales'].sum())
    profit_total = float(df_current['Profit'].sum())
    nb_commandes = int(df_current['Order ID'].nunique())
    nb_clients = int(df_current['Customer ID'].nunique())
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    marge_pct = (profit_total / ca_total * 100) if ca_total > 0 else 0
    remise_moyenne_pct = float(df_current['Discount'].mean() * 100) if len(df_current) > 0 else 0
    profit_par_commande = profit_total / nb_commandes if nb_commandes > 0 else 0

    clients_df = df_current.groupby('Customer ID', as_index=False).agg({'Sales': 'sum'})
    top_clients_ca = float(clients_df.nlargest(10, 'Sales')['Sales'].sum()) if len(clients_df) > 0 else 0
    concentration_top_clients_pct = (top_clients_ca / ca_total * 100) if ca_total > 0 else 0

    categories = df_current.groupby('Category', as_index=False).agg({'Sales': 'sum', 'Profit': 'sum'})
    if len(categories) > 0:
        categories['marge_pct'] = categories.apply(
            lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0,
            axis=1,
        )
        categories = categories.sort_values('Sales', ascending=False)
        categories_alertes = categories.nsmallest(2, 'marge_pct')[['Category', 'marge_pct']].to_dict('records')
    else:
        categories_alertes = []

    variation_ca_pct = 0
    variation_profit_pct = 0
    if date_debut and date_fin:
        start_date = datetime.strptime(date_debut, "%Y-%m-%d")
        end_date = datetime.strptime(date_fin, "%Y-%m-%d")
        if end_date >= start_date:
            period_days = (end_date - start_date).days + 1
            prev_end = start_date - timedelta(days=1)
            prev_start = prev_end - timedelta(days=period_days - 1)
            prev_df = filtrer_dataframe(
                df,
                prev_start.strftime("%Y-%m-%d"),
                prev_end.strftime("%Y-%m-%d"),
                categorie,
                region,
                segment,
            )
            prev_ca = float(prev_df['Sales'].sum())
            prev_profit = float(prev_df['Profit'].sum())
            if prev_ca > 0:
                variation_ca_pct = ((ca_total - prev_ca) / prev_ca) * 100
            if prev_profit != 0:
                variation_profit_pct = ((profit_total - prev_profit) / abs(prev_profit)) * 100

    return {
        "ca_total": round(ca_total, 2),
        "profit_total": round(profit_total, 2),
        "nb_commandes": nb_commandes,
        "nb_clients": nb_clients,
        "panier_moyen": round(panier_moyen, 2),
        "marge_pct": round(marge_pct, 2),
        "remise_moyenne_pct": round(remise_moyenne_pct, 2),
        "profit_par_commande": round(profit_par_commande, 2),
        "concentration_top_clients_pct": round(concentration_top_clients_pct, 2),
        "variation_ca_pct": round(variation_ca_pct, 2),
        "variation_profit_pct": round(variation_profit_pct, 2),
        "categories_alertes": categories_alertes,
    }
