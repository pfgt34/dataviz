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
    """
    backend.main
    Entrypoint minimal qui expose `app` en important le coeur de l'application
    Les routes et la logique sont découpées en modules sous `backend/`.
    """

    from app_core import app  # FastAPI app centralisé

    # Import des modules pour enregister les routes (side-effect imports)
    import endpoints_kpi  # noqa: F401
    import endpoints_filters  # noqa: F401


    if __name__ == "__main__":
        import uvicorn
        print("🚀 Démarrage de l'API Superstore BI sur http://localhost:8000")
        print("📚 Documentation disponible sur http://localhost:8000/docs")
        uvicorn.run(app, host="0.0.0.0", port=8000)