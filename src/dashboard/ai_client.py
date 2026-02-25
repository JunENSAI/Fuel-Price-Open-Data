import streamlit as st
from google import genai
import pandas as pd
from sqlalchemy import text

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
        Voici le schéma des tables :

        1. dim_station (Info stations)
           - api_station_id (VARCHAR): ID unique
           - city (VARCHAR): Ville
           - dept_code (VARCHAR): Code département (ex: '35', '75')
           - address (VARCHAR)

        2. dim_fuel (Info carburants)
           - fuel_name (VARCHAR): Nom (Gazole, SP95, E10, E85, GPLc, SP98)

        3. fact_fuel_price (Table de faits volumineuse - 50 millions lignes)
           - price_value (FLOAT): Prix au litre
           - update_time (TIMESTAMP): Date précise
           - station_id, fuel_id (FK)
        
        4. mv_monthly_avg_price (Vue Matérialisée - À PRIVILÉGIER pour les moyennes/stats)
           - year (INT), month (INT)
           - dept_code (VARCHAR)
           - fuel_name (VARCHAR)
           - avg_price (FLOAT): Prix moyen
           - price_count (INT): Nombre de relevés

        RÈGLES IMPORTANTES :
        1. Si l'utilisateur demande une moyenne, une tendance ou une stat par département/année, UTILISE OBLIGATOIREMENT 'mv_monthly_avg_price'. C'est beaucoup plus rapide.
        2. N'utilise 'fact_fuel_price' que si l'utilisateur demande un prix précis à une date précise ou pour une station spécifique.
        3. Génère UNIQUEMENT le code SQL. Pas de balises markdown (```sql), pas d'explications avant ou après. Juste la requête brute.
        4. La requête doit être en lecture seule (SELECT). Interdiction d'utiliser DELETE, UPDATE, DROP, INSERT.
        5. Pour les recherches de ville, utilise ILIKE '%ville%'.
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
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
        if any(word in sql.upper() for word in forbidden):
            return None, " Sécurité : Cette requête contient des mots interdits."

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