import streamlit as st
import duckduckgo_search
from duckduckgo_search import DDGS

st.set_page_config(page_title="MOREIRA.IA", page_icon="🤖", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #007FFF;'>🤖 MOREIRA.IA</h1>
    <p style='text-align: center;'>Sua inteligência artificial pessoal com respostas baseadas na web.</p>
""", unsafe_allow_html=True)

query = st.text_input("Digite sua pergunta ou comando", "")

def buscar_na_web(pergunta):
    with DDGS() as ddgs:
        resultados = ddgs.text(pergunta, max_results=5)
        resposta = ""
        for r in resultados:
            resposta += f"- [{r['title']}]({r['href']}): {r['body']}\n"
        return resposta if resposta else "❌ Nenhum resultado encontrado."

if st.button("🔍 Pesquisar"):
    if query:
        if query.startswith("/marketing"):
            st.info("📢 Estratégia de marketing em breve aqui!")
        else:
            st.markdown("🔎 Buscando na web...")
            resultado = buscar_na_web(query)
            st.markdown(resultado)
    else:
        st.warning("Digite algo para buscar.")
