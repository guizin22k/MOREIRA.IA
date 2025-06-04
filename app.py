import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from readability import Document
import nltk

# Baixar recursos do nltk (só na primeira execução)
nltk.download('punkt')
nltk.download('stopwords')

# ================= CONFIG =================
st.set_page_config(page_title="🤖 MOREIRAGPT", page_icon="🤖", layout="wide")

# Inicializa cliente OpenAI (use st.secrets para proteger sua API key)
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ================= UI =====================
st.markdown("""
<style>
    /* Fundo escuro moderno com gradiente */
    .main {
        background: linear-gradient(135deg, #1e1e2f, #3a3a5c);
        color: #e0e0f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTextInput>div>div>input {
        background-color: #2a2a44 !important;
        color: #ddd !important;
        border-radius: 8px;
        border: none;
        padding: 12px;
        font-size: 1.1em;
    }
    .css-1v0mbdj {
        background-color: #2a2a44 !important;
        border-radius: 8px;
    }
    h1, h2, h3 {
        font-weight: 800;
        text-shadow: 1px 1px 3px #111122;
    }
    .stMarkdown p {
        font-size: 1.1em;
        line-height: 1.6;
    }
</style>

<h1 style='text-align: center; color: #61dafb; margin-top: 20px;'>🤖 MOREIRAGPT</h1>
<p style='text-align: center; font-size: 1.3em; margin-bottom: 25px;'>Sua IA parceira para crescimento, disciplina e renda online</p>
<hr style="border: 1px solid #333a5c; margin-bottom: 25px;">
""", unsafe_allow_html=True)

# Histórico da conversa na sessão
if "historico" not in st.session_state:
    st.session_state["historico"] = []

# ================= FUNÇÕES ==================

def buscar_na_web(pergunta, max_results=3):
    """
    Pesquisa no DuckDuckGo, extrai os resultados e pega texto limpo das páginas via readability.
    Retorna uma lista com título, snippet e link + texto extraído.
    """
    try:
        url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=7)
        if r.status_code != 200:
            return [f"Erro na busca: status {r.status_code}"]

        soup = BeautifulSoup(r.text, 'html.parser')
        resultados = soup.find_all('a', class_='result__a', limit=max_results)
        respostas = []

        for link in resultados:
            href = link['href']
            titulo = link.get_text()

            # Tenta baixar o conteúdo da página para extrair texto principal
            try:
                page = requests.get(href, headers=headers, timeout=7)
                doc = Document(page.text)
                texto_limpo = doc.summary()
                # Limitar tamanho do texto para exibir
                if len(texto_limpo) > 800:
                    texto_limpo = texto_limpo[:800] + "..."
            except Exception:
                texto_limpo = "Conteúdo da página não disponível."

            respostas.append(f"### [{titulo}]({href})\n\n{texto_limpo}\n---")

        if not respostas:
            return ["Nenhum resultado relevante encontrado."]
        return respostas

    except Exception as e:
        return [f"Erro ao buscar na web: {str(e)}"]

def gerar_mensagem_sistema():
    return (
        "Você é a MOREIRAGPT, uma assistente inteligente e humana. "
        "Ajude o usuário a crescer pessoalmente, superar vícios, melhorar hábitos, "
        "ganhar dinheiro online com estratégias práticas e atuais. "
        "Use linguagem clara, motivadora e adaptada à realidade do usuário. "
        "Responda com foco em resultados reais e práticos.\n\n"
        "Você entende comandos especiais:\n"
        " - /marketing: estratégias para marketing digital e vendas\n"
        " - /vendas: dicas e técnicas de vendas\n"
        " - /hábitos: sugestões para disciplina e rotina\n"
        " - /web [termo]: pesquisa na web e resumo dos melhores resultados\n"
        "Responda sempre de forma objetiva e útil."
    )

def interpretar_comando(prompt):
    prompt = prompt.strip()
    if prompt.startswith("/web"):
        termo = prompt[4:].strip()
        if not termo:
            return "Por favor, informe o termo para busca após /web."
        resultados = buscar_na_web(termo)
        return "\n\n".join(resultados)

    elif prompt.startswith("/marketing"):
        return None  # Deixa o GPT responder

    elif prompt.startswith("/vendas"):
        return None

    elif prompt.startswith("/hábitos"):
        return None

    return None

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

# ============== INTERAÇÃO =================

entrada = st.text_input("Digite sua pergunta ou comando:", placeholder="Ex: /marketing Como crescer no TikTok em 2025?")

if entrada:
    resposta_comando = interpretar_comando(entrada)

    if resposta_comando is not None:
        st.info(resposta_comando)
        st.session_state["historico"].append({"user": entrada, "bot": resposta_comando})
    else:
        mensagens = [{"role": "system", "content": gerar_mensagem_sistema()}]
        for troca in st.session_state["historico"][-5:]:
            mensagens.append({"role": "user", "content": troca["user"]})
            mensagens.append({"role": "assistant", "content": troca["bot"]})
        mensagens.append({"role": "user", "content": entrada})

        with st.spinner("Pensando como Moreira..."):
            resposta_ia = enviar_mensagem_openai(mensagens)

        st.success("Resposta da MOREIRAGPT:")
        st.markdown(resposta_ia)
        st.session_state["historico"].append({"user": entrada, "bot": resposta_ia})

# ============== EXIBIR HISTÓRICO ================

if st.session_state["historico"]:
    st.markdown("---")
    st.markdown("### Histórico da conversa")
    for troca in reversed(st.session_state["historico"][-10:]):
        st.markdown(f"**Você:** {troca['user']}")
        st.markdown(f"🤖 **MOREIRAGPT:** {troca['bot']}")
        st.markdown("---")

# ============== RODAPÉ =================

st.markdown("""
<hr>
<p style='text-align: center; font-size: 0.8em;'>Powered by OpenAI • Feito com ❤️ por Moreira</p>
""", unsafe_allow_html=True)
