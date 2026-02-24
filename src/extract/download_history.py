import os
import requests
import zipfile
from io import BytesIO

def download_and_extract_history(years: list, output_dir: str = "data/raw"):
    """
    Télécharge et extrait les données annuelles de prix des carburants.
    Source : https://donnees.roulez-eco.fr/opendata/annee/YYYY
    """
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Dossier créé : {output_dir}")

    base_url = "https://donnees.roulez-eco.fr/opendata/annee"

    for year in years:
        url = f"{base_url}/{year}"
        print(f"--- Traitement de l'année {year} ---")
        
        try:
            print(f"Téléchargement depuis {url} ...")
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                z = zipfile.ZipFile(BytesIO(response.content))
                
                print(f"Extraction dans {output_dir} ...")
                z.extractall(output_dir)
                
                extracted_files = z.namelist()
                print(f"Fichiers extraits : {extracted_files}")
                
            else:
                print(f"Erreur : Impossible de télécharger {year} (Code {response.status_code})")
                
        except Exception as e:
            print(f"Erreur critique pour {year} : {e}")

    print("\n--- Téléchargement terminé ---")

if __name__ == "__main__":

    YEARS_TO_DOWNLOAD = [i for i in range(2015,2026)] 
    
    download_and_extract_history(YEARS_TO_DOWNLOAD)