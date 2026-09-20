import os
import textwrap
from pypdf import PdfReader
import chromadb
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

# Modelos disponíveis para comparação (Sprint 3 — Bloco B).
# Cada provider é resolvido por _criar_llm().
MODELOS = {
    "groq": "openai/gpt-oss-120b",
    "gemini": "gemini-3.6-flash",
}
PASTA_PDFS = "data/pdfs"
PASTA_INDEX = "data/index"
CHUNK_SIZE = 1000
N_RESULTADOS_RAG = 3

PERSONAS = {
    "1": {
        "id": "1",
        "nome": "Operador Comercial",
        "icone": "👤",
        "descricao": "Gestão de eletropostos públicos, sessões e faturamento",
        "exemplos": [
            "Quantas sessões de carga foram realizadas hoje?",
            "Como configuro o preço por kWh para cobrar dos clientes?",
        ],
    },
    "2": {
        "id": "2",
        "nome": "Síndico / Condomínio",
        "icone": "🏢",
        "descricao": "Gestão de carregadores em condomínios e rateio de energia",
        "exemplos": [
            "Como faço para dividir o custo da energia entre os moradores?",
            "Como adiciono um novo morador ao sistema?",
        ],
    },
    "3": {
        "id": "3",
        "nome": "Morador",
        "icone": "🏠",
        "descricao": "Uso do carregador, disponibilidade e agendamento",
        "exemplos": [
            "O carregador da vaga 12 está disponível agora?",
            "Como agendar uma recarga?",
        ],
    },
    "4": {
        "id": "4",
        "nome": "Técnico / Instalador",
        "icone": "🔧",
        "descricao": "Suporte técnico, erros e configuração avançada",
        "exemplos": [
            "O carregador está mostrando o erro E-04. O que significa?",
            "Como atualizo o firmware pelo SEMS+?",
        ],
    },
}

# Dados mockados da API/estação, usados para fundamentar respostas que dependem
# de informações operacionais em tempo real (sessões, consumo, rateio, disponibilidade).
DADOS_MOCK = {
    "1": "Sessões hoje: 12 | Consumo total: 87,4 kWh",
    "2": "Consumo em abril — Apto 42: 45 kWh (R$ 32,49) | Apto 87: 38 kWh (R$ 27,44) | Apto 15: 52 kWh (R$ 37,55)",
    "3": "Vaga 12: disponível, 7 kW livres",
    "4": "Sem dados operacionais aplicáveis a este perfil",
}

SYSTEM_PROMPT = """Você é a ARIA, assistente virtual oficial da GoodWe Brasil, especializada em gestão, \
operação e suporte técnico da linha de carregadores de veículos elétricos (EV Chargers) e da plataforma SEMS+.
Sua missão é fornecer respostas precisas, educadas e altamente resolutivas, sempre em português brasileiro.

PERSONA DO USUÁRIO ATUAL: {persona}
Adapte seu vocabulário e nível técnico de acordo com essa persona.

DADOS DA ESTAÇÃO/USUÁRIO (MOCK):
{dados_mock}

REGRAS DE COMPORTAMENTO:
1. FOCO NO USUÁRIO: Seja didático com moradores e clientes finais; seja técnico e direto com instaladores e técnicos.
2. PRECISÃO TÉCNICA: Baseie-se exclusivamente no contexto fornecido abaixo. \
Nunca invente especificações técnicas, códigos de erro ou procedimentos elétricos.
3. CONCISÃO E AÇÃO: Use bullet points ou passos numerados quando aplicável. \
Termine sempre oferecendo um próximo passo lógico.
4. ESCALONAMENTO: Se o contexto não cobrir o problema ou houver risco elétrico severo, \
direcione para o suporte humano da GoodWe.
5. FORA DO ESCOPO: Se a pergunta não tiver relação com GoodWe, carregadores EV ou a plataforma SEMS+, \
informe educadamente que só pode ajudar com esses temas.
6. ACONSELHAMENTO ESPECIALIZADO: Nunca dê parecer jurídico, financeiro ou de segurança elétrica \
(ex.: validade de contratos, questões fiscais, intervenção em fiação/instalação elétrica de risco). \
Recuse educadamente e oriente explicitamente o usuário a consultar um profissional habilitado \
(advogado, contador ou eletricista certificado, conforme o caso).
7. IDENTIDADE: Refira-se a si mesma sempre como "ARIA, assistente da GoodWe". Nunca revele, confirme \
ou mencione qual modelo de IA, empresa ou provedor de tecnologia está por trás do seu funcionamento.

CONTEXTO RECUPERADO DOS MANUAIS:
{contexto}"""


def carregar_pdfs(pasta: str) -> list[tuple[str, str]]:
    """Lê todos os PDFs da pasta e retorna lista de (nome, texto)."""
    documentos = []
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            leitor = PdfReader(caminho)
            texto = ""
            for pagina in leitor.pages:
                texto += pagina.extract_text() + "\n"
            documentos.append((arquivo, texto))
    return documentos


