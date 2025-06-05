import streamlit as st
from system_prompt import SYSTEM_PROMPT
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import openai
import os
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="MOREIRAGPT 2026", page_icon="🤖", layout="centered")

# CSS customizado para balões e cores
st.markdown(
    """
    <style>
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
        font-size: 16px;
        line-height: 1.4;
        white-space: pre-wrap;
    }
    .user-message {
        background-color: #DCF8C6;
        text-align: right;
        margin-left: auto;
    }
    .bot-message {
        background-color: #F1F0F0;
        text-align: left;
        margin-right: auto;
    }
    .scrollable-chat {
        height: 500px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #fff;
    }
    .loading {
        font-style: italic;
        color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

st.title("🤖 MOREIRAGPT 2026")

def search_web(query: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return "\n\n".join([r["body"] for r in results])

def chat_with_gpt(messages: list) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.6,
    )
    return response["choices"][0]["message"]["content"]

def render_message(role: str, content: str):
    css_class = "user-message" if role == "user" else "bot-message"
    label = "Você" if role == "user" else "MoreiraGPT"
    st.markdown(
        f'<div class="chat-message {css_class}"><b>{label}:</b><br>{content}</div>',
        unsafe_allow_html=True,
    )

# Área do chat com scroll
chat_container = st.container()

# Entrada do usuário com multiline e botões
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_area(
        "Digite sua mensagem ou comando (use /web para pesquisa na web):",
        placeholder="Escreva aqui e pressione Enviar...",
        height=100,
        max_chars=1000,
    )
    submitted = st.form_submit_button("Enviar")

if submitted and user_input.strip():
    if user_input.startswith("/web"):
        termo = user_input[4:].strip()
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Buscando na web..."):
            resultados = search_web(termo)
        st.session_state.messages.append(
            {
                "role": "system",
                "content": f"Resultados da busca para '{termo}':\n{resultados}",
            }
        )
    elif user_input.strip() == "/limpar":
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.experimental_rerun()
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("MoreiraGPT está pensando..."):
        resposta = chat_with_gpt(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

with chat_container:
    st.markdown('<div class="scrollable-chat">', unsafe_allow_html=True)
    for msg in st.session_state.messages[1:]:
        render_message(msg["role"], msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

# Botão para limpar histórico no rodapé
if st.button("🧹 Limpar histórico"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.experimental_rerun()
