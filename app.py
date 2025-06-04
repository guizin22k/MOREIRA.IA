import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
import os

st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #e6f0ff;
    }
    .stApp {
        background-color: #e6f0ff;
    }
    .title {
        font-size: 48px;
        color: #004aad;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">MOREIRAGPT</div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("Configurações")
    openai_api_key = st.text_input("Chave da API OpenAI", type="password")
    if not openai_api_key:
        st.warning("Insira sua chave da OpenAI para continuar.")
        st.stop()

client = OpenAI(api_key=openai_api_key)

def buscar_na_web(query):
    with DDGS() as ddgs:
        resultados = ddgs.text(query, max_results=3)
        texto_resultado = "\n\n".join([r["body"] for r in resultados if "body" in r])
        return texto_resultado or "Nenhum resultado encontrado na web."

def responder_ia(pergunta, contexto_web):
    prompt = f"""
Você é o MOREIRAGPT, uma IA com acesso à internet.

Usuário perguntou: "{pergunta}"

Responda com base nas informações abaixo da web:

{contexto_web}

Responda de forma clara e direta:
"""
    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content

pergunta = st.text_input("Você:", placeholder="Pergunte algo para o MOREIRAGPT")

if pergunta:
    with st.spinner("Buscando na web e gerando resposta..."):
        contexto = buscar_na_web(pergunta)
        resposta = responder_ia(pergunta, contexto)
        st.markdown("### MOREIRAGPT:")
        st.write(resposta)
