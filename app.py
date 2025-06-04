import streamlit as st
from PIL import Image
import io
import os
import base64
import replicate

st.set_page_config(page_title="MOREIRA.IA - Gerador de Imagens", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #007FFF; font-weight: bold;'>🎨 MOREIRA.IA</h1>
    <p style='text-align: center; color: #007FFF;'>Envie uma imagem, descreva o que quer modificar e gere uma nova imagem com IA</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("➕ Envie sua imagem (jpg, png)", type=["jpg", "jpeg", "png"], label_visibility="visible")

default_prompt = ("Transforme esta imagem mantendo sua composição principal, mas adicione iluminação dramática "
                  "e realismo fotográfico, com cores vibrantes e um fundo artístico abstrato. "
                  "Faça a imagem parecer uma obra-prima digital hiper-realista, preservando detalhes nítidos "
                  "e uma atmosfera envolvente.")

prompt = st.text_area("Descreva a modificação desejada para a imagem:", height=100)

if st.button("Inserir prompt padrão"):
    st.session_state["prompt"] = default_prompt
    st.experimental_rerun()

if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

if prompt != st.session_state["prompt"]:
    st.session_state["prompt"] = prompt

if uploaded_file and st.session_state["prompt"].strip():
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem original enviada", use_column_width=True)

    with st.spinner("🧠 Gerando nova imagem com IA..."):
        REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
        if not REPLICATE_API_TOKEN:
            st.error("❗️ Chave da API Replicate não encontrada no Secrets ou variável de ambiente.")
        else:
            client = replicate.Client(api_token=REPLICATE_API_TOKEN)

            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_base64 = f"data:image/png;base64,{img_str}"

            try:
                output_urls = client.run(
                    "stability-ai/stable-diffusion-img2img",
                    input={
                        "image": img_base64,
                        "prompt": st.session_state["prompt"],
                        "strength": 0.6,
                        "num_inference_steps": 50,
                        "guidance_scale": 7.5
                    }
                )
                st.image(output_urls, caption="🖼️ Imagem gerada pela IA", use_column_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar imagem: {e}")

elif uploaded_file and not st.session_state["prompt"].strip():
    st.info("Por favor, digite o que deseja modificar na imagem.")
elif not uploaded_file:
    st.info("Envie uma imagem usando o botão acima para começar.")

