import requests
from typing import Dict, Any, List
import time

class FuelPriceClient:
    """
    Client pour l'API Officielle (data.economie.gouv.fr).
    Documentation : https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/api/
    """

    def __init__(self):
        self.base_url = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records"

    def get_all_data_by_dept(self, dept_code: str) -> List[Dict[str, Any]]:
        """
        Récupère TOUTES les données d'un département en paginant automatiquement.
        Ne s'arrête que lorsque l'API ne renvoie plus de résultats.
        """
        all_results = []
        offset = 0
        batch_size = 100
        
        print(f"   [API] Récupération totale pour le département {dept_code}...")

        while True:
            params = {
                "where": f'startswith(cp, "{dept_code}")',
                "limit": batch_size,
                "offset": offset
            }

            try:
                # Appel API
                response = requests.get(self.base_url, params=params, timeout=20)
                
                if response.status_code == 429:
                    print("   [API] Trop de requêtes (Rate Limit). Pause de 5sec...")
                    time.sleep(5)
                    continue

                if response.status_code != 200:
                    print(f"   [Erreur] API Status {response.status_code} à l'offset {offset}")
                    break
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                all_results.extend(results)

                offset += batch_size

                if offset % 500 == 0:
                    print(f"      -> {len(all_results)} lignes chargées...", end="\r")

            except requests.exceptions.RequestException as e:
                print(f"   [Erreur Connexion] {e}")
                break
        
        print(f"   [API] Terminé : {len(all_results)} stations trouvées pour le {dept_code}.")
        return all_results