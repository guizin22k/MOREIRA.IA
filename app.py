import streamlit as st
from PIL import Image
import io
import replicate
import os

# Configurações básicas
st.set_page_config(page_title="MOREIRA.IA - Gerador de Imagens", layout="centered")

# Título
st.markdown("""
    <h1 style='text-align: center; color: #007FFF; font-weight: bold;'>🎨 MOREIRA.IA</h1>
    <p style='text-align: center; color: #007FFF;'>Envie uma imagem, descreva o que quer modificar e gere uma nova imagem com IA</p>
""", unsafe_allow_html=True)

# Função para estilizar o botão "+" para upload (usando HTML + CSS)
st.markdown("""
    <style>
    div.stUpload {
        text-align: center;
        font-size: 72px;
        font-weight: bold;
        color: #007FFF;
        cursor: pointer;
        border: 3px dashed #007FFF;
        border-radius: 12px;
        padding: 40px;
        margin: 20px auto;
        max-width: 320px;
    }
    </style>
""", unsafe_allow_html=True)

# Aqui criamos um widget normal, mas o style acima deixa ele "grande e com borda +"
uploaded_file = st.file_uploader("➕", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

prompt = st.text_input("✍️ O que deseja modificar ou adicionar na imagem?")

if uploaded_file and prompt:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem original enviada", use_column_width=True)

    with st.spinner("🧠 Gerando nova imagem com IA..."):
        # Pega chave do secrets (variável ambiente)
        REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
        client = replicate.Client(api_token=REPLICATE_API_TOKEN)

        # Converte imagem para bytes para enviar
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Executa modelo img2img no replicate
        output_urls = client.run(
            "stability-ai/stable-diffusion-img2img",
            input={
