import pandas as pd
from .database import load_data

def get_departments_list(engine):
    """Récupère la liste unique des codes départements présents en base."""
    sql = "SELECT DISTINCT dept_code FROM dim_station ORDER BY dept_code;"
    df = load_data(sql, engine)
    return df['dept_code'].tolist()

def get_kpis(engine, start_year, end_year, depts):
    """
    Récupère les chiffres clés filtrés.
    """
    
    mv_dept_filter = ""
    station_dept_filter = ""
    
    if depts:
        dept_list_str = "', '".join(depts)
        mv_dept_filter = f"AND dept_code IN ('{dept_list_str}')"
        station_dept_filter = f"AND dept_code IN ('{dept_list_str}')"

    sql_prices = f"""
        SELECT SUM(price_count) as total_price_points
        FROM mv_monthly_avg_price
        WHERE year BETWEEN {start_year} AND {end_year}
        {mv_dept_filter}
    """
    
    sql_stations = f"""
        SELECT COUNT(api_station_id) as total_stations
        FROM dim_station
        WHERE 1=1
        {station_dept_filter}
    """

    df_prices = load_data(sql_prices, engine)
    df_stations = load_data(sql_stations, engine)
    
    total_prices = df_prices['total_price_points'].iloc[0] if not df_prices.empty else 0
    total_stations = df_stations['total_stations'].iloc[0] if not df_stations.empty else 0

    return pd.DataFrame({
        'total_stations': [total_stations],
        'total_price_points': [total_prices]
    })

def get_price_evolution_data(engine, start_year, end_year, depts):
    """
    Récupère l'évolution du prix moyen par an et par carburant.
    """
    dept_filter = ""
    if depts:
        dept_list_str = "', '".join(depts)
        dept_filter = f"AND dept_code IN ('{dept_list_str}')"

    sql = f"""
        SELECT 
            year, 
            fuel_name, 
            AVG(avg_price) as mean_price
        FROM mv_monthly_avg_price
        WHERE year BETWEEN {start_year} AND {end_year}
        {dept_filter}
        GROUP BY year, fuel_name
        ORDER BY year, fuel_name
    """
    return load_data(sql, engine)

def get_volume_data(engine):
    """Récupère le volume de relevés par carburant (Pie Chart)."""
    sql = """
        SELECT fuel_name, SUM(price_count) as total_volume
        FROM mv_monthly_avg_price
        GROUP BY fuel_name
        ORDER BY total_volume DESC
    """
    return load_data(sql, engine)