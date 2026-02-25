import streamlit as st
import pandas as pd
import plotly.express as px
from ..queries import get_departments_list, get_price_trends, get_dept_comparison

def render_prices_tab(engine):
    st.header("Analyse Détaillée des Prix")

    with st.expander("Filtres de Recherche", expanded=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            years = st.slider("Période", 2015, 2026, (2022, 2025), key="price_years")
            start_year, end_year = years
        
        with c2:
            all_depts = get_departments_list(engine)
            selected_depts = st.multiselect(
                "Départements (Laisser vide = France entière)", 
                all_depts, 
                default=[],
                key="price_depts"
            )

        with c3:
            fuel_options = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
            selected_fuels = st.multiselect(
                "Carburants", 
                fuel_options, 
                default=["Gazole", "SP95"],
                key="price_fuels"
            )

    st.markdown("---")

    st.subheader(f"Évolution Mensuelle ({start_year}-{end_year})")
    
    if not selected_fuels:
        st.warning("Veuillez sélectionner au moins un carburant.")
    else:
        df_trends = get_price_trends(engine, start_year, end_year, selected_depts, selected_fuels)
        
        if not df_trends.empty:
            df_trends['date'] = pd.to_datetime(df_trends[['year', 'month']].assign(day=1))
            
            fig_line = px.line(
                df_trends,
                x="date",
                y="weighted_price",
                color="fuel_name",
                title="Prix Moyen Mensuel (€/L)",
                labels={"weighted_price": "Prix (€)", "date": "Date"},
                markers=True
            )
            fig_line.update_traces(hovertemplate='%{y:.3f} €/L')
            st.plotly_chart(fig_line, width='stretch')

            csv = df_trends.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Télécharger ces données (CSV)",
                csv,
                "evolution_prix.csv",
                "text/csv"
            )
        else:
            st.info("Aucune donnée trouvée pour cette période/sélection.")

    st.markdown("---")

    st.subheader("Comparatif Géographique (Moyenne Annuelle)")
    
    col_comp1, col_comp2 = st.columns([1, 3])
    
    with col_comp1:
        target_year = st.selectbox("Année de référence", range(2015, 2026), index=10, key="comp_year")
        target_fuel = st.selectbox("Carburant à comparer", fuel_options, index=0, key="comp_fuel")

    with col_comp2:
        df_comp = get_dept_comparison(engine, target_year, target_fuel)
        
        if not df_comp.empty:
            
            fig_bar = px.bar(
                df_comp,
                x="dept_code",
                y="annual_avg_price",
                color="annual_avg_price",
                color_continuous_scale="RdYlGn_r",
                title=f"Classement des départements : {target_fuel} en {target_year}",
                labels={"annual_avg_price": "Prix Moyen (€)", "dept_code": "Département"}
            )
            min_price = df_comp['annual_avg_price'].min() * 0.95
            fig_bar.update_layout(yaxis_range=[min_price, df_comp['annual_avg_price'].max() * 1.02])
            
            st.plotly_chart(fig_bar, width='stretch')
        else:
            st.warning(f"Pas de données pour {target_fuel} en {target_year}.")