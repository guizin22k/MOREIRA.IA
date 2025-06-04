
import streamlit as st
import openai
import os

st.set_page_config(page_title="Minha IA", layout="centered")
st.title("🤖 Sua IA Pessoal")

openai.api_key = os.getenv("OPENAI_API_KEY")

user_input = st.text_input("Digite sua pergunta:")

if user_input:
    with st.spinner("A IA está pensando..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}]
            )
            st.success("Resposta:")
            st.write(response["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"Erro: {str(e)}")
