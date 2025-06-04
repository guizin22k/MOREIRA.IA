import streamlit as st
from openai import OpenAI
import requests

# Configurações da página
st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖")

# Estilo personalizado (azul)
st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
        }
        .main {
            background-color: #e6f0ff;
            padding: 2rem;
            border-radius: 10px;
        }
        h1 {
            color: #0056b3;
            text-align: center;
        }
        .stTextInput>div>div>input {
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("🤖 MOREIRAGPT - Sua IA com acesso à Web")

# Chaves secretas
client = OpenAI(api_key=st.secrets["openai_api_key"])
SERPAPI_KEY = st.secrets["serpapi_key"]

# Função para buscar dados na web
def buscar_web(query):
    url = f"https://serpapi.com/search.json?q={query}&hl=pt-br&gl=br&api_key={SERPAPI_KEY}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        if "answer_box" in dados:
            box = dados["answer_box"]
            if "answer" in box:
                return box["answer"]
            if "snippet" in box:
                return box["snippet"]
            if "highlighted_words" in box:
                return ", ".join(box["highlighted_words"])
        if "organic_results" in dados and len(dados["organic_results"]) > 0:
            return dados["organic_results"][0].get("snippet", "Sem resposta clara.")
        return "Nenhum dado relevante encontrado."
    else:
        return "Erro ao buscar na internet."

# Mensagem de sistema (primeira interação)
if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "system",
        "content": "Você é uma IA brasileira chamada MOREIRAGPT. Sempre responda com base nas informações encontradas na internet. Seja direto e claro."
    }]

# Entrada do usuário
pergunta = st.text_input("Pergunte algo para a MOREIRAGPT 👇")

if pergunta:
    resultado_web = buscar_web(pergunta)

    st.session_state["messages"].append({
        "role": "user",
        "content": (
            f"Responda à pergunta abaixo usando SOMENTE o conteúdo obtido da web.\n\n"
            f"PERGUNTA: {pergunta}\n"
            f"RESULTADO DA WEB: {resultado_web}\n\n"
            f"Se o resultado for vago, diga isso. Mas NUNCA diga que não consegue responder."
        )
    })

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state["messages"],
        temperature=0.7,
        max_tokens=500
    )

    conteudo_ia = resposta.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": conteudo_ia})

    # Mostrar o histórico da conversa
    for msg in st.session_state["messages"][1:]:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content'].splitlines()[0]}")
        elif msg["role"] == "assistant":
            st.markdown(f"**MOREIRAGPT:** {msg['content']}")
