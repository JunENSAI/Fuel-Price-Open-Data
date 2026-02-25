import streamlit as st
import plotly.express as px
from ..queries import get_departments_list, get_kpis, get_price_evolution_data, get_volume_data

def render_stats_tab(engine):
    st.header("Statistiques Générales")

    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        years = st.slider("Période d'analyse", 2015, 2026, (2020, 2025))
    
    with col_filter2:
        all_depts = get_departments_list(engine)
        selected_depts = st.multiselect("Filtrer par Département", all_depts, default=[])

    start_year, end_year = years

    kpi_df = get_kpis(engine, start_year, end_year, selected_depts)
    
    if not kpi_df.empty:
        total_stations = kpi_df['total_stations'].iloc[0]
        total_releves = kpi_df['total_price_points'].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Stations Actives (Est.)", f"{total_stations:,.0f}")
        c2.metric("Relevés de prix analysés", f"{total_releves:,.0f}")
        c3.metric("Années couvertes", f"{end_year - start_year + 1} ans")

    st.markdown("---")

    col_graph1, col_graph2 = st.columns([2, 1])

    with col_graph1:
        st.subheader(" Évolution du Prix Moyen")
        df_evol = get_price_evolution_data(engine, start_year, end_year, selected_depts)
        
        if not df_evol.empty:
            fig_evol = px.line(
                df_evol, 
                x="year", 
                y="mean_price", 
                color="fuel_name",
                markers=True,
                title="Prix moyen annuel par carburant (€/L)",
                labels={"mean_price": "Prix (€)", "year": "Année", "fuel_name": "Carburant"}
            )
            st.plotly_chart(fig_evol, width='stretch')
        else:
            st.warning("Pas de données pour cette sélection.")

    with col_graph2:
        st.subheader("Distribution des Carburants")
        df_vol = get_volume_data(engine)
        
        if not df_vol.empty:
            fig_pie = px.pie(
                df_vol, 
                values='total_volume', 
                names='fuel_name', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig_pie, width='stretch')