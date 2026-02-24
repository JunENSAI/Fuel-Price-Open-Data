import sys
import os
import time
import json
from urllib.parse import quote_plus
from extract.api_client import FuelPriceClient
from transform.data_processor import FuelDataProcessor
from load.db_loader import DatabaseLoader

def load_departements_list(filepath="data/departements.json"):
    """Charge la liste des codes départements depuis le fichier JSON."""
    if not os.path.exists(filepath):
        print(f"ERREUR : Le fichier {filepath} est introuvable.")
        return []
    
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    """
    Point d'entrée principal de l'orchestrateur ETL.
    Coordonne l'extraction depuis l'API officielle, la transformation des données complexes,
    et le chargement dans le schéma en étoile PostgreSQL.
    """
    
    # Config
    raw_password = "open-data@fuel"
    encoded_password = quote_plus(raw_password)
    
    # Paramètres de connexion BDD
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "fuel_db"
    DB_USER = "user_fuel"
    DB_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    client = FuelPriceClient()
    processor = FuelDataProcessor()
    
    try:
        loader = DatabaseLoader(DB_URL)
    except Exception as e:
        print(f"ERREUR CRITIQUE BDD : {e}")
        sys.exit(1)
    
    dept_list = load_departements_list()
    if not dept_list:
        sys.exit(1)
    
    total_stations_global = 0

    for dept in dept_list:
        print(f"\nTraitement Département : {dept}")
        
        # 1. Extraction
        raw_data = client.get_all_data_by_dept(dept)
        
        if not raw_data:
            print(f"   -> Aucune donnée.")
            continue

        # 2. Transformation
        df_clean = processor.process_data(raw_data)
        
        if df_clean.empty:
            print(f"   -> Données vides après transformation.")
            continue

        # 3. Chargement
        try:
            loader.load_data(df_clean)
            count = len(df_clean)
            total_stations_global += count
            print(f"   -> Succès : {count} prix insérés en base.")
        except Exception as e:
            print(f"   -> ERREUR Chargement BDD : {e}")

        # pause pour ne saturer l'appel à l'api
        time.sleep(1)

    print(f"\n--- FIN DU TRAITEMENT ---")
    print(f"Total global des prix mis à jour : {total_stations_global}")

if __name__ == "__main__":
    main()