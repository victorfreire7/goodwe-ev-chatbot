from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from src.chatbot import inicializar_rag, gerar_resposta, limpar_historico, PERSONAS
from src.session import get_sessao, definir_persona, resetar_sessao

app = Flask(__name__)
colecao = inicializar_rag()
PROVIDER_PADRAO = "groq"

MENU_PERSONAS = (
    "👋 Olá! Sou a *ARIA*, assistente virtual da GoodWe Brasil.\n"
    "Para te ajudar melhor, me diga quem é você:\n\n"
    "  [1] 👤 Operador Comercial\n"
    "  [2] 🏢 Síndico / Condomínio\n"
    "  [3] 🏠 Morador\n"
    "  [4] 🔧 Técnico / Instalador\n\n"
    "Digite o número da sua opção."
)


def montar_exemplos(persona: dict) -> str:
    exemplos = "\n".join([f'  • "{e}"' for e in persona["exemplos"]])
    return (
        f"✅ Perfil identificado: {persona['icone']} *{persona['nome']}*\n\n"
        f"💡 Exemplos de perguntas para você:\n{exemplos}\n\n"
        f"Digite _sair_ a qualquer momento para trocar de perfil."
    )


@app.after_request
def adicionar_headers(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "ARIA Webhook ativo.", 200

    numero = request.form.get("From")
    mensagem = request.form.get("Body", "").strip()

    sessao = get_sessao(numero)
    resposta = MessagingResponse()
    msg = resposta.message()

    if mensagem.lower() == "sair":
        resetar_sessao(numero)
        limpar_historico(numero)
        msg.body(MENU_PERSONAS)
        return str(resposta)

    if sessao["persona"] is None:
        if mensagem in PERSONAS:
            persona = PERSONAS[mensagem]
            definir_persona(numero, persona)
            msg.body(montar_exemplos(persona))
        else:
            msg.body(MENU_PERSONAS)
        return str(resposta)

    persona = sessao["persona"]

    texto_resposta = gerar_resposta(numero, colecao, mensagem, persona, PROVIDER_PADRAO)

    msg.body(texto_resposta)
    return str(resposta)
