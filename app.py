import streamlit as st
from openai import OpenAI
from serpapi import GoogleSearch

st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="centered")

# Interface customizada (azul)
st.markdown(
    """
    <style>
    .main > div {
        background-color: #1E90FF;  /* azul */
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTextInput > div > input {
        border-radius: 10px;
        border: 2px solid #1E90FF;
        padding: 0.5rem;
        font-size: 18px;
    }
    .css-1d391kg {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 MOREIRAGPT")

# Criar cliente OpenAI com a chave da streamlit secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Função para busca no Google via SerpAPI
def buscar_web(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": st.secrets["serpapi_key"],
        "num": 3,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    snippets = []
    if "organic_results" in results:
        for r in results["organic_results"][:3]:
            if "snippet" in r:
                snippets.append(r["snippet"])
    return "\n".join(snippets)

# Função que gera resposta usando OpenAI com base na busca web
def responder_pergunta(pergunta):
    conteudo_web = buscar_web(pergunta)
    if not conteudo_web:
        return "Desculpe, não consegui encontrar informações relevantes na web para sua pergunta."

    prompt = (
        "Você é um assistente inteligente chamado MOREIRAGPT.\n"
        "Responda a pergunta abaixo usando SOMENTE o conteúdo extraído da web, de forma clara e direta.\n\n"
        f"Conteúdo da web:\n{conteudo_web}\n\n"
        f"Pergunta: {pergunta}\n"
        "Resposta clara e objetiva:"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente útil e educado."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# Interface do app
pergunta = st.text_input("Faça sua pergunta para MOREIRAGPT e ele buscará na web:")

if pergunta:
    with st.spinner("Pesquisando na web e gerando resposta..."):
        resposta = responder_pergunta(pergunta)
    st.markdown(f"**Resposta:** {resposta}")
