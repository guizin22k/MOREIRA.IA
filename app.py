import streamlit as st
from system_prompt import SYSTEM_PROMPT
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import openai
import os
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="🤖 MOREIRAGPT", page_icon="🤖", layout="centered")

# Inicializa memória de conversa
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Cache para resultados de busca
@st.cache_data(ttl=600)
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            textos = [r["body"] for r in results]
            return "\n\n".join(textos)
    except Exception as e:
        return f"Erro na busca: {e}"

# Função de chamada ao GPT
def chat_with_gpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.6,
        max_tokens=1000,
    )
    return response["choices"][0]["message"]["content"]

st.title("🤖 MOREIRAGPT - IA do Moreira")

user_input = st.text_input("Digite sua mensagem ou comando:")

if user_input:
    if user_input.strip() == "/limpar":
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.success("Histórico apagado com sucesso!")
        st.experimental_rerun()  # Recarrega app para resetar input
    else:
        if user_input.startswith("/web "):
            termo = user_input[5:].strip()
            st.info(f"Buscando na web por: {termo}")
            resultados = search_web(termo)
            # Acrescenta resultados encontrados à mensagem do usuário
            user_input += f"\n\nINFORMAÇÕES ENCONTRADAS NA WEB:\n{resultados}"

        # Adiciona input do usuário à memória
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Pensando..."):
            resposta = chat_with_gpt(st.session_state.messages)

        # Salva resposta na memória
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# Exibe o chat completo, mas omite sistema
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**Você:** {msg['content']}")
    else:
        st.markdown(f"**MoreiraGPT:** {msg['content']}")

st.markdown("---")
st.markdown("Comandos disponíveis:\n- `/web <termo>` para busca na web\n- `/limpar` para apagar o histórico")

