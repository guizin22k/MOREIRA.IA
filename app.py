import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Cria cliente oficial OpenAI novo
client = OpenAI(api_key=openai_api_key)

st.set_page_config(page_title="🤖 MOREIRAGPT", page_icon="🤖", layout="centered")

SYSTEM_PROMPT = """
Você é o MOREIRAGPT, uma IA super inteligente, educada e útil, pronta para ajudar com tudo que o usuário precisar.
Seja claro, objetivo e amigável.
"""

# Inicializa histórico de conversa
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Busca na web via DuckDuckGo (cache de 10 min)
@st.cache_data(ttl=600)
def search_web(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return "\n\n".join([r["body"] for r in results])

# Função que chama a OpenAI API moderna
def chat_with_gpt(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.6,
        max_tokens=1000,
    )
    return response.choices[0].message.content

st.title("🤖 MOREIRAGPT - IA do Moreira")

user_input = st.text_input("Digite sua mensagem ou comando:")

if user_input:
    if user_input.strip() == "/limpar":
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.success("Histórico apagado com sucesso!")
        st.experimental_rerun()
    else:
        if user_input.startswith("/web "):
            termo = user_input[5:].strip()
            st.info(f"Buscando na web por: {termo}")
            resultados = search_web(termo)
            user_input += f"\n\nINFORMAÇÕES ENCONTRADAS NA WEB:\n{resultados}"

        # Adiciona mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Gera resposta do GPT
        with st.spinner("Pensando..."):
            resposta = chat_with_gpt(st.session_state.messages)

        # Salva resposta
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# Exibe a conversa
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**Você:** {msg['content']}")
    else:
        st.markdown(f"**MoreiraGPT:** {msg['content']}")

st.markdown("---")
st.markdown("Comandos:\n- `/web <termo>` para busca na web\n- `/limpar` para apagar o histórico")
