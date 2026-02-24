import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from typing import Generator

class XmlFuelProcessor:
    """
    Gère les archives XML (2015-2025) [grand volume de données qui pouvait faire bugger l'API].
    """

    def parse_xml_file(self, file_path: str, chunk_size: int = 5000) -> Generator[pd.DataFrame, None, None]:
        print(f"   [Debug] Lecture du fichier {file_path}...")
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except Exception as e:
            print(f"   [Erreur] Impossible de lire le XML : {e}")
            return

        records = []
        count_pdv = 0
        count_prix = 0
        
        for pdv in root.findall('pdv'):
            count_pdv += 1
            
            try:
                lat_raw = pdv.get('latitude')
                lon_raw = pdv.get('longitude')
                
                if not lat_raw or not lon_raw:
                    continue

                lat = float(lat_raw) / 100000
                lon = float(lon_raw) / 100000
            except (ValueError, TypeError):
                continue

            adresse_elem = pdv.find('adresse')
            ville_elem = pdv.find('ville')
            cp = pdv.get('cp')
            
            station_info = {
                'api_station_id': str(pdv.get('id')),
                'address': adresse_elem.text if adresse_elem is not None else None,
                'city': ville_elem.text if ville_elem is not None else None,
                'postal_code': cp,
                'latitude': lat,
                'longitude': lon
            }

            for prix in pdv.findall('prix'):
                valeur_raw = prix.get('valeur')
                nom = prix.get('nom')
                maj = prix.get('maj')
                
                if not all([valeur_raw, nom, maj]):
                    continue

                try:
                    maj_clean = maj.replace('T', ' ')
                    
                    update_dt = datetime.strptime(maj_clean, '%Y-%m-%d %H:%M:%S')
                    
                    price_val = float(valeur_raw) / 1000
                    
                    record = station_info.copy()
                    record.update({
                        'fuel_name': nom,
                        'price_value': price_val,
                        'update_time': update_dt,
                        'date_id': int(update_dt.strftime('%Y%m%d'))
                    })
                    
                    records.append(record)
                    count_prix += 1

                except ValueError as e:
                    continue

                if len(records) >= chunk_size:
                    yield pd.DataFrame(records)
                    records = []

        if records:
            yield pd.DataFrame(records)
            
        print(f"   [Debug] Analyse terminée : {count_pdv} stations scanées, {count_prix} prix trouvés.")