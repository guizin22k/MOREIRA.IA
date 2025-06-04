import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import time

# ================= CONFIGURAÇÕES =================
st.set_page_config(
    page_title="MOREIRAGPT 2.0 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa cliente OpenAI com sua chave do secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ================= BIBLIOTECA ===================

def buscar_na_web(pergunta, max_results=5):
    try:
        url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MoreiraBot/2.0)"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            resultados = soup.find_all('div', class_='result__body', limit=max_results)
            lista = []
            for res in resultados:
                a = res.find('a', class_='result__a')
                snippet = res.find('a', class_='result__snippet')
                title = a.get_text() if a else "Sem título"
                href = a['href'] if a and a.has_attr('href') else ""
                resumo = snippet.get_text() if snippet else ""
                lista.append(f"**{title}**\n{resumo}\n🔗 {href}")
            return lista if lista else ["Nenhum resultado relevante encontrado."]
        else:
            return [f"Erro na busca: status {r.status_code}"]
    except Exception as e:
        return [f"Erro ao buscar na web: {str(e)}"]

def gerar_mensagem_sistema():
    return (
        "Você é a MOREIRAGPT 2.0, uma assistente ultra avançada, focada em:\n"
        "- Crescimento pessoal e mental\n"
        "- Disciplina e superação de vícios\n"
        "- Estratégias de vendas, marketing digital, e geração de renda real em 2025\n"
        "- Respostas objetivas, práticas e altamente aplicáveis\n"
        "- Linguagem humana, motivadora e atualizada\n"
        "- Entende comandos especiais:\n"
        "    /marketing — dicas e táticas para marketing digital de alta conversão\n"
        "    /vendas — técnicas e estratégias para vender mais e melhor\n"
        "    /hábitos — sugestões para formar rotinas poderosas e disciplina\n"
        "    /web [termo] — pesquisa na web com resumo dos melhores resultados\n"
        "Responda SEMPRE de forma clara, convincente e orientada a resultados reais."
    )

def interpretar_comando(prompt):
    prompt = prompt.strip()
    if prompt.startswith("/web"):
        termo = prompt[4:].strip()
        if termo == "":
            return "Por favor, informe o termo para busca após /web."
        resultados = buscar_na_web(termo, max_results=5)
        return "\n\n".join(resultados)
    # Outros comandos ficam para GPT processar
    return None

def enviar_mensagem_openai(mensagens, client):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4",
            messages=mensagens,
            temperature=0.8,
            max_tokens=900,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.3,
            timeout=15,
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao obter resposta da IA: {str(e)}"

# ================== INTERFACE =====================

# Fundo estilizado com CSS
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #1f1c2c, #928dab);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-top: 1rem;
        letter-spacing: 0.15rem;
        background: -webkit-linear-gradient(#2C6EFA, #00FFD1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        font-size: 1.3rem;
        margin-bottom: 2rem;
        color: #A1A1A1;
    }
    .chat-box {
        background-color: #2a2a3d;
        border-radius: 15px;
        padding: 20px;
        max-height: 550px;
        overflow-y: auto;
        box-shadow: 0 0 12px #00ffd1;
        font-size: 1.1rem;
    }
    .user-msg {
        color: #00FFD1;
        font-weight: 700;
    }
    .bot-msg {
        color: #FFFFFF;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        font-size: 0.85rem;
        margin-top: 3rem;
        color: #666;
    }
    input[type="text"] {
        border-radius: 12px;
        border: 2px solid #00FFD1;
        padding: 12px 15px;
        font-size: 1.1rem;
        width: 100%;
        background-color: #1f1c2c;
        color: white;
        outline: none;
        transition: border-color 0.3s ease;
    }
    input[type="text"]:focus {
        border-color: #2C6EFA;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'>🤖 MOREIRAGPT 2.0</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sua IA parceira para crescimento, disciplina e renda online</div>", unsafe_allow_html=True)
st.markdown("---")

# Histórico da conversa na sessão
if "historico" not in st.session_state:
    st.session_state["historico"] = []

# Caixa de input lateral para instruções rápidas
with st.sidebar:
    st.header("⚙️ Comandos Rápidos")
    st.markdown("""
    - **/marketing** — estratégias de marketing digital e vendas  
    - **/vendas** — dicas e técnicas de vendas  
    - **/hábitos** — disciplina, rotina e hábitos  
    - **/web [termo]** — pesquisa rápida na web  
    ---
    Dica: Sempre use comandos para respostas especializadas.
    """)

entrada = st.text_input("Digite sua pergunta ou comando:", placeholder="Ex: /marketing Como crescer no TikTok em 2025?")

if entrada:
    resposta_comando = interpretar_comando(entrada)

    if resposta_comando is not None:
        # Exibe resposta do comando especial (/web)
        st.info(resposta_comando)
        st.session_state["historico"].append({"user": entrada, "bot": resposta_comando})
    else:
        # Monta histórico para contexto (últimas 5 trocas)
        mensagens = [{"role": "system", "content": gerar_mensagem_sistema()}]
        for troca in st.session_state["historico"][-5:]:
            mensagens.append({"role": "user", "content": troca["user"]})
            mensagens.append({"role": "assistant", "content": troca["bot"]})
        mensagens.append({"role": "user", "content": entrada})

        with st.spinner("Pensando como Moreira..."):
            resposta_ia = enviar_mensagem_openai(mensagens, client)

        st.success("Resposta da MOREIRAGPT:")
        st.markdown(resposta_ia)

        st.session_state["historico"].append({"user": entrada, "bot": resposta_ia})

# Exibe histórico de conversa com estilo
if st.session_state["historico"]:
    st.markdown("---")
    st.markdown("### Histórico da conversa")
    for troca in reversed(st.session_state["historico"][-10:]):
        st.markdown(f"<p class='user-msg'>Você: {troca['user']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='bot-msg'>🤖 MOREIRAGPT: {troca['bot']}</p>", unsafe_allow_html=True)
        st.markdown("---")

# Rodapé
st.markdown(
    """
    <div class='footer'>Powered by OpenAI • Feito com ❤️ por Moreira</div>
    """,
    unsafe_allow_html=True
)
