import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

from src.chatbot import inicializar_rag, gerar_resposta, PERSONAS


def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def selecionar_persona() -> dict:
    """Exibe o menu de personas e retorna a escolhida."""
    print("👋 Olá! Sou a ARIA, assistente virtual da GoodWe Brasil.")
    print("   Para te ajudar melhor, me diga quem é você:\n")

    for numero, persona in PERSONAS.items():
        print(f"  [{numero}] {persona['icone']}  {persona['nome']}")
        print(f"       {persona['descricao']}\n")

    while True:
        escolha = input("Digite o número da sua opção: ").strip()
        if escolha in PERSONAS:
            return PERSONAS[escolha]
        print("⚠️  Opção inválida. Digite 1, 2, 3 ou 4.\n")


def main():
    print("=" * 60)
    print("  ARIA — Assistente de Recarga Inteligente e Autônoma")
    print("  GoodWe EV Chatbot")
    print("=" * 60)
    print()

    colecao = inicializar_rag()
    cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

    persona = selecionar_persona()
    historico = []

    limpar_terminal()

    print("=" * 60)
    print("  ARIA — Assistente de Recarga Inteligente e Autônoma")
    print("  GoodWe EV Chatbot")
    print("=" * 60)
    print()
    print(f"✅ Perfil identificado: {persona['icone']} {persona['nome']}")
    print("\n💡 Exemplos de perguntas para você:\n")
    for exemplo in persona["exemplos"]:
        print(f'   • "{exemplo}"')
    print("\n   Digite 'sair' a qualquer momento para encerrar.")
    print("-" * 60)
    print()

    while True:
        pergunta = input("Você: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("\nARIA: Até logo! Qualquer dúvida sobre sua estação GoodWe, estarei aqui. 👋")
            break

        resposta = gerar_resposta(cliente, historico, colecao, pergunta, persona)

        historico.append({"role": "user", "content": pergunta})
        historico.append({"role": "assistant", "content": resposta})

        print(f"\nARIA: {resposta}\n")
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
