import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from readability import Document
import nltk
import time
import datetime
import threading
import telegram
import os

# Baixar recursos do nltk para tokenização (executar só uma vez)
nltk.download('punkt')

# Configurações iniciais
st.set_page_config(
    page_title="MOREIRAGPT 2.0 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Configura Telegram (coloque seu token no secrets do Streamlit Cloud)
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
else:
    bot = None

# CSS custom para interface futurista
def load_css():
    st.markdown(
        """
        <style>
        /* Fonte moderna */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');

        html, body, #root, .appview-container, .main {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #e0e6f1;
            font-family: 'Orbitron', sans-serif;
        }
        .stTextInput > div > input {
            background: #1e2a38;
            border-radius: 10px;
            color: #a9b8cf;
            font-size: 18px;
            padding: 12px;
            border: none;
        }
        .css-18e3th9 {
            background-color: #122733 !important;
            border-radius: 15px;
            padding: 15px 20px;
        }
        .stButton>button {
            background: linear-gradient(90deg, #00d2ff, #3a47d5);
            color: white;
            font-weight: 700;
            font-size: 16px;
            padding: 12px 25px;
            border-radius: 12px;
            border: none;
            transition: background 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #3a47d5, #00d2ff);
            cursor: pointer;
        }
        .chat-entry {
            border-radius: 12px;
            padding: 12px;
            margin: 10px 0;
            background: #152a45cc;
            box-shadow: 0 0 10px #3a47d5aa;
        }
        .chat-user {
            color: #00ffff;
            font-weight: bold;
            font-size: 18px;
        }
        .chat-bot {
            color: #9cfffe;
            font-size: 16px;
        }
        .sidebar .css-1d391kg {
            background: #122733;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .timer {
            font-size: 48px;
            color: #00d2ff;
            font-weight: 900;
            text-align: center;
            margin: 20px 0;
            font-family: 'Orbitron', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============== FUNÇÕES ===============

def buscar_na_web(pergunta, max_results=3):
    try:
        url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=7)
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

def extrair_texto_url(url):
    try:
        r = requests.get(url, timeout=7)
        doc = Document(r.text)
        return doc.summary()
    except:
        return ""

def resumir_texto(texto, max_sentencas=5):
    sentencas = nltk.tokenize.sent_tokenize(texto)
    resumo = " ".join(sentencas[:max_sentencas])
    if len(resumo) == 0:
        return "Não foi possível resumir o conteúdo."
    return resumo

def gerar_mensagem_sistema():
    return (
        "Você é a MOREIRAGPT, uma assistente inteligente, motivadora e humana. "
        "Ajude o usuário a crescer pessoalmente, superar vícios, melhorar hábitos, "
        "ganhar dinheiro online com estratégias práticas e atuais. "
        "Use linguagem clara, motivadora e adaptada à realidade do usuário. "
        "Responda com foco em resultados reais e práticos.\n\n"
        "Você entende comandos especiais:\n"
        " - /marketing: estratégias para marketing digital e vendas\n"
        " - /vendas: dicas e técnicas de vendas\n"
        " - /hábitos: sugestões para disciplina e rotina\n"
        " - /web [termo]: pesquisa na web e resumo dos melhores resultados\n"
        " - /lembrete [texto]: cria um lembrete simples para aparecer na tela e enviar por Telegram\n"
        " - /meta [texto]: define uma meta diária para o usuário\n"
        " - /relatorio: gera um relatório rápido do progresso com hábitos, lembretes e metas\n"
        "Responda sempre de forma objetiva, humana e útil."
    )

def enviar_mensagem_openai(mensagens):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4",
            messages=mensagens,
            temperature=0.7,
            max_tokens=700,
            timeout=15
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao obter resposta da IA: {str(e)}"

def interpretar_comando(prompt):
    prompt = prompt.strip()
    if prompt.startswith("/web"):
        termo = prompt[4:].strip()
        if termo == "":
            return "Por favor, informe o termo para busca após /web."
        resultados = buscar_na_web(termo)
        textos_resumo = []
        for res in resultados:
            partes = res.split("🔗 ")
            if len(partes) == 2:
                texto, url = partes
                texto_limpo = BeautifulSoup(texto, "html.parser").get_text()
                conteudo = extrair_texto_url(url.strip())
                resumo = resumir_texto(conteudo, max_sentencas=5)
                textos_resumo.append(f"{texto_limpo}\nResumo:\n{resumo}\n🔗 {url.strip()}")
            else:
                textos_resumo.append(res)
        return "\n\n".join(textos_resumo)

    elif prompt.startswith("/lembrete"):
        lembrete_texto = prompt[8:].strip()
        if lembrete_texto == "":
            return "Por favor, informe o texto do lembrete após /lembrete."
        st.session_state["lembretes"].append(lembrete_texto)
        if bot:
            try:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📌 Lembrete: {lembrete_texto}")
            except:
                pass
        return f"Lembrete criado e enviado: {lembrete_texto}"

    elif prompt.startswith("/meta"):
        meta_texto = prompt[5:].strip()
        if meta_texto == "":
            return "Por favor, informe o texto da meta após /meta."
        st.session_state["meta_diaria"] = meta_texto
        return f"Meta diária definida: {meta_texto}"

    elif prompt.startswith("/relatorio"):
        lembretes = st.session_state.get("lembretes", [])
        meta = st.session_state.get("meta_diaria", "Nenhuma meta definida")
        rel = f"📋 Relatório Rápido:\n- Meta diária: {meta}\n- Lembretes ativos: {len(lembretes)}"
        if lembretes:
            rel += "\n- Lembretes:\n"
            for idx, lm in enumerate(lembretes, 1):
                rel += f"  {idx}. {lm}\n"
        else:
            rel += "\n- Nenhum lembrete ativo."
        return rel

    elif prompt.startswith("/marketing"):
        return (
            "Para crescer no marketing digital, foque em conteúdos autênticos e consistentes, "
            "invista em vídeos curtos no TikTok e Reels, utilize gatilhos mentais como escassez e prova social, "
            "e teste anúncios pagos otimizados por segmentação. Posicione-se como especialista no nicho."
        )

    elif prompt.startswith("/vendas"):
        return (
            "Dicas para vendas: crie rapport com o cliente, escute mais do que fale, utilize perguntas abertas, "
            "explique benefícios claros do produto, e finalize sempre com uma chamada para ação urgente e amigável."
        )

    elif prompt.startswith("/hábitos"):
        return (
            "Para disciplina e hábitos: defina pequenas metas diárias, faça uso de timers para foco (pomodoro), "
            "registre seu progresso, elimine distrações e mantenha um ritual matinal forte para energia e motivação."
        )

    return None

# =============== TIMER POMODORO ================

def timer_pomodoro(duracao_minutos=25):
    with st.empty():
        for i in range(duracao_minutos * 60, -1, -1):
            minutos, segundos = divmod(i, 60)
            st.markdown(f"<div class='timer'>{minutos:02d}:{segundos:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)

# =============== INÍCIO DA INTERFACE ===============

load_css()

st.title("🤖 MOREIRAGPT 2.0 — Sua IA futurista e parceira")

with st.sidebar:
    st.header("⚙️ Menu")
    if st.button("🕒 Iniciar Timer Pomodoro 25min"):
        st.write("Timer iniciado! Foco total!")
        timer_pomodoro(25)
    if st.button("📋 Ver Relatório Rápido"):
        meta = st.session_state.get("meta_diaria", "Nenhuma meta definida")
        lembretes = st.session_state.get("lembretes", [])
        st.write(f"**Meta diária:** {meta}")
        if lembretes:
            st.write("**Lembretes ativos:**")
            for lm in lembretes:
                st.write(f"- {lm}")
        else:
            st.write("Nenhum lembrete ativo no momento.")
    if st.button("➕ Limpar Lembretes"):
        st.session_state["lembretes"] = []
        st.success("Lembretes apagados!")

# Entrada do usuário
entrada = st.text_input(
    "Digite sua pergunta ou comando (ex: /marketing, /web inteligência artificial, /lembrete pagar contas):",
    key="input_entrada"
)

if entrada:
    resposta_comando = interpretar_comando(entrada)

    if resposta_comando is not None:
        st.info(resposta_comando)
        st.session_state.setdefault("historico", []).append({"user": entrada, "bot": resposta_comando})
    else:
        mensagens = [{"role": "system", "content": gerar_mensagem_sistema()}]
        for troca in st.session_state.get("historico", [])[-5:]:
            mensagens.append({"role": "user", "content": troca["user"]})
            mensagens.append({"role": "assistant", "content": troca["bot"]})
        mensagens.append({"role": "user", "content": entrada})

        with st.spinner("Pensando como Moreira..."):
            resposta_ia = enviar_mensagem_openai(mensagens)

        st.success("Resposta da MOREIRAGPT:")
        st.markdown(resposta_ia)
        st.session_state.setdefault("historico", []).append({"user": entrada, "bot": resposta_ia})

# Histórico de conversas
if st.session_state.get("historico"):
    st.markdown("---")
    st.markdown("### Histórico da conversa")
    for troca in reversed(st.session_state["historico"][-10:]):
        st.markdown(f"<div class='chat-entry'><span class='chat-user'>Você:</span> {troca['user']}<br>"
                    f"<span class='chat-bot'>🤖 MOREIRAGPT:</span> {troca['bot']}</div>", unsafe_allow_html=True)

# Mostrar lembretes e meta diária no rodapé
st.markdown("---")
st.markdown("### Lembretes Ativos")
if st.session_state.get("lembretes"):
    for idx, lembrete in enumerate(st.session_state["lembretes"], 1):
        st.markdown(f"- {idx}. {lembrete}")
else:
    st.write("Nenhum lembrete ativo.")

st.markdown("---")
meta_diaria = st.session_state.get("meta_diaria", None)
if meta_diaria:
    st.markdown(f"### 🎯 Meta diária definida:\n> {meta_diaria}")

# Rodapé
st.markdown(
    """
    <footer style='text-align:center; margin-top:30px; color:#4bcaff;'>
    Powered by MOREIRAGPT 2.0 — Futurista & Humana 🤖
    </footer>
    """,
    unsafe_allow_html=True,
)

# Inicialização de estado
if "lembretes" not in st.session_state:
    st.session_state["lembretes"] = []

if "meta_diaria" not in st.session_state:
    st.session_state["meta_diaria"] = None

if "historico" not in st.session_state:
    st.session_state["historico"] = []
