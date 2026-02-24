import os
import glob
from urllib.parse import quote_plus
from transform.xml_processor import XmlFuelProcessor
from load.db_loader import DatabaseLoader

def import_history_data():
    """
    Script dédié à l'ingestion massive des fichiers historiques XML.
    """
    
    raw_password = "open-data@fuel"
    encoded_password = quote_plus(raw_password)
    DB_URL = f"postgresql://user_fuel:{encoded_password}@localhost:5432/fuel_db"

    RAW_DIR = "data/raw"

    processor = XmlFuelProcessor()
    loader = DatabaseLoader(DB_URL)
    
    xml_files = glob.glob(os.path.join(RAW_DIR, "*.xml"))
    
    if not xml_files:
        print(f"Aucun fichier XML trouvé dans {RAW_DIR}")
        return

    print(f"--- Démarrage de l'import historique ({len(xml_files)} fichiers) ---")

    for file_path in xml_files:
        filename = os.path.basename(file_path)
        print(f"\nTraitement du fichier : {filename}")
        
        total_rows = 0
        
        for df_chunk in processor.parse_xml_file(file_path, chunk_size=5000):
            try:
                if not df_chunk.empty:
                    loader.load_data(df_chunk)
                    total_rows += len(df_chunk)
                    print(f"\r   -> Importé : {total_rows} lignes...", end="", flush=True)
            except Exception as e:
                print(f"\n   ERREUR sur un lot : {e}")
        
        print(f"\n   -> Terminé pour {filename}.")

    print("\n--- Importation Historique Terminée ---")

if __name__ == "__main__":
    import_history_data()