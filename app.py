import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(
    page_title="MOREIRAGPT 2.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Estilos CSS customizados para interface futurista ---
st.markdown(
    """
    <style>
    .main > div { max-width: 900px; margin: auto; }
    .css-1d391kg { background: linear-gradient(135deg, #1f005c, #5b0060); }
    .stButton>button {
        background: linear-gradient(45deg, #ff6a00, #ee0979);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        height: 45px;
        width: 100%;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #ee0979, #ff6a00);
        transform: scale(1.05);
    }
    .css-18e3th9 { padding: 2rem 1rem 2rem 1rem; }
    .streamlit-expanderHeader {
        font-size: 18px;
        font-weight: 700;
        color: #ff6a00;
    }
    .css-1aumxhk { color: #ddd !important; }
    .css-ffhzg2 { color: #aaa !important; }
    .css-10trblm { font-family: 'Roboto Mono', monospace; }
    pre {
        background-color: #222;
        color: #eee;
        padding: 15px;
        border-radius: 10px;
        overflow-x: auto;
        font-size: 14px;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Função para buscar na web via DuckDuckGo ---
def buscar_na_web(pergunta, max_results=4):
    try:
        url = f"https://duckduckgo.com/html/?q={pergunta.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MoreiraBot/1.0)"}
        r = requests.get(url, headers=headers, timeout=8)
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

# --- Prompt do sistema para a IA ---
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

# --- Interpretador de comandos especiais ---
def interpretar_comando(prompt):
    prompt = prompt.strip()
    if prompt.startswith("/web"):
        termo = prompt[4:].strip()
        if termo == "":
            return "Por favor, informe o termo para busca após /web."
        resultados = buscar_na_web(termo, max_results=5)
        return "\n\n".join(resultados)

    if prompt.startswith("/marketing"):
        return (
            "Dicas poderosas para marketing digital:\n"
            "- Conheça profundamente seu público\n"
            "- Utilize gatilhos mentais (escassez, autoridade)\n"
            "- Crie conteúdo que resolva dores reais\n"
            "- Teste anúncios e otimize constantemente\n"
            "- Use redes sociais para criar autoridade\n"
        )

    if prompt.startswith("/vendas"):
        return (
            "Estratégias para vender mais:\n"
            "- Entenda a dor do cliente, ofereça solução clara\n"
            "- Use provas sociais (depoimentos, cases)\n"
            "- Faça ofertas irresistíveis e limitadas\n"
            "- Crie urgência sem pressão exagerada\n"
            "- Follow-up é essencial para fechar vendas\n"
        )

    if prompt.startswith("/hábitos"):
        return (
            "Sugestões para formar hábitos poderosos:\n"
            "- Comece pequeno e aumente gradativamente\n"
            "- Use gatilhos diários para lembrar a ação\n"
            "- Mantenha disciplina com recompensas\n"
            "- Evite tentar mudar tudo de uma vez\n"
            "- Tenha um diário para monitorar progresso\n"
        )

    # Sem comando especial, retorna None para usar GPT normal
    return None

# --- Função que chama a API OpenAI ---
def enviar_mensagem_openai(mensagens, client, retries=3):
    for tentativa in range(retries):
        try:
            resposta = client.chat.completions.create(
                model="gpt-4",
                messages=mensagens,
                temperature=0.8,
                max_tokens=900,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.3,
                timeout=10,
            )
            return resposta.choices[0].message.content.strip()
        except Exception as e:
            if tentativa < retries - 1:
                time.sleep(1)  # espera e tenta novamente
            else:
                return f"Erro ao obter resposta da IA: {str(e)}"

# --- Inicializa a API OpenAI ---
def init_openai():
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.error("⚠️ A chave da API OpenAI não está configurada nos Secrets do Streamlit!")
        st.stop()
    return openai.OpenAI(api_key=api_key)

# --- Interface principal ---
def main():
    st.title("🤖 MOREIRAGPT 2.0 — Sua IA Máquina de Dinheiro")
    st.markdown(
        "Uma assistente inteligente para te ajudar em crescimento pessoal, marketing, vendas, hábitos e buscas na web."
    )

    client = init_openai()

    if "historico" not in st.session_state:
        st.session_state.historico = []

    with st.sidebar.expander("🛠️ Como usar / Comandos especiais"):
        st.markdown(
            """
            - Escreva perguntas ou comandos na caixa abaixo e envie.
            - Comandos especiais (inicie a mensagem com):
              - `/marketing` — dicas de marketing digital
              - `/vendas` — técnicas para vender mais
              - `/hábitos` — dicas para criar hábitos poderosos
              - `/web termo` — busca e resumo na web
            - Use linguagem natural para conversar normalmente.
            - Limpe o histórico com o botão abaixo.
            """
        )
        if st.button("🧹 Limpar histórico"):
            st.session_state.historico = []

    prompt_usuario = st.text_area(
        "Escreva aqui sua pergunta ou comando:",
        height=100,
        placeholder="Ex: /marketing ou Me dê dicas para vender mais"
    )

    if st.button("Enviar") and prompt_usuario.strip():
        st.session_state.historico.append({"user": prompt_usuario})
        resposta_comando = interpretar_comando(prompt_usuario)
        if resposta_comando:
            st.session_state.historico.append({"bot": resposta_comando})
        else:
            mensagens = [
                {"role": "system", "content": gerar_mensagem_sistema()},
            ]
            for msg in st.session_state.historico:
                if "user" in msg:
                    mensagens.append({"role": "user", "content": msg["user"]})
                if "bot" in msg:
                    mensagens.append({"role": "assistant", "content": msg["bot"]})

            resposta_ia = enviar_mensagem_openai(mensagens, client)
            st.session_state.historico.append({"bot": resposta_ia})

    # Exibir histórico
    for i, troca in enumerate(st.session_state.historico):
        if "user" in troca:
            st.markdown(f"<p style='color:#ff6a00; font-weight:600;'>Você:</p> {troca['user']}", unsafe_allow_html=True)
        if "bot" in troca:
            st.markdown(f"<p style='color:#eee; background:#222; border-radius:10px; padding:10px;'>{troca['bot']}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
