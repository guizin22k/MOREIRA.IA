import streamlit as st
from PIL import Image
import io
import os
import base64
import replicate

st.set_page_config(page_title="MOREIRA.IA Chat Misto", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #007FFF; font-weight: bold;'>🤖 MOREIRA.IA Chat Misto</h1>
    <p style='text-align: center; color: #007FFF;'>Envie texto, imagem, ou ambos. Receba respostas e imagens geradas pela IA.</p>
""", unsafe_allow_html=True)

# Input do usuário
user_text = st.text_area("Digite sua mensagem ou prompt para a IA:", height=100)
uploaded_file = st.file_uploader("➕ Envie uma imagem (opcional)", type=["jpg", "jpeg", "png"])

# Padrão prompt para img2img
default_prompt = ("Transforme esta imagem mantendo sua composição principal, mas adicione iluminação dramática "
                  "e realismo fotográfico, com cores vibrantes e um fundo artístico abstrato. "
                  "Faça a imagem parecer uma obra-prima digital hiper-realista, preservando detalhes nítidos "
                  "e uma atmosfera envolvente.")

if st.button("Inserir prompt padrão"):
    user_text = default_prompt
    st.experimental_rerun()

def gerar_imagem(img: Image.Image, prompt: str):
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    if not REPLICATE_API_TOKEN:
        st.error("❗️ Chave da API Replicate não encontrada.")
        return None

    client = replicate.Client(api_token=REPLICATE_API_TOKEN)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    img_base64 = f"data:image/png;base64,{img_str}"

    try:
        output_urls = client.run(
            "stability-ai/stable-diffusion-img2img:latest",
            input={
                "image": img_base64,
                "prompt": prompt if prompt.strip() else default_prompt,
                "strength": 0.6,
                "num_inference_steps": 50,
                "guidance_scale": 7.5
            }
        )
        return output_urls
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {e}")
        return None

# Fluxo de resposta
if st.button("Enviar"):
    if uploaded_file and user_text.strip():
        # Usuário enviou imagem + texto
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Imagem original", use_column_width=True)
        st.write(f"Prompt enviado: {user_text}")

        result = gerar_imagem(image, user_text)
        if result:
            st.image(result, caption="Imagem gerada pela IA", use_column_width=True)

    elif uploaded_file and not user_text.strip():
        # Só imagem enviada, usar prompt padrão
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Imagem original", use_column_width=True)
        st.write("Usando prompt padrão para modificar a imagem.")
        result = gerar_imagem(image, default_prompt)
        if result:
            st.image(result, caption="Imagem gerada pela IA", use_column_width=True)

    elif not uploaded_file and user_text.strip():
        # Só texto enviado, responder texto (exemplo simples)
        st.write("Você enviou apenas texto:")
        st.write(user_text)
        st.write("Aqui você pode integrar GPT para respostas mais completas.")

    else:
        st.info("Por favor, envie uma mensagem, uma imagem, ou ambos para interagir com a IA.")
