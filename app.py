import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import time

# ============ CONFIG ===============
st.set_page_config(page_title="🤖 MOREIRAGPT 2.0 - Máquina de Dinheiro", page_icon="🚀", layout="wide")

# Carregando API KEY OpenAI (garanta que está no st.secrets)
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============ CSS PERSONALIZADO =============
def local_css():
    st.markdown("""
    <style>
        /* Fundo degradê futurista */
        body, .block-container {
            background: linear-gradient(135deg, #020024 0%, #090979 35%, #00d4ff 100%);
            color: #E0F7FA;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        h1, h2, h3 {
            font-weight: 900;
            text-shadow: 1px 1px 8px #00e5ff;
        }
        .stTextInput>div>div>input {
            border-radius: 12px !important;
            padding: 12px 18px !important;
            border: 2px solid #00e5ff !important;
            background: #02122c !important;
            color: #00ffff !important;
        }
        .stButton>button {
            background: linear-gradient(90deg, #00e5ff 0%, #006aff 100%) !important;
            color: #001f3f !important;
            font-weight: 700 !important;
            border-radius: 14px !important;
            padding: 12px 28px !important;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background: #00bcd4 !important;
            color: white !important;
            cursor: pointer;
        }
        .chat-message {
            border-radius: 15px;
            padding: 16px 24px;
            margin-bottom: 18px;
            box-shadow: 0 0 12px rgba(0, 229, 255, 0.4);
            background: rgba(2, 40, 70, 0.8);
        }
        .user-msg {
            color: #00ffff;
            font-weight: 700;
            text-align: right;
        }
        .bot-msg {
            color: #00e5ff;
            font-weight: 600;
            text-align: left;
            white-space: pre-wrap;
        }
        footer {
            font-size: 0.8rem;
            color: #00838f;
            text-align: center;
            margin-top: 2rem;
            padding: 10px 0;
        }
        /* Scroll suave histórico */
        #historico {
            max-height: 380px;
            overflow-y: auto;
            padding-right: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ============ UI =============
st.markdown("""
    <h1 style='text-align: center;'>🤖 MOREIRAGPT 2.0</h1>
    <h3 style='text-align: center; font-weight: 500; color: #00e5ff;'>Sua IA parceira para crescer, faturar e dominar em 2025</h3>
    <hr style='border: 1px solid #00e5ff; margin-bottom: 1.5rem;'>
""", unsafe_allow_html=True)

# Histórico de conversa
if "historico" not in st.session_state:
    st.session_state["historico"] = []

# ============ FUNÇÕES AVANÇADAS ============

def buscar_na_web(pergunta, max_results=4):
    """Pesquisa no DuckDuckGo com scrape avançado, retorna snippets ricos"""
    try:
        url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MoreiraBot/1.0)"}
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

    # Os outros comandos deixam rolar para o GPT
    return None

def enviar_mensagem_openai(mensagens):
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

# ============ INTERAÇÃO ==============

entrada = st.text_input("Digite sua pergunta ou comando:", placeholder="Ex: /marketing Como faturar com TikTok em 2025?")

if entrada:
    resposta_comando = interpretar_comando(entrada)

    if resposta_comando is not None:
        # Comando /web ou erro simples
        st.info(resposta_comando)
        st.session_state["historico"].append({"user": entrada, "bot": resposta_comando})
    else:
        # Monta o contexto do chat, usa histórico até 5 trocas para contexto
        mensagens = [{"role": "system", "content": gerar_mensagem_sistema()}]
        for troca in st.session_state["historico"][-5:]:
            mensagens.append({"role": "user", "content": troca["user"]})
            mensagens.append({"role": "assistant", "content": troca["bot"]})
        mensagens.append({"role": "user", "content": entrada})

        with st.spinner("Pensando como Moreira 2.0... 🚀"):
            resposta_ia = enviar_mensagem_openai(mensagens)

        st.success("Resposta da MOREIRAGPT 2.0:")
        st.markdown(f"<div class='bot-msg'>{resposta_ia}</div>", unsafe_allow_html=True)
        st.session_state["historico"].append({"user": entrada, "bot": resposta_ia})

# ============ EXIBIR HISTÓRICO ==============

if st.session_state["historico"]:
    st.markdown("---")
    st.markdown("<h3 style='color:#00e5ff'>Histórico da conversa (role para ver mais)</h3>", unsafe_allow_html=True)
    with st.container():
        for troca in reversed(st.session_state["historico"][-15:]):
            st.markdown(f"<div class='chat-message user-msg'>Você: {troca['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-message bot-msg'>{troca['bot']}</div>", unsafe_allow_html=True)

# ============ RODAPÉ ==============
st.markdown("""
<footer>
    Desenvolvido por MOREIRA | Para resultados reais em 2025 🚀
</footer>
""", unsafe_allow_html=True)
