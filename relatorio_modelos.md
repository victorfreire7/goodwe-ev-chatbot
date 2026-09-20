# Relatório de Uso de Modelos — Sprint 3 (Bloco B)

## Modelos testados

| Provider | Modelo | Acesso |
|---|---|---|
| Groq | `openai/gpt-oss-120b` | Free tier |
| Google | `gemini-3.6-flash` | Free tier (Google AI Studio) |

## Parametrização

Para manter a comparação justa, os dois modelos foram testados com os mesmos parâmetros onde aplicável:

| Parâmetro | Groq | Gemini |
|---|---|---|
| `temperature` | 0.2 | 0.2 |
| `max_tokens` / `max_output_tokens` | 1024 | 1024 |
| Específico do provider | — | `thinking_level="low"` |

**Sobre o `thinking_level`:** o Gemini 3.6 Flash usa por padrão o nível de raciocínio interno "high", que consome parte do `max_output_tokens` em processamento invisível antes de gerar a resposta visível. No primeiro teste (sem esse parâmetro), isso causou respostas truncadas e latências de até 84s. Com `thinking_level="low"` a resposta passou a vir completa, mas a latência continuou alta (ver resultados) — ou seja, não foi um problema apenas de configuração, é uma característica do modelo.

## Metodologia

O eval set das Sprints 1/2 (3 perguntas, uma por persona) foi reexecutado nos dois modelos, via o script `compare_models.py`, medindo latência (tempo de resposta ponta a ponta) e tokens consumidos (input/output/total).

## Resultados

| Persona | Pergunta (resumo) | Latência Groq | Latência Gemini | Tokens Groq (total) | Tokens Gemini (total) |
|---|---|---|---|---|---|
| Síndico | Rateio de energia entre moradores | 2.41s | 165.94s | 1.819 | 2.189 |
| Técnico/Instalador | Diagnóstico do erro E-04 | 2.90s | 63.84s | 1.552 | 2.092 |
| Morador | Agendamento de recarga | 1.61s | 12.26s | 1.599 | 1.982 |
| **Média** | | **2.31s** | **80.68s** | **1.657** | **2.088** |

## Análise qualitativa

Ambos os modelos produziram respostas corretas, bem estruturadas (passo a passo, tabelas, valores calculados corretamente a partir dos dados mockados) e alinhadas ao tom esperado por persona. Não houve alucinação de dados técnicos em nenhum dos dois — ambos escalonaram adequadamente o erro E-04 (não documentado na base RAG) para o suporte humano, em vez de inventar uma causa.

Diferenças observadas:
- **Groq** tende a ser mais detalhado e estruturado (mais subtítulos, tabelas, listas numeradas).
- **Gemini** é mais direto/conciso, mas ainda cobre os pontos essenciais.
- Em termos de qualidade de conteúdo, a diferença é pequena — ambos atenderiam ao usuário final.

## Seleção justificada

**Modelo escolhido para produção: Groq (`openai/gpt-oss-120b`)**

A diferença decisiva não foi qualidade de resposta, mas **latência**, e ela tem uma implicação técnica concreta pra esse projeto: o webhook do Twilio (canal WhatsApp) tem um timeout padrão de **15 segundos** para retornar o TwiML de resposta. Das 3 chamadas ao Gemini, **2 de 3 ultrapassaram esse limite** (165.94s e 63.84s) — ou seja, em produção, essas mensagens teriam **falhado silenciosamente no WhatsApp**, com o usuário nunca recebendo resposta. Mesmo a chamada mais rápida do Gemini (12.26s) ficou perigosamente perto do limite.

O Groq, com latência média de 2.31s (máximo observado: 2.90s), fica com folga confortável dentro da janela de 15s, tornando-se a escolha viável para o canal de produção (WhatsApp). O Gemini permanece como opção secundária/comparativa — útil para o teste do Bloco B, mas não indicado para esse caso de uso em tempo real sem mudanças arquiteturais (ex.: resposta assíncrona, o que estaria fora do escopo desta sprint).

## Configuração final do projeto

`src/webhook.py` usa `PROVIDER_PADRAO = "groq"` fixo, refletindo essa decisão. O suporte ao Gemini permanece no código (`src/chatbot.py`) e acessível via `main.py` (modo terminal) para fins de teste e demonstração do comparativo.
