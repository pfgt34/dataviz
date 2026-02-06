def formater_euro(valeur: float) -> str:
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")


def formater_nombre(valeur: int) -> str:
    return f"{valeur:,}".replace(",", " ")


def formater_pourcentage(valeur: float) -> str:
    return f"{valeur:.2f}%"
