"""FilaZero — Sistema de pedidos para almoço comunitário.

Aplicação principal FastAPI.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from .database import Base, engine
from .routers import cliente, cozinha, admin
from . import auth

# Cria tabelas (idempotente — só cria se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FilaZero", description="Sistema de pedidos para almoço comunitário")

# Sessão para login da cozinha/admin
SECRET = os.getenv("SECRET_KEY", "filazero-dev-secret-change-in-prod")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

# Estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(cliente.router)
app.include_router(cozinha.router)
app.include_router(admin.router)
app.include_router(auth.router)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Trata o redirect lançado pelo requer_login."""
    if exc.status_code == 302 and "Location" in (exc.headers or {}):
        return RedirectResponse(url=exc.headers["Location"], status_code=302)
    # Página 404 amigável
    if exc.status_code == 404:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="app/templates")
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "mensagem": exc.detail},
            status_code=404,
        )
    # Default
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
