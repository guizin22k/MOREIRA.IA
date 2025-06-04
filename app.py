import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import time

# CONFIGURAÇÕES INICIAIS
st.set_page_config(page_title="MOREIRAGPT 2.0 - Sua IA de Renda e Disciplina", layout="centered")
st.title("🤖 MOREIRAGPT 2.0")
st.caption("IA focada em crescimento pessoal, disciplina e ganhar dinheiro online")

# SIDEBAR
with st.sidebar:
    st.header("Configurações")
    st.markdown("**Comandos especiais:**\n- `/web [termo]` busca na web\n- `/marketing` táticas de marketing\n- `/vendas` técnicas de vendas\n- `/habitos` rotinas de disciplina")
    st.markdown("---")
    st.info("Esta é a versão otimizada para velocidade usando GPT-3.5 Turbo")

# CONFIGURAR API
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# BUSCA WEB SIMPLES
def buscar_na_web(pergunta, max_results=3):
    try:
        url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MoreiraBot/1.0)"}
        r = requests.get(url, headers=headers, timeout=10)
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
    except Exception as e:
        return [f"Erro ao buscar na web: {str(e)}"]

# PROMPT DE SISTEMA
def gerar_mensagem_sistema():
    return (
        "Você é a MOREIRAGPT 2.0, uma assistente ultra avançada, focada em:\n"
        "- Crescimento pessoal e mental\n"
        "- Disciplina e superação de vícios\n"
        "- Estratégias de vendas, marketing digital, e geração de renda real em 2025\n"
        "- Respostas objetivas, práticas e altamente aplicáveis\n"
        "- Linguagem humana, motivadora e atualizada\n"
        "- Entende comandos especiais:\n"
        "    /marketing — dicas e táticas para marketing digital\n"
        "    /vendas — técnicas para vender mais\n"
        "    /habitos — sugestões para formar rotinas e disciplina\n"
        "    /web [termo] — pesquisa na web com resumo\n"
        "Responda SEMPRE de forma clara, convincente e orientada a resultados reais."
    )

# COMANDOS ESPECIAIS
comandos_ia = {
    "/marketing": "Me dê ideias de marketing digital para vender produtos como afiliado.",
    "/vendas": "Quais são as técnicas mais poderosas de vendas em 2025?",
    "/habitos": "Quais hábitos são ideais para quem quer parar de fumar e se disciplinar?"
}

def interpretar_comando(prompt):
    prompt = prompt.strip()
    if prompt.startswith("/web"):
        termo = prompt[4:].strip()
        if termo == "":
            return "Digite algo após /web para pesquisar."
        resultados = buscar_na_web(termo)
        return "\n\n".join(resultados)
    elif prompt in comandos_ia:
        return comandos_ia[prompt]  # envia isso pro modelo
    return None

# FUNÇÃO OPENAI
def enviar_mensagem_openai(mensagens, client, retries=3):
    for tentativa in range(retries):
        try:
            with st.spinner("⏳ Carregando resposta da IA..."):
                resposta = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=mensagens,
                    temperature=0.8,
                    max_tokens=900,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.3,
                    timeout=20,
                )
            return resposta.choices[0].message.content.strip()
        except Exception as e:
            if tentativa < retries - 1:
                time.sleep(1)
            else:
                return f"❌ Erro ao obter resposta da IA: {str(e)}"

# HISTÓRICO
if "historico" not in st.session_state:
    st.session_state.historico = []

# INTERFACE
prompt = st.text_input("Digite sua pergunta ou comando:", placeholder="Ex: /habitos para parar de fumar")
if st.button("Enviar") and prompt:
    comando = interpretar_comando(prompt)
    if comando is not None and prompt.startswith("/") and not prompt.startswith("/web"):
        mensagens = [
            {"role": "system", "content": gerar_mensagem_sistema()},
            {"role": "user", "content": comando}
        ]
    elif comando is not None and prompt.startswith("/web"):
        resposta = comando
        st.session_state.historico.append((prompt, resposta))
        st.success(resposta)
        st.stop()
    else:
        mensagens = [
            {"role": "system", "content": gerar_mensagem_sistema()},
            {"role": "user", "content": prompt}
        ]

    resposta = enviar_mensagem_openai(mensagens, client)
    st.session_state.historico.append((prompt, resposta))

# HISTÓRICO DE CONVERSA
if st.session_state.historico:
    st.markdown("---")
    st.subheader("Histórico de Conversa")
    for pergunta, resposta in reversed(st.session_state.historico[-5:]):
        st.markdown(f"**Você:** {pergunta}")
        st.markdown(f"**MOREIRAGPT:** {resposta}")
