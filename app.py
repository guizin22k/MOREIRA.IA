import streamlit as st
import os
import openai

st.set_page_config(page_title="MOREIRA.IA Chat Vendas", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #007FFF;'>💬 MOREIRA.IA - Chat Inteligente</h1>
    <p style='text-align: center;'>Use comandos como <code>/vendas</code>, <code>/marketing</code> ou apenas fale comigo!</p>
""", unsafe_allow_html=True)

# Entrada do usuário
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Digite sua mensagem ou comando...")

# Configurar OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Função para resposta da IA
def gerar_resposta(prompt):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=st.session_state.chat_history + [{"role": "user", "content": prompt}]
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"⚠️ Erro ao gerar resposta: {str(e)}"

# Processar entrada
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    if user_input.startswith("/vendas"):
        comando = user_input.replace("/vendas", "").strip()
        prompt = f"Crie uma copy de vendas para: {comando}" if comando else "Crie uma copy de vendas genérica para um produto digital."
    elif user_input.startswith("/marketing"):
        comando = user_input.replace("/marketing", "").strip()
        prompt = f"Me dê 3 ideias de vídeos virais sobre: {comando}" if comando else "Me dê 3 ideias de vídeos virais para vender um curso."
    elif user_input.startswith("/meta"):
        prompt = "Me motive com uma frase forte e direta sobre disciplina e foco."
    else:
        prompt = user_input

    resposta = gerar_resposta(prompt)
    st.session_state.chat_history.append({"role": "assistant", "content": resposta})

# Exibir chat
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "ai"):
        st.markdown(msg["content"])

st.markdown("""
    <hr>
    <p style='text-align: center; font-size: 12px;'>MOREIRA.IA - versão texto inteligente 🚀</p>
""", unsafe_allow_html=True)
