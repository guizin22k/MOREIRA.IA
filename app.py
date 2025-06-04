import streamlit as st
from PIL import Image
import io
import replicate
import os

st.set_page_config(page_title="MOREIRA.IA - Gerador de Imagens", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #007FFF; font-weight: bold;'>🎨 MOREIRA.IA</h1>
    <p style='text-align: center; color: #007FFF;'>Envie uma imagem, descreva o que quer modificar e gere uma nova imagem com IA</p>
""", unsafe_allow_html=True)

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

uploaded_file = st.file_uploader("➕", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

prompt = st.text_input("✍️ O que deseja modificar ou adicionar na imagem?")

if uploaded_file and prompt:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem original enviada", use_column_width=True)

    with st.spinner("🧠 Gerando nova imagem com IA..."):
        REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
        if not REPLICATE_API_TOKEN:
            st.error("❗️ Chave da API Replicate não encontrada. Adicione ela no Secrets do Streamlit ou na variável de ambiente.")
        else:
            client = replicate.Client(api_token=REPLICATE_API_TOKEN)

            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            output_urls = client.run(
                "stability-ai/stable-diffusion-img2img",
                input={
                    "image": img_bytes,
                    "prompt": prompt,
                    "strength": 0.6,
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            )

            st.image(output_urls, caption="🖼️ Imagem gerada pela IA", use_column_width=True)

elif not uploaded_file:
    st.info("Envie uma imagem usando o botão + acima para começar.")
elif not prompt:
    st.info("Digite o que deseja modificar ou adicionar na imagem.")
