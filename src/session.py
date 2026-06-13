# Gerencia o estado de cada usuário por número de telefone
# Cada usuário tem: persona escolhida e histórico de conversa

_sessoes: dict = {}


def get_sessao(numero: str) -> dict:
    """Retorna a sessão do usuário. Cria uma nova se não existir."""
    if numero not in _sessoes:
        _sessoes[numero] = {
            "persona": None,
            "historico": [],
        }
    return _sessoes[numero]


def definir_persona(numero: str, persona: dict):
    """Define a persona escolhida pelo usuário."""
    _sessoes[numero]["persona"] = persona


def adicionar_historico(numero: str, role: str, content: str):
    """Adiciona uma mensagem ao histórico do usuário."""
    _sessoes[numero]["historico"].append({"role": role, "content": content})


def resetar_sessao(numero: str):
    """Reseta a sessão do usuário (volta ao menu de personas)."""
    _sessoes[numero] = {
        "persona": None,
        "historico": [],
    }
