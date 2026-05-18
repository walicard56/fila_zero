"""Modelos de dados do FilaZero."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SAEnum
import enum
from .database import Base


class StatusPedido(str, enum.Enum):
    """Estados possíveis de um pedido."""
    AGUARDANDO = "aguardando"   # ficha emitida, aguardando preparo
    PREPARANDO = "preparando"   # cozinha pegou para preparar
    PRONTO = "pronto"           # marmita pronta para retirada
    ENTREGUE = "entregue"       # cliente retirou
    CANCELADO = "cancelado"     # não compareceu / cancelado


class Pedido(Base):
    """Pedido de marmita feito por um beneficiário."""
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    senha = Column(String(8), unique=True, index=True, nullable=False)
    nome = Column(String(120), nullable=False)
    telefone = Column(String(20), nullable=True)
    observacao = Column(String(280), nullable=True)
    status = Column(SAEnum(StatusPedido), default=StatusPedido.AGUARDANDO, nullable=False, index=True)
    data = Column(Date, default=date.today, index=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def status_label(self) -> str:
        labels = {
            StatusPedido.AGUARDANDO: "Aguardando",
            StatusPedido.PREPARANDO: "Preparando",
            StatusPedido.PRONTO: "Pronto",
            StatusPedido.ENTREGUE: "Entregue",
            StatusPedido.CANCELADO: "Cancelado",
        }
        return labels[self.status]

    def status_cor(self) -> str:
        cores = {
            StatusPedido.AGUARDANDO: "bg-amber-100 text-amber-800 border-amber-300",
            StatusPedido.PREPARANDO: "bg-blue-100 text-blue-800 border-blue-300",
            StatusPedido.PRONTO: "bg-emerald-100 text-emerald-800 border-emerald-300",
            StatusPedido.ENTREGUE: "bg-slate-100 text-slate-700 border-slate-300",
            StatusPedido.CANCELADO: "bg-rose-100 text-rose-800 border-rose-300",
        }
        return cores[self.status]
