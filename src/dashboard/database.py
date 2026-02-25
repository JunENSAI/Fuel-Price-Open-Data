import streamlit as st
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import pandas as pd

@st.cache_resource
def get_db_engine():
    """
    Crée et met en cache la connexion à la base de données.
    """
    raw_password = "open-data@fuel"
    encoded_password = quote_plus(raw_password)
    DB_URL = f"postgresql://user_fuel:{encoded_password}@localhost:5432/fuel_db"
    
    return create_engine(DB_URL)

@st.cache_data(ttl=3600)
def load_data(query_str, _engine):
    """
    Exécute une requête SQL et renvoie un DataFrame.
    Le paramètre _engine est préfixé par _ pour dire à Streamlit de ne pas le hasher.
    """
    with _engine.connect() as conn:
        return pd.read_sql(text(query_str), conn)