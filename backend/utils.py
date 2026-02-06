from typing import Optional
import pandas as pd


def filtrer_dataframe(
    df: pd.DataFrame,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None
) -> pd.DataFrame:
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
