"""Rotas do cliente/beneficiário: pedir marmita e acompanhar a senha."""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from .. import models, utils
from ..database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    """Página inicial: formulário de pedido."""
    hoje = date.today()
    total_hoje = db.query(models.Pedido).filter(models.Pedido.data == hoje).count()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "total_hoje": total_hoje,
    })


@router.post("/pedir")
def criar_pedido(
    request: Request,
    nome: str = Form(...),
    telefone: str = Form(""),
    observacao: str = Form(""),
    db: Session = Depends(get_db),
):
    """Cria um pedido novo e redireciona para a ficha."""
    nome = nome.strip()
    if len(nome) < 2:
        raise HTTPException(status_code=400, detail="Nome muito curto.")

    pedido = models.Pedido(
        senha=utils.gerar_senha(db),
        nome=nome[:120],
        telefone=telefone.strip()[:20] or None,
        observacao=observacao.strip()[:280] or None,
        status=models.StatusPedido.AGUARDANDO,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return RedirectResponse(url=f"/ficha/{pedido.senha}", status_code=303)


@router.get("/ficha/{senha}", response_class=HTMLResponse)
def ver_ficha(senha: str, request: Request, db: Session = Depends(get_db)):
    """Mostra a ficha digital com a senha e o status em tempo real."""
    hoje = date.today()
    pedido = db.query(models.Pedido).filter(
        models.Pedido.senha == senha.upper(),
        models.Pedido.data == hoje
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Ficha não encontrada.")

    # posição na fila: quantos AGUARDANDO/PREPARANDO criados antes deste
    posicao = db.query(models.Pedido).filter(
        models.Pedido.data == hoje,
        models.Pedido.criado_em < pedido.criado_em,
        models.Pedido.status.in_([
            models.StatusPedido.AGUARDANDO,
            models.StatusPedido.PREPARANDO,
        ])
    ).count() + (1 if pedido.status in [
        models.StatusPedido.AGUARDANDO,
        models.StatusPedido.PREPARANDO,
    ] else 0)

    return templates.TemplateResponse("ficha.html", {
        "request": request,
        "pedido": pedido,
        "posicao": posicao,
    })


@router.get("/api/status/{senha}")
def status_json(senha: str, db: Session = Depends(get_db)):
    """Endpoint JSON usado pela ficha para atualizar status sem recarregar."""
    hoje = date.today()
    pedido = db.query(models.Pedido).filter(
        models.Pedido.senha == senha.upper(),
        models.Pedido.data == hoje
    ).first()
    if not pedido:
        raise HTTPException(status_code=404)
    return {
        "status": pedido.status.value,
        "label": pedido.status_label(),
    }
