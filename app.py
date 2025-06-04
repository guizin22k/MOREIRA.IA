import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import newspaper
from readability import Document
import nltk
import time

# Baixar recursos do nltk para tokenização
nltk.download('punkt')

# ================= CONFIG =================
st.set_page_config(page_title="MOREIRAGPT", page_icon="🤖", layout="wide")
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ================= UI =====================
st.markdown("""
    <h1 style='text-align: center; color: #2C6EFA;'>🤖 MOREIRAGPT</h1>
    <p style='text-align: center;'>Sua IA parceira para crescimento, disciplina e renda online</p>
    <hr>
""", unsafe_allow_html=True)

# Inicializa sessão para histórico de conversa e lembretes
if "historico" not in st.session_state:
    st.session_state["historico"] = []
if "lembretes" not in st.session_state:
    st.session_state["lembretes"] = []

# =============== FUNÇÕES ================

def buscar_na_web(pergunta, max_results=3):
    """
    Pesquisa no DuckDuckGo e retorna uma lista de snippets (título + resumo + link).
    """
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
    """
    Extrai o texto principal da página, usando newspaper3k ou readability.
    """
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        text = article.text
        if len(text) < 200:
            # fallback para readability
            r = requests.get(url, timeout=5)
            doc = Document(r.text)
            text = doc.summary()
        return text
    except:
        try:
            r = requests.get(url, timeout=5)
            doc = Document(r.text)
            return doc.summary()
        except:
            return ""

def resumir_texto(texto, max_sentencas=5):
    """
    Faz uma sumarização simples pegando as primeiras sentenças do texto.
    """
    sentencas = nltk.tokenize.sent_tokenize(texto)
    resumo = " ".join(sentencas[:max_sentencas])
    if len(resumo) == 0:
        return "Não foi possível resumir o conteúdo."
    return resumo

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
        " - /lembrete [texto]: cria um lembrete simples para aparecer na tela\n"
        "Responda sempre de forma objetiva e útil."
    )

def interpretar_comando(prompt):
    prompt = prompt.strip()
    if prompt.startswith("/web"):
        termo = prompt[4:].strip()
        if termo == "":
            return "Por favor, informe o termo para busca após /web."
        resultados = buscar_na_web(termo)
        textos_resumo = []
        for res in resultados:
            # extrair link da string (ultimo link depois do 🔗 )
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
        return f"Lembrete criado: {lembrete_texto}"

    elif prompt.startswith("/marketing"):
        return None

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

# ============== INTERAÇÃO ================

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

# ============== EXIBIR LEMBRETES ================
if st.session_state["lembretes"]:
    st.markdown("---")
    st.markdown("### Lembretes")
    for idx, lembrete in enumerate(st.session_state["lembretes"], 1):
        st.markdown(f"- {idx}. {lembrete}")

# ============== RODAPÉ =================
st.markdown("""
<hr>
<p style='text-align: center; font-size: 0.8em;'>Powered by OpenAI • Feito com ❤️ por Moreira</p>
""", unsafe_allow_html=True)
