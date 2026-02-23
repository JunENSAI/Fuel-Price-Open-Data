import requests
from typing import Dict, Any, List

class FuelPriceClient:
    """
    Client pour l'API Officielle (data.economie.gouv.fr).
    Documentation : https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/api/
    """

    def __init__(self):
        self.base_url = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records"

    def get_data_by_department(self, dept_code: str = "35", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les données en filtrant par Code Postal via startswith.
        """
        where_clause = f'startswith(cp, "{dept_code}")'
        
        params = {
            "where": where_clause,
            "limit": limit
        }

        try:
            print(f"Appel API avec filtre : {where_clause}")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Erreur API ({response.status_code}): {response.text}")
                return []
            
            data = response.json()
            results = data.get("results", [])
            
            print(f"Succès ! {len(results)} stations récupérées.")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion : {e}")
            return []