import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

class FuelDataProcessor:
    """
    Gère la transformation des données JSON brutes provenant de l'API des carburants 
    en une structure plate adaptée à l'insertion en base de données.
    """

    def process_data(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Aplatit la structure JSON imbriquée en un DataFrame Pandas.
        Chaque ligne du DataFrame résultant représente une lecture de prix unique.
        
        Args:
            raw_data (List[Dict[str, Any]]): La liste brute des stations renvoyée par l'API.

        Returns:
            pd.DataFrame: Un DataFrame plat contenant les informations combinées de la station et du prix.
                          Retourne un DataFrame vide si aucune donnée valide n'est trouvée.
        """
        flattened_records = []

        for station in raw_data:
            if 'prix' not in station or not station['prix']:
                continue

            station_info = {
                'api_station_id': station.get('id'),
                'address': station.get('adresse'),
                'city': station.get('ville'),
                'postal_code': station.get('cp'),
                'latitude': station.get('latitude'),
                'longitude': station.get('longitude')
            }

            for price_data in station['prix']:
                record = station_info.copy()
                
                try:
                    update_dt = datetime.strptime(price_data.get('maj'), '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    continue 

                record.update({
                    'fuel_name': price_data.get('nom'),
                    'price_value': float(price_data.get('valeur')),
                    'update_time': update_dt,
                    'date_id': int(update_dt.strftime('%Y%m%d'))
                })
                
                flattened_records.append(record)

        return pd.DataFrame(flattened_records)