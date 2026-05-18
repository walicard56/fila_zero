"""Rotas administrativas: relatório do dia e indicadores."""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from .. import models
from ..database import get_db
from ..auth import requer_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin", response_class=HTMLResponse)
def relatorio(request: Request, db: Session = Depends(get_db), _user=Depends(requer_login)):
    """Relatório do dia + últimos 7 dias para gráfico."""
    hoje = date.today()

    pedidos_hoje = db.query(models.Pedido).filter(models.Pedido.data == hoje).all()
    total = len(pedidos_hoje)
    entregues = sum(1 for p in pedidos_hoje if p.status == models.StatusPedido.ENTREGUE)
    cancelados = sum(1 for p in pedidos_hoje if p.status == models.StatusPedido.CANCELADO)
    pendentes = total - entregues - cancelados

    # tempo médio de preparo (criado → entregue), em minutos
    tempos = []
    for p in pedidos_hoje:
        if p.status == models.StatusPedido.ENTREGUE:
            delta = (p.atualizado_em - p.criado_em).total_seconds() / 60
            tempos.append(delta)
    tempo_medio = round(sum(tempos) / len(tempos), 1) if tempos else 0

    # últimos 7 dias para o gráfico
    inicio = hoje - timedelta(days=6)
    historico = db.query(
        models.Pedido.data,
        func.count(models.Pedido.id)
    ).filter(
        models.Pedido.data >= inicio
    ).group_by(models.Pedido.data).all()

    historico_map = {d: c for d, c in historico}
    labels = []
    valores = []
    for i in range(7):
        d = inicio + timedelta(days=i)
        labels.append(d.strftime("%d/%m"))
        valores.append(historico_map.get(d, 0))

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "total": total,
        "entregues": entregues,
        "cancelados": cancelados,
        "pendentes": pendentes,
        "tempo_medio": tempo_medio,
        "labels": labels,
        "valores": valores,
        "pedidos": sorted(pedidos_hoje, key=lambda p: p.criado_em, reverse=True),
    })
