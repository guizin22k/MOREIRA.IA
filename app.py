import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
import os

# Título da página
st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="centered")
st.markdown("<h1 style='color:#1f77b4;text-align:center;'>MOREIRAGPT 💬</h1>", unsafe_allow_html=True)
st.markdown("### Sua assistente com respostas diretas da web!")

# Chave da API OpenAI
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Função de busca na web
def buscar_web_duckduckgo(pergunta):
    with DDGS() as ddgs:
        resultados = ddgs.text(pergunta, max_results=5)
        respostas = [r["body"] for r in resultados if "body" in r]
        return respostas

# Função que gera uma resposta clara com base na web
def gerar_resposta(pergunta):
    resultados = buscar_web_duckduckgo(pergunta)
    
    if not resultados:
        return "❌ Não encontrei nada relevante na web."

    contexto = "\n\n".join(resultados[:3])
    prompt = f"""Responda com clareza e estilo humano à pergunta abaixo, usando SOMENTE o conteúdo da web.
    
Pergunta: {pergunta}
Conteúdo da web:
{contexto}

Resposta:"""

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return resposta.choices[0].message.content.strip()

# Interface do usuário
pergunta = st.text_input("Você:", placeholder="Digite aqui sua pergunta...")

if pergunta:
    with st.spinner("Consultando a web..."):
        resposta = gerar_resposta(pergunta)
    st.markdown(f"**MOREIRAGPT:** {resposta}")
