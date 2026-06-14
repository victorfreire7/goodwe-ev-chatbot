# ARIA — Assistente de Recarga Inteligente e Autônoma
### GoodWe EV Challenge 2026 — Sprint 2

---

> ## ⚠️ Nota de Desvios em Relação à Sprint 1
>
> Durante o desenvolvimento da Sprint 2, três decisões técnicas divergiram do que foi documentado na Sprint 1. Todas foram tomadas por razões práticas e estão justificadas abaixo.
>
> ### 1. Claude API → LLaMA 3.3 70B (via Groq)
> **Documentado:** `claude-sonnet-4-20250514` (Anthropic)
> **Implementado:** `llama-3.3-70b-versatile` (Groq)
> **Motivo:** A API da Anthropic não possui free tier contínuo — exige créditos pagos. Para viabilizar o desenvolvimento, testes e demonstração do projeto sem custo, migramos para o Groq, que oferece acesso gratuito ao LLaMA 3.3 70B com alta velocidade de inferência e qualidade técnica equivalente para o caso de uso.
>
> ### 2. LangChain removido
> **Documentado:** LangChain como orquestrador de cadeia RAG e roteamento por persona
> **Implementado:** Pipeline RAG implementado diretamente com ChromaDB + Groq SDK
> **Motivo:** Para o escopo do projeto, o LangChain adicionaria complexidade e dependências desnecessárias sem benefício real. O roteamento por persona foi resolvido de forma mais simples e controlada via seleção numérica pelo usuário, e a cadeia RAG foi implementada manualmente em menos de 20 linhas. A decisão segue o princípio de menor complexidade possível.

---

## Integrantes do Grupo

- Davi Ramos - RM: 571744
- Lucas Malchior - RM: 504027
- Gustavo Rocha - RM: 570672
- Victor - RM: 571099
- Timothée Campos Ferraz - RM: 568688
- Gabriel Cavaloti - RM: 571643

---

## Repositório

