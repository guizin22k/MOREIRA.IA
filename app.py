import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Configurações da interface
st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="centered")

# Estilo simples azul
st.markdown(
    """
    <style>
    body { background-color: #007BFF; color: white; }
    .stApp { background-color: #007BFF; }
    .css-1v3fvcr { color: white; }
    .css-2trqyj { color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("MOREIRAGPT")

# Sua chave da OpenAI no secrets.toml
openai.api_key = st.secrets["openai_api_key"]

def busca_google(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    params = {
        "q": query,
        "hl": "pt"
    }
    url = "https://www.google.com/search"
    res = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(res.text, "html.parser")

    snippets = []
    for g in soup.find_all('div', class_='tF2Cxc')[:5]:
        snippet = g.find('div', class_='IsZvec')
        if snippet:
            text = snippet.get_text(separator=' ', strip=True)
            snippets.append(text)
    return "\n".join(snippets)

def gerar_resposta(pergunta, contexto):
    prompt = (
        f"Você é MOREIRAGPT, um assistente que responde apenas com base no texto abaixo, "
        f"sem inventar nada:\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pergunta: {pergunta}\n"
        f"Resposta clara e objetiva:"
    )
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.3,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

query = st.text_input("Faça sua pergunta para MOREIRAGPT:")

if query:
    with st.spinner("Buscando na web e gerando resposta..."):
        contexto = busca_google(query)
        if not contexto:
            st.write("Não encontrei resultados relevantes na web.")
        else:
            resposta = gerar_resposta(query, contexto)
            st.write("### Resultado da web:")
            st.write(contexto)
            st.write("### Resposta MOREIRAGPT:")
            st.write(resposta)
