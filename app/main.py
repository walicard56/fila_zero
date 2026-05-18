"""FilaZero — Sistema de pedidos para almoço comunitário.

Aplicação principal FastAPI.
"""
import os
from pathlib import Path
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

# Diretórios base do projeto (resolve corretamente em deploys)
BASE_DIR = Path(__file__).resolve().parent.parent
# Prefer root-level `static`/`templates` (useful if project root contains them),
# otherwise fall back to `app/static` and `app/templates`.
STATIC_DIR = (BASE_DIR / "static") if (BASE_DIR / "static").exists() else (Path(__file__).resolve().parent / "static")
TEMPLATES_DIR = (BASE_DIR / "templates") if (BASE_DIR / "templates").exists() else (Path(__file__).resolve().parent / "templates")

# Estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "mensagem": exc.detail},
            status_code=404,
        )
    # Default
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
