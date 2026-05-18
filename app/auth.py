"""Autenticação simples por sessão para áreas restritas (cozinha + admin)."""
import os
from fastapi import Request, HTTPException, status, Depends, Form, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# Senhas configuráveis por variável de ambiente. Em produção, troque!
SENHA_COZINHA = os.getenv("SENHA_COZINHA", "cozinha123")
SENHA_ADMIN = os.getenv("SENHA_ADMIN", "admin123")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def requer_login(request: Request):
    """Dependency: bloqueia se não houver sessão ativa."""
    if not request.session.get("logado"):
        # FastAPI dependency não consegue retornar RedirectResponse diretamente —
        # então lançamos uma exceção tratada no middleware/handler.
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="redirect",
            headers={"Location": "/login"},
        )
    return request.session.get("usuario")


@router.get("/login", response_class=HTMLResponse)
def tela_login(request: Request, erro: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "erro": erro})


@router.post("/login")
def fazer_login(request: Request, senha: str = Form(...)):
    if senha == SENHA_COZINHA:
        request.session["logado"] = True
        request.session["usuario"] = "cozinha"
        return RedirectResponse(url="/cozinha", status_code=303)
    if senha == SENHA_ADMIN:
        request.session["logado"] = True
        request.session["usuario"] = "admin"
        return RedirectResponse(url="/admin", status_code=303)
    return RedirectResponse(url="/login?erro=1", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
