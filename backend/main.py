"""
backend.main
Entrypoint minimal qui expose `app` en important le coeur de l'application.
Les routes et la logique sont decoupees en modules sous `backend/`.
"""

from app_core import app

# Side-effect imports pour enregistrer les routes
import endpoints_kpi  # noqa: F401
import endpoints_filters  # noqa: F401


if __name__ == "__main__":
    import uvicorn

    print("Demarrage de l'API Superstore BI sur http://localhost:8000")
    print("Documentation disponible sur http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
