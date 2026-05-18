"""Funções auxiliares."""
import random
import string
from sqlalchemy.orm import Session
from datetime import date
from . import models


def gerar_senha(db: Session) -> str:
    """Gera senha única no formato A123 (1 letra + 3 dígitos) para o dia."""
    hoje = date.today()
    for _ in range(50):
        letra = random.choice(string.ascii_uppercase)
        numero = random.randint(100, 999)
        senha = f"{letra}{numero}"
        existe = db.query(models.Pedido).filter(
            models.Pedido.senha == senha,
            models.Pedido.data == hoje
        ).first()
        if not existe:
            return senha
    # Fallback raro: prefixo + nanossegundos
    import time
    return f"X{int(time.time()) % 10000}"
