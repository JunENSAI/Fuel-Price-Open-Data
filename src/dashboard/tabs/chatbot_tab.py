import streamlit as st
from ..ai_client import FuelAIClient

def render_chatbot_tab(engine):
    st.header("🤖 Assistant IA (Text-to-SQL)")
    st.markdown("Posez des questions en langage naturel sur la base de données.")
    st.info("Exemples : *'Quel est le prix moyen du Gazole en 2023 ?'*")

    ai_client = FuelAIClient(engine)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "data" in message:
                st.dataframe(message["data"])
            if "sql" in message:
                with st.expander("Voir la requête SQL générée"):
                    st.code(message["sql"], language="sql")

    if prompt := st.chat_input("Votre question sur les carburants..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ *Réflexion et génération du SQL...*")

            sql_query = ai_client.generate_sql(prompt)
            
            message_placeholder.markdown("⚡ *Interrogation de la base de données...*")
            df_result, error = ai_client.execute_query(sql_query)

            if error:
                st.error(f"Oups, je n'ai pas réussi : {error}")
                st.code(sql_query, language="sql")
                response_text = "Je n'ai pas pu exécuter la requête."
            else:
                message_placeholder.markdown("📝 *Analyse des résultats...*")
                response_text = ai_client.summarize_results(prompt, df_result)
                
                message_placeholder.markdown(response_text)
                st.dataframe(df_result)
                with st.expander("Voir la requête SQL technique"):
                    st.code(sql_query, language="sql")

        assistant_msg = {
            "role": "assistant", 
            "content": response_text, 
            "sql": sql_query
        }
        if df_result is not None and not df_result.empty:
            assistant_msg["data"] = df_result
            
        st.session_state.messages.append(assistant_msg)