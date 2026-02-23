import pandas as pd
import json
from typing import List, Dict, Any
from datetime import datetime

class FuelDataProcessor:
    """
    Gère la transformation des données de l'API Officielle.
    Correction : Gère le cas où 'prix' est un objet unique au lieu d'une liste.
    """

    def process_data(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        flattened_records = []

        for station in raw_data:
            prix_str = station.get('prix')
            if not prix_str:
                continue

            try:
                decoded_prix = json.loads(prix_str)
                
                if isinstance(decoded_prix, dict):
                    prix_list = [decoded_prix]
                elif isinstance(decoded_prix, list):
                    prix_list = decoded_prix
                else:
                    continue

            except json.JSONDecodeError:
                continue

            geom = station.get('geom') or {}
            
            station_info = {
                'api_station_id': str(station.get('id')),
                'address': station.get('adresse'),
                'city': station.get('ville'),
                'postal_code': station.get('cp'),
                'latitude': geom.get('lat'),
                'longitude': geom.get('lon')
            }

            for price_data in prix_list:
                if not isinstance(price_data, dict):
                    continue

                record = station_info.copy()
                
                date_str = price_data.get('@maj')
                
                try:
                    if date_str:
                        update_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        continue 
                except (ValueError, TypeError):
                    continue 

                valeur_raw = price_data.get('@valeur')
                if not valeur_raw:
                    continue

                try:
                    price_float = float(valeur_raw)
                except ValueError:
                    continue

                record.update({
                    'fuel_name': price_data.get('@nom'),
                    'price_value': price_float,
                    'update_time': update_dt,
                    'date_id': int(update_dt.strftime('%Y%m%d'))
                })
                
                flattened_records.append(record)

        if not flattened_records:
            return pd.DataFrame()

        return pd.DataFrame(flattened_records)