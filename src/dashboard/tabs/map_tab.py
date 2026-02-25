import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from ..queries import get_departments_list, get_stations_with_latest_price

def render_map_tab(engine):
    st.header("Carte des Prix en Temps Réel")

    c1, c2, c3 = st.columns([1, 1, 2])
    
    with c1:
        all_depts = get_departments_list(engine)
        default_idx = all_depts.index("35") if "35" in all_depts else 0
        target_dept = st.selectbox("Département (Obligatoire)", all_depts, index=default_idx)

    with c2:
        fuel_options = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
        target_fuel = st.selectbox("Carburant", fuel_options)
        
    with c3:
        city_search = st.text_input("Filtrer par Ville (Optionnel)", placeholder="Ex: Rennes")

    with st.spinner("Localisation des stations..."):
        df_stations = get_stations_with_latest_price(engine, target_dept, target_fuel, city_search)

    if df_stations.empty:
        st.warning("Aucune station trouvée avec ces critères (ou pas de prix récent < 30 jours).")
        return

    avg_price = df_stations['price_value'].mean()
    
    st.info(f"📍 {len(df_stations)} stations trouvées. Prix moyen local : **{avg_price:.3f} €/L**")

    center_lat = df_stations['latitude'].mean()
    center_lon = df_stations['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_stations.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            continue

        price = row['price_value']
        if price < avg_price - 0.05:
            color = "green"
        elif price > avg_price + 0.05:
            color = "red"
        else:
            color = "orange"

        popup_html = f"""
        <b>{row['city']}</b><br>
        {row['address']}<br>
        <hr>
        <b>{target_fuel}: {price:.3f} €</b><br>
        <small>Mis à jour: {row['update_time']}</small>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{price:.3f} €",
            icon=folium.Icon(color=color, icon="gas-pump", prefix="fa")
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=800, returned_objects=[])