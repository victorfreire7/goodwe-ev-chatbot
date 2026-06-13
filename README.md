# ARIA — Assistente de Recarga Inteligente e Autônoma
### GoodWe EV Challenge 2026 — Sprint 2

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
Trechos são injetados no system prompt junto com a persona
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
├── data/
│   ├── pdfs/          # Manuais oficiais da GoodWe (base do RAG)
│   └── index/         # Índice vetorial gerado automaticamente
├── .env               # Variáveis de ambiente (não versionado)
├── .gitignore
├── app.py             # Servidor Flask + webhook Twilio
├── main.py            # Chatbot principal (terminal)
├── session.py         # Gerenciamento de sessão por número de telefone
├── README.md          # Esta documentação
└── requirements.txt   # Dependências
```

---

## System Prompt

```
Você é a ARIA, assistente virtual oficial da GoodWe Brasil, especializada em gestão,
operação e suporte técnico da linha de carregadores de veículos elétricos (EV Chargers)
e da plataforma SEMS+.

PERSONA DO USUÁRIO ATUAL: {persona}
Adapte seu vocabulário e nível técnico de acordo com essa persona.

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
