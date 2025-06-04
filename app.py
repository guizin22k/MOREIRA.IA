import streamlit as st
import replicate
from PIL import Image
import io

st.set_page_config(page_title="MOREIRA.IA - Gerador de Imagens", page_icon="🎨", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #007FFF;'>🎨 MOREIRA.IA</h1>
    <p style='text-align: center;'>Gere imagens incríveis com base em uma imagem enviada + seu comando em texto.</p>
""", unsafe_allow_html=True)

# Inserir sua chave de API do Replicate (use variável de ambiente na versão final)
REPLICATE_API_TOKEN = "sua_chave_aqui"
replicate.Client(api_token=REPLICATE_API_TOKEN)

uploaded_image = st.file_uploader("📷 Envie uma imagem base (jpg ou png)", type=["jpg", "jpeg", "png"])
prompt = st.text_input("✍️ O que deseja adicionar ou modificar na imagem?")
generate = st.button("🚀 Gerar imagem com IA")

if uploaded_image and prompt and generate:
    image = Image.open(uploaded_image).convert("RGB")
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    with st.spinner("🧠 Gerando imagem com IA..."):
        output_url = replicate.run(
            "stability-ai/stable-diffusion-img2img",
            input={
                "image": img_bytes,
                "prompt": prompt,
                "strength": 0.6,
                "num_inference_steps": 50,
                "guidance_scale": 7.5
            }
        )

    st.image(output_url, caption="🖼️ Imagem gerada pela IA")

