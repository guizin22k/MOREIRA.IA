import streamlit as st
from openai import OpenAI
import requests

# Chaves secretas salvas no Streamlit Cloud
client = OpenAI(api_key=st.secrets["openai_api_key"])
SERPAPI_KEY = st.secrets["serpapi_key"]

st.set_page_config(page_title="MOREIRA.IA", page_icon="🤖")
st.title("🤖 MOREIRA.IA - Inteligência com Busca na Web")

# Função que busca na internet via SerpAPI
def buscar_web(query):
    url = f"https://serpapi.com/search.json?q={query}&hl=pt-br&gl=br&api_key={SERPAPI_KEY}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        if "answer_box" in dados and "answer" in dados["answer_box"]:
            return dados["answer_box"]["answer"]
        elif "organic_results" in dados and len(dados["organic_results"]) > 0:
            return dados["organic_results"][0].get("snippet", "Sem resposta direta.")
        else:
            return "Nenhuma informação clara encontrada."
    else:
        return "Erro ao buscar na internet."

# Instruções do sistema
if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "system",
        "content": "Você é uma IA brasileira chamada MOREIRA.IA que responde com base na internet. Sempre use os dados da web para responder com clareza e objet
