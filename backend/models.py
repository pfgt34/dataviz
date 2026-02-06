from pydantic import BaseModel


class KPIGlobaux(BaseModel):
    ca_total: float
    nb_commandes: int
    nb_clients: int
    panier_moyen: float
    quantite_vendue: int
    profit_total: float
    marge_moyenne: float


class ProduitTop(BaseModel):
    produit: str
    categorie: str
    ca: float
    quantite: int
    profit: float


class CategoriePerf(BaseModel):
    categorie: str
    ca: float
    profit: float
    nb_commandes: int
    marge_pct: float
