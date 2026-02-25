import streamlit as st
from src.dashboard.database import get_db_engine
from src.dashboard.tabs.stats_tab import render_stats_tab

st.set_page_config(
    page_title="Fuel Price Dashboard",
    page_icon="⛽",
    layout="wide"
)

def main():
    st.title("Observatoire des Carburants en France")
    
    try:
        engine = get_db_engine()
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "Statistiques Globales", 
        "Analyse des Prix", 
        "Carte Interactive", 
        "Assistant IA"
    ])

    with tab1:
        render_stats_tab(engine)
    
    with tab2:
        st.info("Module 'Prix' en construction...")
        
    with tab3:
        st.info("Module 'Carte' en construction...")

    with tab4:
        st.info("Module 'Chatbot' en construction...")

if __name__ == "__main__":
    main()