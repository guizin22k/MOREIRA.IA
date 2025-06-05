
import streamlit as st
from system_prompt import SYSTEM_PROMPT
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

st.title("🤖 MOREIRAGPT - IA do Moreira")

def search_web(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return "\n\n".join([r["body"] for r in results])

def chat_with_gpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.6,
    )
    return response["choices"][0]["message"]["content"]

user_input = st.text_input("Digite sua mensagem ou comando:")

if user_input:
    if user_input.startswith("/web"):
        termo = user_input[5:]
        resultados = search_web(termo)
        user_input += f"\n\nINFORMAÇÕES ENCONTRADAS NA WEB:\n{resultados}"
    elif user_input == "/limpar":
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.success("Histórico apagado.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Pensando..."):
        resposta = chat_with_gpt(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": resposta})

for m in st.session_state.messages[1:]:
    st.markdown(f"**{m['role'].upper()}**: {m['content']}")
