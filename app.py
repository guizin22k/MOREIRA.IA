import streamlit as st
import openai
import requests

# ================= CONFIG =================
st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="wide")
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ================ UI =====================
st.markdown("""
    <h1 style='text-align: center; color: #2C6EFA;'>🤖 MOREIRAGPT</h1>
    <p style='text-align: center;'>Sua IA parceira para crescimento, disciplina e renda online</p>
    <hr>
""", unsafe_allow_html=True)

# =============== HELPERS ================
def buscar_na_web(pergunta):
    url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        resultados = soup.find_all('a', class_='result__a')
        links = [a['href'] for a in resultados[:3] if a.has_attr('href')]
        return links
    return []

def gerar_mensagem_sistema():
    return (
        "Você é a MOREIRAGPT, uma IA treinada para ajudar o usuário a evoluir pessoalmente, superar vícios, melhorar hábitos, ganhar dinheiro online com estratégias de vendas, marketing e disciplina.\n"
        "Seja clara, direta e humana. Use uma linguagem prática, atualizada e adaptada à realidade do usuário.\n"
        "Você entende comandos especiais como /marketing, /vendas, /hábitos, /web e responde com foco total no resultado."
    )

def interpretar_comando(prompt):
    if prompt.startswith("/web"):
        busca = prompt.replace("/web", "").strip()
        links = buscar_na_web(busca)
        return f"Resultados encontrados:\n" + "\n".join(links) if links else "Nenhum resultado encontrado."
    return None

# ============= INTERAÇÃO ================
prompt = st.text_input("Digite sua pergunta ou comando:", placeholder="Ex: /marketing Como crescer no TikTok em 2025?")

if prompt:
    resposta_comando = interpretar_comando(prompt)

    if resposta_comando:
        st.info(resposta_comando)
    else:
        with st.spinner("Pensando como Moreira..."):
            resposta = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": gerar_mensagem_sistema()},
                    {"role": "user", "content": prompt}
                ]
            )
            st.success("Resposta da MOREIRAGPT:")
            st.markdown(resposta.choices[0].message.content)

# ============== RODAPÉ =================
st.markdown("""
<hr>
<p style='text-align: center; font-size: 0.8em;'>Powered by OpenAI • Feito com ❤️ por Moreira</p>
""", unsafe_allow_html=True)
