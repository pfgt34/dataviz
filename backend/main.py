"""
API FastAPI pour l'analyse du dataset Superstore
🎯 Niveau débutant - Code simple et bien commenté
📊 Tous les KPI e-commerce implémentés
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import pandas as pd
from pydantic import BaseModel
import logging

# ============================================================================
# CONFIGURATION LOGGER
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================
DATASET_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"

# ============================================================================
# INITIALISATION FASTAPI
# ============================================================================
app = FastAPI(
    title="Superstore BI API",
    description="API d'analyse Business Intelligence pour le dataset Superstore",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CHARGEMENT DES DONNÉES
# ============================================================================

def load_data() -> pd.DataFrame:
    """
    Charge le dataset Superstore depuis GitHub
    Nettoie et prépare les données pour l'analyse
    
    Returns:
        pd.DataFrame: Dataset nettoyé et prêt à l'emploi
    """
    try:
        logger.info(f"Chargement du dataset depuis {DATASET_URL}")
        
        df = pd.read_csv(DATASET_URL, encoding='latin-1')
        df.columns = df.columns.str.strip()
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Ship Date'] = pd.to_datetime(df['Ship Date'])
        df = df.dropna(subset=['Order ID', 'Customer ID', 'Sales'])
        
        logger.info(f"✅ Dataset chargé : {len(df)} commandes")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des données : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de chargement : {str(e)}")


# Chargement au démarrage
df = load_data()

# ============================================================================
# MODÈLES PYDANTIC (Validation des réponses)
# ============================================================================

class KPIGlobaux(BaseModel):
    """KPI globaux"""
    ca_total: float
    nb_commandes: int
    nb_clients: int
    panier_moyen: float
    quantite_vendue: int
    profit_total: float
    marge_moyenne: float


class ProduitTop(BaseModel):
    """Produits top performers"""
    produit: str
    categorie: str
    ca: float
    quantite: int
    profit: float


class CategoriePerf(BaseModel):
    """Performance par catégorie"""
    categorie: str
    ca: float
    profit: float
    nb_commandes: int
    marge_pct: float

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def filtrer_dataframe(
    df: pd.DataFrame,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None
) -> pd.DataFrame:
    """
    Applique les filtres sur le dataframe
    
    Args:
        df: DataFrame source
        date_debut: Date de début (YYYY-MM-DD)
        date_fin: Date de fin (YYYY-MM-DD)
        categorie: Catégorie de produit
        region: Région géographique
        segment: Segment client
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    df_filtered = df.copy()
    
    if date_debut:
        df_filtered = df_filtered[df_filtered['Order Date'] >= date_debut]
    if date_fin:
        df_filtered = df_filtered[df_filtered['Order Date'] <= date_fin]
    if categorie and categorie != "Toutes":
        df_filtered = df_filtered[df_filtered['Category'] == categorie]
    if region and region != "Toutes":
        df_filtered = df_filtered[df_filtered['Region'] == region]
    if segment and segment != "Tous":
        df_filtered = df_filtered[df_filtered['Segment'] == segment]
    
    return df_filtered

# ============================================================================
# ENDPOINTS - INFORMATION
# ============================================================================

@app.get("/", tags=["Info"])
def root():
    """Endpoint racine - Informations sur l'API"""
    return {
        "message": "🛒 API Superstore BI",
        "version": "1.0.0",
        "dataset": "Sample Superstore",
        "nb_lignes": len(df),
        "periode": {
            "debut": df['Order Date'].min().strftime('%Y-%m-%d'),
            "fin": df['Order Date'].max().strftime('%Y-%m-%d')
        },
        "endpoints": {
            "documentation": "/docs",
            "kpi_globaux": "/kpi/globaux",
            "top_produits": "/kpi/produits/top",
            "categories": "/kpi/categories",
            "evolution_temporelle": "/kpi/temporel",
            "performance_geo": "/kpi/geographique",
            "analyse_clients": "/kpi/clients"
        }
    }


# ============================================================================
# ENDPOINTS - KPI PRINCIPAUX
# ============================================================================

@app.get("/kpi/globaux", response_model=KPIGlobaux, tags=["KPI"])
def get_kpi_globaux(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """
    📊 KPI GLOBAUX
    Calcule tous les indicateurs clés de performance
    """
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
    """
    🏆 TOP PRODUITS
    Retourne les meilleurs produits (ca, profit ou quantite)
    """
    produits = df.groupby(['Product Name', 'Category']).agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'Profit': 'sum'
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
    """
    📦 PERFORMANCE PAR CATÉGORIE
    Analyse complète par catégorie de produits
    """
    categories = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    categories['marge_pct'] = (categories['Profit'] / categories['Sales'] * 100).round(2)
    categories.columns = ['categorie', 'ca', 'profit', 'nb_commandes', 'marge_pct']
    categories = categories.sort_values('ca', ascending=False)
    
    return categories.to_dict('records')


@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', regex='^(jour|mois|annee)$', description="Granularité")
):
    """
    📈 ÉVOLUTION TEMPORELLE
    Analyse dans le temps (jour, mois ou année)
    """
    df_temp = df.copy()
    
    format_date = {'jour': '%Y-%m-%d', 'mois': '%Y-%m', 'annee': '%Y'}[periode]
    df_temp['periode'] = df_temp['Order Date'].dt.strftime(format_date)
    
    temporal = df_temp.groupby('periode').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    temporal = temporal.sort_values('periode')
    
    return temporal.to_dict('records')


@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique():
    """
    🌍 PERFORMANCE GÉOGRAPHIQUE
    Analyse par région
    """
    geo = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique'
    }).reset_index()
    
    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo = geo.sort_values('ca', ascending=False)
    
    return geo.to_dict('records')


@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients")
):
    """
    👥 ANALYSE CLIENTS
    Top clients, récurrence et segmentation
    """
    clients = df.groupby('Customer ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Customer Name': 'first'
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
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients']
    
    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }


# ============================================================================
# ENDPOINTS - FILTRES & DONNÉES
# ============================================================================

@app.get("/filters/valeurs", tags=["Filtres"])
def get_valeurs_filtres():
    """
    🎯 VALEURS POUR LES FILTRES
    Retourne toutes les valeurs disponibles pour les filtres du dashboard
    """
    return {
        "categories": sorted(df['Category'].unique().tolist()),
        "regions": sorted(df['Region'].unique().tolist()),
        "segments": sorted(df['Segment'].unique().tolist()),
        "etats": sorted(df['State'].unique().tolist()),
        "plage_dates": {
            "min": df['Order Date'].min().strftime('%Y-%m-%d'),
            "max": df['Order Date'].max().strftime('%Y-%m-%d')
        }
    }


@app.get("/data/commandes", tags=["Données brutes"])
def get_commandes(
    limite: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    📋 DONNÉES BRUTES
    Retourne les commandes avec pagination
    """
    total = len(df)
    commandes = df.iloc[offset:offset+limite].copy()
    
    commandes['Order Date'] = commandes['Order Date'].dt.strftime('%Y-%m-%d')
    commandes['Ship Date'] = commandes['Ship Date'].dt.strftime('%Y-%m-%d')
    
    return {
        "total": total,
        "limite": limite,
        "offset": offset,
        "data": commandes.to_dict('records')
    }

# ============================================================================
# DÉMARRAGE SERVEUR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API Superstore BI sur http://localhost:8000")
    print("📚 Documentation disponible sur http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)