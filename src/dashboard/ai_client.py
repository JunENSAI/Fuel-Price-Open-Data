import streamlit as st
from google import genai
import pandas as pd
from sqlalchemy import text
import re

class FuelAIClient:
    def __init__(self, engine):
        self.engine = engine
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except FileNotFoundError:
            st.error("Il manque le fichier .streamlit/secrets.toml avec GEMINI_API_KEY")
            return

        self.client = genai.Client(api_key=api_key)
        
        self.system_instruction = """
        Tu es un expert SQL PostgreSQL. Tu as accès à une base de données de prix des carburants.
        
        SCHEMA DES TABLES (à respecter scrupuleusement) :

        1. dim_station (Info stations)
           - station_id (INT): Clé primaire interne (PK) <-- à utiliser pour les jointures
           - api_station_id (VARCHAR): ID Gouvernemental (ex: '3500001')
           - city (VARCHAR): Ville
           - dept_code (VARCHAR): Code département (ex: '35')
           - address (VARCHAR)

        2. dim_fuel (Info carburants)
           - fuel_id (INT): Clé primaire (PK)
           - fuel_name (VARCHAR): Nom (Gazole, SP95, E10, E85, GPLc, SP98)

        3. fact_fuel_price (Table de faits - Historique)
           - price_value (FLOAT): Prix au litre
           - update_time (TIMESTAMP): Date précise
           - station_id (INT): Clé étrangère (FK) vers dim_station.station_id
           - fuel_id (INT): Clé étrangère (FK) vers dim_fuel.fuel_id
        
        4. mv_monthly_avg_price (Vue Matérialisée - À PRIVILÉGIER pour les moyennes)
           - year (INT), month (INT)
           - dept_code (VARCHAR)
           - fuel_name (VARCHAR)
           - avg_price (FLOAT)

        RÈGLES DE JOINTURE (CRUCIAL) :
        - Pour joindre 'fact_fuel_price' et 'dim_station', utilise TOUJOURS : 
          ON fact_fuel_price.station_id = dim_station.station_id
        - NE JAMAIS joindre sur 'api_station_id'.

        RÈGLES GÉNÉRALES :
        1. Si on demande "le moins cher" ou un prix actuel précis : Utilise 'fact_fuel_price' et filtre sur la date la plus récente (ORDER BY update_time DESC LIMIT 1).
        2. Pour les villes : Utilise ILIKE '%ville%'.
        3. Pas de balises markdown, juste le code SQL pur.
        """

    def generate_sql(self, user_question):
        """Transforme la question en SQL via Gemini."""
        try:
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=f"{self.system_instruction}\n\nQuestion utilisateur : {user_question}"
            )

            sql = response.text.replace("```sql", "").replace("```", "").strip()
            return sql
        except Exception as e:
            return f"Erreur IA : {e}"

    def execute_query(self, sql):
        """Exécute le SQL généré de manière sécurisée."""
        forbidden_patterns = [
            r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", 
            r"\bINSERT\b", r"\bALTER\b", r"\bTRUNCATE\b"
        ]
        upper_sql = sql.upper()
        for pattern in forbidden_patterns:
            if re.search(pattern, upper_sql):
                return None, f"Sécurité : Mot interdit détecté ({pattern.replace(r'\\b', '')})"

        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)
            return df, None
        except Exception as e:
            return None, f"Erreur SQL : {e}"

    def summarize_results(self, user_question, df):
        """Demande à Gemini de faire une phrase de synthèse des résultats."""
        if df.empty:
            return "Aucun résultat trouvé."
        
        data_preview = df.head(10).to_string()
        
        prompt = f"""
        Question: {user_question}
        Données (extrait):
        {data_preview}
        
        Fais une réponse courte et naturelle (en français) qui résume ces données. 
        Si c'est un chiffre unique, donne-le simplement.
        """
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text