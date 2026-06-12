import os
import textwrap
from dotenv import load_dotenv
from pypdf import PdfReader
import chromadb
from groq import Groq

load_dotenv()

# ─── Configurações ────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELO = "llama-3.3-70b-versatile"
PASTA_PDFS = "data/pdfs"
PASTA_INDEX = "data/index"
CHUNK_SIZE = 1000
N_RESULTADOS_RAG = 3

SYSTEM_PROMPT = """Você é o assistente virtual oficial da GoodWe Brasil, especializado em gestão, \
operação e suporte técnico da linha de carregadores de veículos elétricos (EV Chargers) e da plataforma SEMS+.
Sua missão é fornecer respostas precisas, educadas e altamente resolutivas, sempre em português brasileiro.

REGRAS DE COMPORTAMENTO:
1. FOCO NO USUÁRIO: Molde seu vocabulário à persona. Seja didático com moradores e clientes finais; \
seja técnico e direto com instaladores e técnicos.
2. PRECISÃO TÉCNICA: Baseie-se exclusivamente no contexto fornecido abaixo. \
Nunca invente especificações técnicas, códigos de erro ou procedimentos elétricos.
3. CONCISÃO E AÇÃO: Use bullet points ou passos numerados quando aplicável. \
Termine sempre oferecendo um próximo passo lógico.
4. ESCALONAMENTO: Se o contexto não cobrir o problema ou houver risco elétrico severo, \
direcione para o suporte humano da GoodWe.
5. FORA DO ESCOPO: Se a pergunta não tiver relação com GoodWe, carregadores EV ou a plataforma SEMS+, \
informe educadamente que só pode ajudar com esses temas.

CONTEXTO RECUPERADO DOS MANUAIS:
{contexto}"""

# ─── Carregamento e indexação dos PDFs ────────────────────────────────────────

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


def indexar_documentos(colecao, documentos: list[tuple[str, str]]):
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


# ─── RAG + Geração ────────────────────────────────────────────────────────────

def buscar_contexto(colecao, pergunta: str) -> str:
    """Busca os trechos mais relevantes no ChromaDB."""
    resultado = colecao.query(query_texts=[pergunta], n_results=N_RESULTADOS_RAG)
    trechos = resultado["documents"][0]
    return "\n\n---\n\n".join(trechos)


def gerar_resposta(cliente: Groq, historico: list, colecao, pergunta: str) -> str:
    """Busca contexto via RAG e gera resposta com o LLaMA."""
    contexto = buscar_contexto(colecao, pergunta)
    system = SYSTEM_PROMPT.format(contexto=contexto)

    mensagens = [{"role": "system", "content": system}] + historico + [{"role": "user", "content": pergunta}]

    resposta = cliente.chat.completions.create(
        model=MODELO,
        messages=mensagens,
        temperature=0.2,
        max_tokens=1024,
    )

    return resposta.choices[0].message.content


# ─── Loop principal ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  GoodWe EV Chatbot — Assistente de Carregadores Elétricos")
    print("=" * 60)
    print()

    colecao = inicializar_rag()
    cliente = Groq(api_key=GROQ_API_KEY)
    historico = []

    print("💬 Chatbot pronto! Digite 'sair' para encerrar.\n")

    while True:
        pergunta = input("Você: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Encerrando. Até logo!")
            break

        resposta = gerar_resposta(cliente, historico, colecao, pergunta)

        historico.append({"role": "user", "content": pergunta})
        historico.append({"role": "assistant", "content": resposta})

        print(f"\nARIA: {resposta}\n")


if __name__ == "__main__":
    main()