[https://github.com/victorfreire7/goodwe-ev-chatbot](https://github.com/victorfreire7/goodwe-ev-chatbot)

---

## Modos de Execução

O projeto suporta dois modos de uso: **terminal** (interface local) e **WhatsApp** (via Twilio + Cloudflare Tunnel).

### Modo Terminal

Interface local para testes e desenvolvimento.

**Pré-requisitos:**
- Python 3.10+
- Conta gratuita no [Groq Console](https://console.groq.com) com API key gerada

**Instalação:**
```bash
git clone https://github.com/victorfreire7/goodwe-ev-chatbot
cd goodwe-ev-chatbot

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

**Configuração — arquivo `.env`:**
```
GROQ_API_KEY=sua_chave_aqui
```

**Execução:**
```bash
python main.py
```

Na primeira execução os manuais são indexados automaticamente. Nas seguintes, o índice é carregado do cache.

---

### Modo WhatsApp (Twilio + Cloudflare Tunnel)

Permite interagir com a ARIA diretamente pelo WhatsApp via Twilio Sandbox.

**Pré-requisitos adicionais:**
- Conta gratuita no [Twilio](https://twilio.com) com Sandbox do WhatsApp ativado
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) instalado

> ⚠️ **Por que Cloudflare e não ngrok?**
> O ngrok no plano gratuito exibe uma página de verificação para acessos automatizados, bloqueando as requisições do Twilio. O Cloudflare Tunnel não tem essa restrição e funciona de forma transparente.

**Configuração adicional — adicione ao `.env`:**
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Execução:**

Terminal 1 — sobe o servidor Flask:
```bash
python app.py
```

Terminal 2 — expõe o servidor para a internet:
```bash
cloudflared tunnel --url http://localhost:5000
```

O Cloudflare vai gerar uma URL pública no formato:
```
https://algo-algo-algo.trycloudflare.com
```

**Configuração do Webhook no Twilio:**
1. Acesse [console.twilio.com](https://console.twilio.com)
2. Vá em **Messaging → Try it out → Send a WhatsApp message → Sandbox Settings**
3. No campo **"When a message comes in"** cole:
```
https://sua-url.trycloudflare.com/webhook
```
4. Método: **HTTP POST**
5. Clique em **Save**

**Ativação do Sandbox:**

Cada número de telefone que quiser testar precisa enviar a mensagem de ativação para o número do Twilio Sandbox (`+1 415 523 8886`):
```
join <palavra-chave-do-seu-sandbox>
```

Após a confirmação, basta enviar qualquer mensagem e a ARIA responderá.

---

## O Problema Abordado

A distribuição de carregadores de veículos elétricos (EVs) no Brasil enfrenta desafios críticos de rentabilidade e disponibilidade. A GoodWe possui excelência em hardware, mas o desafio central não é apenas instalar carregadores — é tornar os eletropostos **operacionalmente inteligentes**.

Identificamos os seguintes gaps operacionais e comerciais:

- **ChargeGrid Intelligence (Operação Comercial):** Eletropostos públicos carecem de integração para orquestrar potência, registrar ciclos com rastreabilidade, faturar de forma automatizada e comunicar falhas em tempo real.
- **EV ChargeOps (Condomínios):** Falta de sistemas para rateio justo de energia, controle de acesso por unidade habitacional e transparência no faturamento.
- **Barreiras de Adoção:** Instaladores e revendedores têm dificuldade em dimensionar projetos, enquanto os consumidores finais esbarram em suporte técnico fragmentado e processos de vendas com baixa conversão.

---

## A Proposta

A ARIA é uma camada de inteligência e interface baseada em IA, desenvolvida para resolver a lacuna entre o hardware competitivo da GoodWe e a operação diária dos eletropostos.

O chatbot atua como um assistente multifuncional capaz de:

1. **Auxiliar clientes finais e instaladores:** Recomendando hardware, auxiliando no dimensionamento técnico e simulando economia e payback.
2. **Gerenciar a operação:** Respondendo perguntas de operadores comerciais sobre sessões, consumo e faturamento.
3. **Administrar condomínios:** Ajudando síndicos e moradores com rateio de custos, status de disponibilidade e agendamento de recargas.
4. **Automatizar o suporte técnico:** Atuando como primeiro nível para troubleshooting e configuração na plataforma SEMS+.

---

## Tecnologias Utilizadas

| Tecnologia | Função | Justificativa |
|---|---|---|
| **LLaMA 3.3 70B** (via Groq) | Modelo de linguagem principal | Gratuito, respostas sub-segundo, alta qualidade técnica |
| **ChromaDB** | Banco de dados vetorial (RAG) | Leve, sem servidor, persiste índice localmente |
| **sentence-transformers** | Embeddings multilíngues | Suporte nativo PT/EN sem necessidade de tradução |
| **pypdf** | Extração de texto dos manuais | Leitura dos PDFs oficiais da GoodWe |
| **python-dotenv** | Gestão de variáveis de ambiente | API key nunca exposta no código |
| **Flask** | Servidor web para o webhook | Leve, simples e compatível com Twilio |
| **Twilio** | Integração com WhatsApp | Sandbox gratuito para testes sem aprovação Meta |
| **Cloudflare Tunnel** | Exposição do servidor local | Sem página de verificação, compatível com Twilio |

---

## Arquitetura RAG

O sistema utiliza **Retrieval-Augmented Generation (RAG)** para fundamentar as respostas nos manuais oficiais da GoodWe, eliminando alucinações em informações técnicas.

**Documentos indexados:**
- `GW_SEMS-PLUS_User-Manual-EN.pdf` — Operações do app SEMS+
- `Manual_técnico_do_carregador_HCA_G2.pdf` — Hardware, códigos de erro e troubleshooting

**Fluxo de funcionamento:**
```
Usuário pergunta
      ↓
ChromaDB busca os 3 trechos mais relevantes nos manuais
      ↓
Trechos e dados mockados são injetados no system prompt junto com a persona
      ↓
LLaMA 3.3 70B gera resposta contextualizada em PT-BR
      ↓
ARIA responde ao usuário
```

---

## Personas Suportadas

| # | Persona | Escopo |
|---|---|---|
| 1 | 👤 Operador Comercial | Sessões, consumo, faturamento, tarifação |
| 2 | 🏢 Síndico / Condomínio | Rateio de energia, controle de acesso, moradores |
| 3 | 🏠 Morador | Disponibilidade de vaga, agendamento de recarga |
| 4 | 🔧 Técnico / Instalador | Códigos de erro, firmware, configuração avançada |

---

## Estrutura do Projeto

```
goodwe-ev-chatbot/
├── src/
│   ├── __init__.py
│   ├── chatbot.py     # RAG, personas, dados mockados, geração de resposta
│   ├── session.py     # Gerenciamento de sessão por número de telefone
│   └── webhook.py     # Flask + rotas Twilio
├── data/
│   ├── pdfs/          # Manuais oficiais da GoodWe (base do RAG)
│   └── index/         # Índice vetorial gerado automaticamente
├── .env               # Variáveis de ambiente (não versionado)
├── .gitignore
├── app.py             # Entrypoint WhatsApp
├── main.py            # Entrypoint terminal
├── README.md          # Esta documentação
└── requirements.txt   # Dependências
```

---

## System Prompt

```
Você é a ARIA, assistente virtual oficial da GoodWe Brasil, especializada em gestão,
operação e suporte técnico da linha de carregadores de veículos elétricos (EV Chargers)
e da plataforma SEMS+.
Sua missão é fornecer respostas precisas, educadas e altamente resolutivas, sempre em português brasileiro.

PERSONA DO USUÁRIO ATUAL: {persona}
Adapte seu vocabulário e nível técnico de acordo com essa persona.

DADOS DA ESTAÇÃO/USUÁRIO (MOCK):
{dados_mock}

REGRAS DE COMPORTAMENTO:
1. FOCO NO USUÁRIO: Seja didático com moradores e clientes finais; seja técnico e
   direto com instaladores e técnicos.
2. PRECISÃO TÉCNICA: Baseie-se exclusivamente no contexto fornecido. Nunca invente
   especificações técnicas, códigos de erro ou procedimentos elétricos.
3. CONCISÃO E AÇÃO: Use bullet points ou passos numerados quando aplicável. Termine
   sempre oferecendo um próximo passo lógico.
4. ESCALONAMENTO: Se o contexto não cobrir o problema ou houver risco elétrico severo,
   direcione para o suporte humano da GoodWe.
5. FORA DO ESCOPO: Se a pergunta não tiver relação com GoodWe, carregadores EV ou
   a plataforma SEMS+, informe educadamente que só pode ajudar com esses temas.

CONTEXTO RECUPERADO DOS MANUAIS:
{contexto}
```

---

## Resultados do Golden Set

As 5 perguntas definidas na Sprint 1 foram executadas no modo terminal (`python main.py`), uma por persona correspondente. Abaixo estão as respostas obtidas e a avaliação qualitativa de cada uma, comparadas com a "Resposta Ideal Esperada" documentada na Sprint 1. As perguntas 1, 2 e 3 foram re-executadas após a implementação do mock de dados (`DADOS_MOCK`).

### 1. Operador Comercial — Sessões e consumo

**Pergunta:** "Quantas sessões de carga foram realizadas hoje no meu eletroposto e qual foi o consumo total em kWh?"

**Resposta da ARIA:** Informou, com base nos dados disponíveis, que hoje foram realizadas **12 sessões de carga** e que o consumo total foi de **87,4 kWh**, encerrando com a pergunta "O que você gostaria de saber em seguida?".

**Avaliação:** 🟢 **Adequada**

**Observação:** Métricas exatas conforme o mock de dados, tom adequado à persona e CTA aberto ao final — atende plenamente ao critério de sucesso da Sprint 1 (uso correto dos dados, métricas corretas e call-to-action).

---

### 2. Síndico — Rateio de energia entre moradores

**Pergunta:** "Como faço para dividir o custo da energia entre os moradores em abril?"

**Resposta da ARIA:** Apresentou o consumo de cada apartamento (Apto 42: 45 kWh / R$ 32,49, Apto 87: 38 kWh / R$ 27,44, Apto 15: 52 kWh / R$ 37,55), o custo total (R$ 97,48), o cálculo proporcional de cada unidade e finalizou sugerindo confirmar a divisão com os moradores e manter registro dos dados.

**Avaliação:** 🟢 **Adequada**

**Observação:** Cálculo matemático exato com base nos dados mockados e separação clara por apartamento — os dois critérios mais importantes da Sprint 1 foram atendidos. O único ponto não coberto foi a oferta explícita de gerar um PDF do rateio, mencionada na resposta ideal; o "próximo passo" oferecido foi de natureza organizacional em vez de geração de documento. Gap menor, não compromete a avaliação geral.

---

### 3. Morador — Disponibilidade da vaga 12

**Pergunta:** "O carregador da vaga 12 está disponível agora?"

**Resposta da ARIA:** Confirmou que a vaga 12 está **disponível**, com **7 kW livres**, e detalhou os próximos passos para iniciar o carregamento (conectar o plugue, iniciar pelo app, verificar funcionamento), incluindo precauções de segurança.

**Avaliação:** 🟢 **Adequada**

**Observação:** Resposta direta (sim/disponível + potência) conforme o mock de dados, seguida de orientação prática — atende ao critério de status preciso, resposta enxuta e oferta de próximo passo da Sprint 1.

---

### 4. Técnico / Instalador — Erro E-04

**Pergunta:** "O carregador HCA G2 está mostrando o erro E-04. O que significa e como resolver?"

**Resposta da ARIA:** Identificou o erro como falha de comunicação com a placa de controle e apresentou 5 passos de resolução (verificar conexão, reiniciar, verificar configuração, atualizar firmware, verificar placa de controle), encerrando com escalonamento para suporte técnico.

**Avaliação:** 🟢 **Adequada**

**Observação:** Resposta estruturada em passos numerados, com diagnóstico técnico claro e escalonamento ao final — exatamente o formato previsto no critério de sucesso da Sprint 1. Demonstra que o RAG recuperou contexto relevante dos manuais para um cenário técnico.

---

### 5. Operador Comercial — Configuração de preço por kWh

**Pergunta:** "Como configuro o preço por kWh para cobrar dos clientes?"

**Resposta da ARIA:** Apresentou 5 passos no SEMS+/SolarGo (acessar plataforma, navegar até configuração do carregador, selecionar "Preço por kWh", inserir valor, salvar), finalizando com um próximo passo de verificação.

**Avaliação:** 🟢 **Adequada**

**Observação:** Instrução clara, acessível e com CTA de verificação ao final, conforme o critério de sucesso. O caminho de menu difere ligeiramente do documentado na Sprint 1 (Configurações > Eletroposto > Tarifação), mas a estrutura e objetividade da resposta atendem ao esperado.

---

### Resumo Geral

| # | Persona | Avaliação |
|---|---|---|
| 1 | Operador Comercial (sessões/kWh) | 🟢 Adequada |
| 2 | Síndico (rateio) | 🟢 Adequada |
| 3 | Morador (disponibilidade) | 🟢 Adequada |
| 4 | Técnico (erro E-04) | 🟢 Adequada |
| 5 | Operador Comercial (tarifação) | 🟢 Adequada |
