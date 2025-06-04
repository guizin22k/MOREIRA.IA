import streamlit as st
from openai import OpenAI
import requests

# Inicializa o cliente OpenAI com a chave segura do secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.title("MOREIRA.IA - Chat com busca web")

def busca_wikipedia(consulta):
    url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{consulta}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        return dados.get("extract", "Sem resumo encontrado.")
    else:
        return "Não consegui encontrar nada no Wikipedia."

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "Você é um assistente útil que responde perguntas de forma clara e objetiva."}]

user_input = st.text_input("Você:", key="input")

if user_input:
    termo_busca = user_input.split("?")[0].strip().replace(" ", "_")
    resumo = busca_wikipedia(termo_busca)

    contexto = f"Aqui está um resumo do Wikipedia sobre '{termo_busca}': {resumo}"

    st.session_state["messages"][0]["content"] = (
        "Você é um assistente útil que responde perguntas de forma clara e objetiva.\n"
        + contexto
    )

    st.session_state["messages"].append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state["messages"],
        max_tokens=300,
        temperature=0.7,
    )

    answer = response.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**IA:** {msg['content']}")
