"""Rotas da cozinha: painel para acompanhar e atualizar pedidos."""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime

from .. import models
from ..database import get_db
from ..auth import requer_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/cozinha", response_class=HTMLResponse)
def painel(request: Request, db: Session = Depends(get_db), _user=Depends(requer_login)):
    """Painel da cozinha com pedidos do dia agrupados por status."""
    hoje = date.today()
    pedidos = db.query(models.Pedido).filter(
        models.Pedido.data == hoje
    ).order_by(models.Pedido.criado_em.asc()).all()

    aguardando = [p for p in pedidos if p.status == models.StatusPedido.AGUARDANDO]
    preparando = [p for p in pedidos if p.status == models.StatusPedido.PREPARANDO]
    pronto     = [p for p in pedidos if p.status == models.StatusPedido.PRONTO]
    entregue   = [p for p in pedidos if p.status == models.StatusPedido.ENTREGUE]

    return templates.TemplateResponse("cozinha.html", {
        "request": request,
        "aguardando": aguardando,
        "preparando": preparando,
        "pronto": pronto,
        "entregue": entregue,
        "total": len(pedidos),
    })


@router.post("/cozinha/avancar/{pedido_id}")
def avancar_status(pedido_id: int, db: Session = Depends(get_db), _user=Depends(requer_login)):
    """Avança o pedido para o próximo status na linha do tempo."""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404)

    transicoes = {
        models.StatusPedido.AGUARDANDO: models.StatusPedido.PREPARANDO,
        models.StatusPedido.PREPARANDO: models.StatusPedido.PRONTO,
        models.StatusPedido.PRONTO: models.StatusPedido.ENTREGUE,
    }
    if pedido.status in transicoes:
        pedido.status = transicoes[pedido.status]
        pedido.atualizado_em = datetime.utcnow()
        db.commit()
    return RedirectResponse(url="/cozinha", status_code=303)


@router.post("/cozinha/cancelar/{pedido_id}")
def cancelar(pedido_id: int, db: Session = Depends(get_db), _user=Depends(requer_login)):
    """Marca o pedido como cancelado."""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido:
        pedido.status = models.StatusPedido.CANCELADO
        pedido.atualizado_em = datetime.utcnow()
        db.commit()
    return RedirectResponse(url="/cozinha", status_code=303)
