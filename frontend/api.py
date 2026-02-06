import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Impossible de se connecter à l'API")
        st.info(f"Vérifiez que l'API est démarrée sur: {API_URL}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur API: {e}")
        st.stop()
