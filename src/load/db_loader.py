import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

class DatabaseLoader:
    """
    Gère l'insertion des données transformées.
    Assure l'intégrité référentielle en mettant à jour les dimensions avant d'insérer les faits.
    """

    def __init__(self, connection_string: str):
        """
        Initialise la connexion à la base de données.

        Args:
            connection_string (str): Chaîne de connexion SQLAlchemy 
            (ex: 'postgresql://user:pass@host:port/dbname').
        """
        self.engine = create_engine(connection_string)

    def load_data(self, df: pd.DataFrame):
        """
        Orchestre le processus de chargement complet.
        
        Étapes :
        1. Synchronisation des dimensions (Carburants, Stations, Dates).
        2. Insertion des faits (Prix).
        """
        if df.empty:
            return

        with self.engine.begin() as conn:
            self._sync_fuels(conn, df['fuel_name'].unique())
            self._sync_stations(conn, df)
            self._sync_dates(conn, df)
            
            self._insert_facts(conn, df)

    def _sync_fuels(self, conn, fuel_names):
        """
        Insère les nouveaux types de carburants dans dim_fuel si inexistants.
        """
        for fuel in fuel_names:
            if not fuel: continue
            
            sql = text("""
                INSERT INTO dim_fuel (fuel_code, fuel_name)
                VALUES (:fuel, :fuel)
                ON CONFLICT (fuel_code) DO NOTHING;
            """)
            conn.execute(sql, {"fuel": fuel})

    def _sync_stations(self, conn, df):
        """
        Met à jour ou insère les stations dans dim_station.
        En cas de conflit sur l'ID, met à jour l'adresse et les coordonnées pour garantir la fraîcheur des données.
        """
        stations = df[['api_station_id', 'address', 'city', 'postal_code', 'latitude', 'longitude']].drop_duplicates('api_station_id')
        
        for _, row in stations.iterrows():
            sql = text("""
                INSERT INTO dim_station (api_station_id, address, city, postal_code, latitude, longitude)
                VALUES (:id, :addr, :city, :cp, :lat, :lon)
                ON CONFLICT (api_station_id) 
                DO UPDATE SET 
                    address = EXCLUDED.address,
                    city = EXCLUDED.city,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude;
            """)
            conn.execute(sql, {
                "id": row['api_station_id'],
                "addr": row['address'],
                "city": row['city'],
                "cp": row['postal_code'],
                "lat": row['latitude'],
                "lon": row['longitude']
            })

    def _sync_dates(self, conn, df):
        """
        Alimente la dimension temps dim_date avec les nouvelles dates rencontrées.
        """
        unique_dates = df['update_time'].dt.date.unique()
        
        for d in unique_dates:
            date_id = int(d.strftime('%Y%m%d'))
            sql = text("""
                INSERT INTO dim_date (date_id, full_date, year, month, day_of_week)
                VALUES (:did, :fdate, :y, :m, :dow)
                ON CONFLICT (date_id) DO NOTHING;
            """)
            conn.execute(sql, {
                "did": date_id,
                "fdate": d,
                "y": d.year,
                "m": d.month,
                "dow": d.weekday()
            })

    def _insert_facts(self, conn, df):
        """
        Insère les relevés de prix dans la table de faits fact_fuel_price.
        Utilise une jointure SQL pour retrouver les IDs techniques des dimensions (station_id, fuel_id).
        Ignore les doublons basés sur la contrainte unique (station, carburant, date_maj).
        """
        for _, row in df.iterrows():
            sql = text("""
                INSERT INTO fact_fuel_price (station_id, fuel_id, date_id, price_value, update_time)
                SELECT 
                    s.station_id,
                    f.fuel_id,
                    :date_id,
                    :price,
                    :update_time
                FROM dim_station s, dim_fuel f
                WHERE s.api_station_id = :api_id 
                  AND f.fuel_code = :fuel_name
                ON CONFLICT (station_id, fuel_id, update_time) DO NOTHING;
            """)
            
            conn.execute(sql, {
                "date_id": row['date_id'],
                "price": row['price_value'],
                "update_time": row['update_time'],
                "api_id": row['api_station_id'],
                "fuel_name": row['fuel_name']
            })