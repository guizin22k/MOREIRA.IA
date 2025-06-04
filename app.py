import streamlit as st
from openai import OpenAI
import requests

client = OpenAI(api_key=st.secrets["openai_api_key"])

def busca_duckduckgo(query):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
        "skip_disambig": 1,
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()
        abstract = data.get("AbstractText", "")
        related = data.get("RelatedTopics", [])
        snippets = [abstract] if abstract else []
        for topic in related:
            if isinstance(topic, dict) and "Text" in topic:
                snippets.append(topic["Text"])
        return "\n".join(snippets[:5]) if snippets else "Não encontrei resultados relevantes na web."
    else:
        return "Erro ao buscar na web."

def gera_resposta(pergunta):
    conteudo_web = busca_duckduckgo(pergunta)
    prompt = f"""
Você: Responda à pergunta abaixo usando SOMENTE o conteúdo obtido da web.

Conteúdo da web:
{conteudo_web}

Resposta precisa e clara:
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# Interface azul customizada no Streamlit

st.markdown(
    """
    <style>
    .css-18e3th9 {
        background-color: #001F7A;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stTextInput>div>div>input {
        background-color: #e0e7ff;
        color: #001F7A;
        border-radius: 0.25rem;
        padding: 0.5rem;
    }
    .css-1v0mbdj {
        color: #001F7A;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 MOREIRAGPT")

pergunta = st.text_input("Faça uma pergunta para MOREIRAGPT:")

if pergunta:
    with st.spinner("Pesquisando e gerando resposta..."):
        resposta = gera_resposta(pergunta)
        st.markdown(f"**Você:** {pergunta}")
        st.markdown(f"**MOREIRAGPT:** {resposta}")
