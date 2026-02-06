from fastapi import HTTPException
import pandas as pd
from config import DATASET_URL, logger


def load_data() -> pd.DataFrame:
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


# Chargement global
df = load_data()
