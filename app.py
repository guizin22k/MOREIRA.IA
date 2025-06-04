import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Setup da API OpenAI - pega da secrets do Streamlit
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="centered")

# CSS customizado para cor azul e interface igual a minha
st.markdown(
    """
    <style>
    /* Fundo azul escuro */
    .css-18e3th9 {
        background-color: #0d47a1;  /* azul escuro */
    }
    /* Container branco para chat */
    .css-1d391kg {
        background-color: white !important;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    /* Título */
    .css-1v3fvcr h1 {
        color: white;
        font-weight: 700;
    }
    /* Botão */
    button {
        background-color: #1976d2 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    /* Caixa de texto */
    textarea, input {
        border-radius: 6px !important;
        border: 1px solid #1976d2 !important;
        padding: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 MOREIRAGPT")

def busca_google(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    params = {"q": query, "hl": "pt"}
    url = "https://www.google.com/search"
    res = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(res.text, "html.parser")

    snippets = []
    for g in soup.find_all('div', class_='tF2Cxc')[:5]:
        snippet_div = g.find('div', class_='VwiC3b')
        if snippet_div:
            text = snippet_div.get_text(separator=' ', strip=True)
            snippets.append(text)
    return "\n".join(snippets) if snippets else "Não encontrei resultados relevantes na web."

def gera_resposta(pergunta):
    conteudo_web = busca_google(pergunta)
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

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("form", clear_on_submit=True):
    pergunta = st.text_input("Faça uma pergunta para MOREIRAGPT:")
    submit = st.form_submit_button("Enviar")

if submit and pergunta:
    with st.spinner("Pesquisando e gerando resposta..."):
        resposta = gera_resposta(pergunta)
        st.session_state.history.append((pergunta, resposta))

if st.session_state.history:
    for i, (perg, resp) in enumerate(reversed(st.session_state.history)):
        st.markdown(f"**Você:** {perg}")
        st.markdown(f"**MOREIRAGPT:** {resp}")
        if i != len(st.session_state.history) - 1:
            st.markdown("---")
