import sys
from urllib.parse import quote_plus
from extract.api_client import FuelPriceClient
from transform.data_processor import FuelDataProcessor
from load.db_loader import DatabaseLoader

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
    
    DEPT_CIBLE = "35" 
    LIMIT_RESULTS = 100

    # Extract
    print(f"Phase Extraction ")
    client = FuelPriceClient()

    raw_data = client.get_data_by_department(dept_code=DEPT_CIBLE, limit=LIMIT_RESULTS)
    
    if not raw_data:
        print("ERREUR : Aucune donnée récupérée. Vérifiez votre connexion internet ou le code département.")
        sys.exit(1)
        
    print(f"   => {len(raw_data)} stations brutes récupérées.")

    # Transform
    print(f" Phase Transformation")
    processor = FuelDataProcessor()

    df_clean = processor.process_data(raw_data)
    
    if df_clean.empty:
        print("AVERTISSEMENT : Aucun prix valide trouvé après transformation (formats incorrects ou données vides).")
        sys.exit(0)

    print(f"   => {len(df_clean)} lignes de prix prêtes à l'insertion.")
    print(f"   => Aperçu :\n{df_clean[['api_station_id', 'fuel_name', 'price_value', 'update_time']].head(3)}")

    # Load
    print(f"Phase Chargement dans ({DB_NAME})...")
    try:
        loader = DatabaseLoader(DB_URL)
        loader.load_data(df_clean)
        print("   -> Chargement terminé avec succès.")
    except Exception as e:
        print(f"ERREUR CRITIQUE lors du chargement en base : {e}")
        sys.exit(1)
    
    print("--- Pipeline ETL terminé avec succès ---")

if __name__ == "__main__":
    main()