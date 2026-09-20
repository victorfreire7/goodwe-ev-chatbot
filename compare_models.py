"""Roda o eval set das Sprints 1/2 nos dois modelos (Groq e Gemini) e salva os
resultados em comparativo_raw.md, para alimentar o relatorio_modelos.md (Bloco B).

Uso: python compare_models.py
"""
import time
from dotenv import load_dotenv

load_dotenv()

from src.chatbot import inicializar_rag, gerar_resposta_completa, extrair_texto_resposta, PERSONAS

EVAL_SET = [
    ("2", "Como dividir o custo de energia entre os moradores de abril?"),
    ("4", "O carregador está mostrando o erro E-04. O que significa? Como resolver?"),
    ("3", "Como agendar uma recarga?"),
]

PROVIDERS = ["groq", "gemini"]


def formatar_tokens(msg) -> str:
    uso = getattr(msg, "usage_metadata", None)
    if not uso:
        return "n/d"
    return f"in={uso.get('input_tokens', '?')} out={uso.get('output_tokens', '?')} total={uso.get('total_tokens', '?')}"


def main():
    colecao = inicializar_rag()
    linhas_md = ["# Comparativo bruto — Groq vs Gemini\n"]

    for persona_id, pergunta in EVAL_SET:
        persona = PERSONAS[persona_id]
        linhas_md.append(f"## {persona['nome']} — \"{pergunta}\"\n")

        for provider in PROVIDERS:
            session_id = f"compare_{persona_id}_{provider}"
            inicio = time.perf_counter()
            msg = gerar_resposta_completa(session_id, colecao, pergunta, persona, provider)
            latencia = time.perf_counter() - inicio
            texto = extrair_texto_resposta(msg.content)

            print(f"\n{'='*60}\n{persona['nome']} | {provider} | {latencia:.2f}s\n{'='*60}")
            print(texto)

            linhas_md.append(f"### {provider}")
            linhas_md.append(f"- Latência: {latencia:.2f}s")
            linhas_md.append(f"- Tokens: {formatar_tokens(msg)}")
            linhas_md.append(f"- Resposta:\n\n```\n{texto}\n```\n")

    with open("comparativo_raw.md", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))

    print("\n✅ Resultado bruto salvo em comparativo_raw.md")


if __name__ == "__main__":
    main()