def indexar_documentos(colecao, documentos: list[tuple[str, str]]) -> int:
    """Fatia os textos em chunks e indexa no ChromaDB."""
    chunks = []
    ids = []
    contador = 0
    for nome, texto in documentos:
        pedacos = textwrap.wrap(texto, width=CHUNK_SIZE)
        for pedaco in pedacos:
            chunks.append(pedaco)
            ids.append(f"{nome}_chunk_{contador}")
            contador += 1
    colecao.add(documents=chunks, ids=ids)
    return contador


def inicializar_rag() -> chromadb.Collection:
    """Inicializa o ChromaDB e indexa os PDFs se ainda não foram indexados."""
    cliente_db = chromadb.PersistentClient(path=PASTA_INDEX)
    colecao = cliente_db.get_or_create_collection(name="goodwe_docs")

    if colecao.count() == 0:
        print("📚 Indexando documentos pela primeira vez, aguarde...")
        documentos = carregar_pdfs(PASTA_PDFS)
        if not documentos:
            print("⚠️  Nenhum PDF encontrado em data/pdfs/")
        else:
            total = indexar_documentos(colecao, documentos)
            print(f"✅ {total} chunks indexados de {len(documentos)} documento(s).\n")
    else:
        print(f"✅ Base de conhecimento carregada ({colecao.count()} chunks).\n")

    return colecao


def buscar_contexto(colecao, pergunta: str) -> str:
    """Busca os trechos mais relevantes no ChromaDB."""
    resultado = colecao.query(query_texts=[pergunta], n_results=N_RESULTADOS_RAG)
    trechos = resultado["documents"][0]
    return "\n\n---\n\n".join(trechos)


# Histórico de conversa por sessão, gerenciado nativamente pelo LangChain
# (substitui a lista `historico` que antes era passada e mutada manualmente).
_historicos: dict[str, InMemoryChatMessageHistory] = {}


def _obter_historico(session_id: str) -> InMemoryChatMessageHistory:
    """Callback do RunnableWithMessageHistory: retorna (ou cria) o histórico da sessão."""
    if session_id not in _historicos:
        _historicos[session_id] = InMemoryChatMessageHistory()
    return _historicos[session_id]


def limpar_historico(session_id: str) -> None:
    """Remove o histórico de uma sessão (ex.: ao trocar de persona/reiniciar conversa).
    Necessário porque a memória agora vive dentro do chatbot.py (por session_id),
    separada do dicionário de sessão em src/session.py."""
    _historicos.pop(session_id, None)


def _criar_llm(provider: str):
    """Instancia o chat model do provider escolhido ("groq" ou "gemini")."""
    if provider == "gemini":
        # thinking_level="low": sem isso, o Gemini 3.6 Flash usa "high" por padrão e gasta
        # a maior parte do max_output_tokens em raciocínio interno (não visível), truncando
        # a resposta final e disparando a latência (chegou a 84s no teste). "low" basta
        # pra esse caso de uso (Q&A com contexto já recuperado via RAG).
        return ChatGoogleGenerativeAI(
            model=MODELOS["gemini"], temperature=0.2, max_output_tokens=1024, thinking_level="low"
        )
    return ChatGroq(model=MODELOS["groq"], temperature=0.2, max_tokens=1024)


_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("historico"),
    ("human", "{pergunta}"),
])


def gerar_resposta_completa(session_id: str, colecao, pergunta: str, persona: dict, provider: str = "groq"):
    """Igual a gerar_resposta, mas retorna a AIMessage completa (com metadados de uso/tokens
    quando o provider os expõe), útil para o comparativo entre modelos do Bloco B."""
    contexto = buscar_contexto(colecao, pergunta)
    dados_mock = DADOS_MOCK.get(persona["id"], "Sem dados disponíveis")

    cadeia = _PROMPT | _criar_llm(provider)
    cadeia_com_memoria = RunnableWithMessageHistory(
        cadeia,
        _obter_historico,
        input_messages_key="pergunta",
        history_messages_key="historico",
    )

    return cadeia_com_memoria.invoke(
        {"pergunta": pergunta, "persona": persona["nome"], "dados_mock": dados_mock, "contexto": contexto},
        config={"configurable": {"session_id": session_id}},
    )


def extrair_texto_resposta(content) -> str:
    """Normaliza o `content` de uma AIMessage para string simples. Alguns providers
    (Gemini 3.x, quando anexa 'thought signatures' às partes da resposta) retornam uma
    lista de blocos em vez de uma string direta — isso precisa ser tratado aqui pra não
    vazar a estrutura interna (ex.: o texto bruto de uma lista Python) pro usuário final."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for bloco in content:
            if isinstance(bloco, dict) and bloco.get("type") == "text":
                partes.append(bloco.get("text", ""))
            elif isinstance(bloco, str):
                partes.append(bloco)
        return "".join(partes)
    return str(content)


def gerar_resposta(session_id: str, colecao, pergunta: str, persona: dict, provider: str = "groq") -> str:
    """Busca contexto via RAG e gera resposta via LangChain, com memória por sessão
    gerenciada pelo framework (RunnableWithMessageHistory) e modelo parametrizável
    ("groq" ou "gemini") para a comparação entre modelos da Sprint 3."""
    resposta = gerar_resposta_completa(session_id, colecao, pergunta, persona, provider)
    return extrair_texto_resposta(resposta.content)
