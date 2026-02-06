from app_core import app
from data import df
from fastapi import Query


@app.get("/", tags=["Info"])
def root():
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


@app.get("/filters/valeurs", tags=["Filtres"])
def get_valeurs_filtres():
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
def get_commandes(limite: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    total = len(df)
    commandes = df.iloc[offset:offset+limite].copy()
    commandes['Order Date'] = commandes['Order Date'].dt.strftime('%Y-%m-%d')
    commandes['Ship Date'] = commandes['Ship Date'].dt.strftime('%Y-%m-%d')
    return {"total": total, "limite": limite, "offset": offset, "data": commandes.to_dict('records')}
