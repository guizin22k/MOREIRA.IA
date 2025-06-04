import streamlit as st
from openai import OpenAI
from serpapi import GoogleSearch

# Layout e estilo
st.set_page_config(page_title="MOREIRAGPT", layout="centered")
st.markdown("<h1 style='text-align: center; color: #0066cc;'>🤖 MOREIRAGPT</h1>", unsafe_allow_html=True)

# Inicializar sessões
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configurar cliente OpenAI
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Função para buscar na web com SerpAPI
def buscar_web(pergunta):
    search = GoogleSearch({
        "q": pergunta + " placar cruzeiro",
        "api_key": st.secrets["serpapi_key"]
    })
    resultados = search.get_dict()
    snippet = ""
    if "organic_results" in resultados:
        for item in resultados["organic_results"]:
            if "snippet" in item:
                snippet += item["snippet"] + " "
    return snippet.strip()

# Interface do chat
st.markdown("### Pergunte qualquer coisa ao MOREIRAGPT:")

pergunta = st.text_input("Sua pergunta:", placeholder="Ex: Quanto ficou o último jogo do Cruzeiro?")

if st.button("Enviar"):
    if pergunta:
        resultado_web = buscar_web(pergunta)

        st.session_state.messages.append({
            "role": "user",
            "content": (
                f"Abaixo está uma pergunta de um usuário e um trecho da web relacionado.\n"
                f"Use o conteúdo da web para gerar a MELHOR RESPOSTA possível.\n"
                f"Se os dados forem vagos, especule com base em contexto, mas não diga que não sabe.\n\n"
                f"Pergunta: {pergunta}\n"
                f"Resultado da Web: {resultado_web}"
            )
        })

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state["messages"]
        )

        resposta_texto = resposta.choices[0].message.content
        st.session_state.messages.append({
            "role": "assistant",
            "content": resposta_texto
        })

# Exibir conversa
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**Você:** {msg['content'].split('Pergunta: ')[-1].split('Resultado da Web')[0].strip()}")
    elif msg["role"] == "assistant":
        st.markdown(f"**MOREIRAGPT:** {msg['content']}")
