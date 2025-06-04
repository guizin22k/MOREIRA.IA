import streamlit as st
from openai import OpenAI
import requests
import json

client = OpenAI(api_key=st.secrets["openai_api_key"])
SERPAPI_KEY = st.secrets["serpapi_key"]

st.title("MOREIRA.IA - Com busca na web (ao vivo)")

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
            return "Não encontrei uma resposta direta na web."
    else:
        return "Erro ao buscar na internet."

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "Você é uma IA que responde perguntas com ajuda da internet."}]

user_input = st.text_input("Pergunte algo:")

if user_input:
    resultado_web = buscar_web(user_input)
    contexto = f"Resultado da web: {resultado_web}"

    st.session_state["messages"].append({"role": "user", "content": f"{user_input}\n\n{contexto}"})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state["messages"],
        max_tokens=300,
        temperature=0.7,
    )

    resposta = response.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": resposta})

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**IA:** {msg['content']}")
