import requests
import pandas as pd
from typing import List, Dict, Any

class FuelPriceClient:
    """
    Client pour l'API des prix des carburants.
    Doc: https://swagger.2aaz.fr/
    """

    def __init__(self):
        self.base_url = "https://api.prix-carburants.2aaz.fr"

    def get_stations_by_dept(self, dept_code: str = "35") -> List[Dict[str, Any]]:
        """
        Récupère toutes les stations et leurs prix pour un département donné.
        
        Args:
            dept_code (str): Le numéro du département (ex: '35' pour Ille-et-Vilaine).
        """
        url = f"{self.base_url}/station/departement/{dept_code}"
        
        try:
            print(f"Appel API : {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"{len(data)} stations trouvées pour le département {dept_code}.")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'appel API : {e}")
            return []